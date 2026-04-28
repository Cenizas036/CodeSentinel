"""
AST Analyzer — Deep structural code analysis using Python AST and pattern matching.
Supports: Python, JavaScript, TypeScript, Java, C, C++, Go, Rust, Ruby, PHP, C#, Swift, Kotlin
"""

import ast
import re
import logging
from typing import Optional

logger = logging.getLogger("CodeSentinel.AST")


class ASTAnalyzer:
    """Analyzes code structure using Abstract Syntax Trees and pattern matching."""

    DANGEROUS_FUNCTIONS = {
        "python": {
            "eval": "Arbitrary code execution via eval()",
            "exec": "Arbitrary code execution via exec()",
            "compile": "Dynamic code compilation",
            "__import__": "Dynamic import can be exploited",
            "pickle.loads": "Deserialization vulnerability",
            "yaml.load": "YAML deserialization (use safe_load)",
            "subprocess.call": "Shell command injection risk (use subprocess.run with shell=False)",
            "os.system": "Shell command injection risk",
            "os.popen": "Shell command injection risk",
        },
        "javascript": {
            "eval": "Arbitrary code execution",
            "Function": "Dynamic function creation",
            "innerHTML": "XSS vulnerability — use textContent or sanitize input",
            "document.write": "XSS vulnerability — avoid document.write",
            "setTimeout": "Implicit eval if string is passed to setTimeout",
            "dangerouslySetInnerHTML": "React XSS risk — sanitize before use",
        },
        "typescript": {
            "eval": "Arbitrary code execution",
            "innerHTML": "XSS vulnerability — use textContent or sanitize input",
            "document.write": "XSS vulnerability",
            "dangerouslySetInnerHTML": "React XSS risk — sanitize before use",
            "as any": "Type safety bypass — avoid using 'as any'",
        },
        "java": {
            "Runtime.getRuntime().exec": "Command injection risk",
            "ProcessBuilder": "Command injection risk — validate inputs",
            "ObjectInputStream": "Deserialization vulnerability",
            "Statement.execute": "SQL injection risk — use PreparedStatement",
            "createStatement": "SQL injection risk — use PreparedStatement",
        },
        "c": {
            "gets": "Buffer overflow — use fgets() instead",
            "sprintf": "Buffer overflow — use snprintf() instead",
            "strcpy": "Buffer overflow — use strncpy() instead",
            "strcat": "Buffer overflow — use strncat() instead",
            "scanf": "Buffer overflow risk — limit input length",
            "system": "Command injection — avoid system(), use exec family",
            "malloc": "Memory leak risk — ensure corresponding free()",
        },
        "cpp": {
            "gets": "Buffer overflow — use fgets() instead",
            "sprintf": "Buffer overflow — use snprintf() instead",
            "strcpy": "Buffer overflow — use strncpy() or std::string",
            "strcat": "Buffer overflow — use strncat() or std::string",
            "system": "Command injection — avoid system()",
            "reinterpret_cast": "Unsafe cast — may cause undefined behavior",
            "const_cast": "Removing const qualifier — potential undefined behavior",
            "new": "Manual memory management — prefer smart pointers",
        },
        "go": {
            "exec.Command": "Command injection risk — validate inputs",
            "os.Exec": "Command injection risk",
            "fmt.Sprintf": "Format string vulnerability if user-controlled",
            "http.ListenAndServe": "No TLS — use ListenAndServeTLS for production",
        },
        "rust": {
            "unsafe": "Unsafe block — bypasses Rust's safety guarantees",
            "unwrap": "Panics on None/Err — use match or unwrap_or",
            "expect": "Panics on None/Err — handle errors gracefully",
            "std::mem::transmute": "Extremely unsafe type reinterpretation",
        },
        "ruby": {
            "eval": "Arbitrary code execution",
            "send": "Dynamic method invocation — validate input",
            "system": "Command injection risk",
            "exec": "Command injection risk",
            "open": "Command injection if input starts with |",
        },
        "php": {
            "eval": "Arbitrary code execution",
            "exec": "Command injection risk",
            "shell_exec": "Command injection risk",
            "system": "Command injection risk",
            "passthru": "Command injection risk",
            "mysql_query": "SQL injection — use PDO prepared statements",
            "extract": "Variable injection vulnerability",
            "unserialize": "Deserialization vulnerability",
            "$_GET": "Unsanitized user input — validate and sanitize",
            "$_POST": "Unsanitized user input — validate and sanitize",
        },
        "csharp": {
            "Process.Start": "Command injection risk — validate inputs",
            "SqlCommand": "SQL injection risk — use parameterized queries",
            "Eval": "Dynamic code execution risk",
            "BinaryFormatter": "Deserialization vulnerability — use JSON serialization",
        },
        "swift": {
            "NSTask": "Command injection risk",
            "Process": "Command execution — validate arguments",
            "UnsafePointer": "Unsafe memory access",
            "UnsafeMutablePointer": "Unsafe mutable memory access",
        },
        "kotlin": {
            "Runtime.getRuntime().exec": "Command injection risk",
            "ProcessBuilder": "Command injection risk",
            "createStatement": "SQL injection risk — use PreparedStatement",
        },
        "html": {
            "http://": "Insecure HTTP usage — upgrade to HTTPS",
            "eval(": "Inline script execution — move JS to separate files and avoid eval()",
            "document.write": "XSS risk and performance issue — use modern DOM APIs",
        },
        "css": {
            "@import": "CSS @import blocks parallel downloads — use <link> tags instead",
            "expression(": "CSS expressions are deprecated and a potential XSS vector",
        },
    }

    # Language-specific secret variable patterns
    SECRET_PATTERNS = ["password", "secret", "api_key", "apikey", "token", "private_key",
                       "auth_token", "access_key", "client_secret", "db_password", "credentials"]

    COMPLEXITY_THRESHOLDS = {
        "function_length": 50,
        "class_methods": 20,
        "nesting_depth": 4,
        "parameter_count": 7,
        "return_statements": 5,
    }

    # Patterns for detecting hardcoded secrets across languages
    HARDCODED_SECRET_REGEX = [
        (r'''(?:password|passwd|pwd)\s*[:=]\s*["'][^"']{3,}["']''', "Hardcoded password detected — use environment variables"),
        (r'''(?:api_?key|apikey|api_?secret)\s*[:=]\s*["'][^"']{3,}["']''', "Hardcoded API key — use environment variables"),
        (r'''(?:secret|token|auth)\s*[:=]\s*["'][^"']{3,}["']''', "Hardcoded secret/token — use environment variables"),
        (r'''(?:private_?key)\s*[:=]\s*["'][^"']{3,}["']''', "Hardcoded private key — use secure key management"),
        (r'''(?:BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY)''', "Private key embedded in source code"),
    ]

    # TODO/FIXME detection
    TODO_PATTERN = re.compile(r'\b(TODO|FIXME|HACK|XXX|BUG)\b', re.IGNORECASE)

    def analyze(self, code: str, language: str) -> list:
        """Perform analysis on source code."""
        issues = []

        if language == "python":
            issues.extend(self._analyze_python(code))
        else:
            issues.extend(self._analyze_generic(code, language))

        # Cross-language checks
        issues.extend(self._check_hardcoded_secrets(code, language))
        issues.extend(self._check_todos(code))
        issues.extend(self._check_long_lines(code))
        issues.extend(self._check_empty_catches(code, language))

        return issues

    # ── Python deep analysis ──────────────────────────────────────

    def _analyze_python(self, code: str) -> list:
        """Deep Python AST analysis."""
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [{"type": "syntax_error", "severity": "critical", "line": e.lineno or 0,
                      "message": f"Syntax error: {e.msg}", "category": "ast"}]

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name in self.DANGEROUS_FUNCTIONS.get("python", {}):
                    issues.append({
                        "type": "dangerous_call", "severity": "high", "line": node.lineno,
                        "message": f"Dangerous function `{func_name}`: {self.DANGEROUS_FUNCTIONS['python'][func_name]}",
                        "category": "security",
                    })

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                issues.extend(self._analyze_function(node))

            if isinstance(node, ast.ClassDef):
                issues.extend(self._analyze_class(node))

            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append({
                    "type": "bare_except", "severity": "medium", "line": node.lineno,
                    "message": "Bare `except:` catches all exceptions including SystemExit and KeyboardInterrupt",
                    "category": "quality",
                })

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults + node.args.kw_defaults:
                    if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append({
                            "type": "mutable_default", "severity": "medium", "line": node.lineno,
                            "message": f"Mutable default argument in `{node.name}()` — use None and assign inside function",
                            "category": "quality",
                        })

            if isinstance(node, ast.Global):
                issues.append({
                    "type": "global_usage", "severity": "low", "line": node.lineno,
                    "message": f"Global variable usage: {', '.join(node.names)} — consider passing as parameter",
                    "category": "quality",
                })

            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name_lower = target.id.lower()
                        if any(p in name_lower for p in self.SECRET_PATTERNS):
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                issues.append({
                                    "type": "hardcoded_secret", "severity": "critical", "line": node.lineno,
                                    "message": f"Potential hardcoded secret in variable `{target.id}` — use environment variables",
                                    "category": "security",
                                })

        return issues

    def _analyze_function(self, node: ast.FunctionDef) -> list:
        issues = []
        body_lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 0

        if body_lines > self.COMPLEXITY_THRESHOLDS["function_length"]:
            issues.append({
                "type": "long_function", "severity": "medium", "line": node.lineno,
                "message": f"Function `{node.name}` is {body_lines} lines — consider refactoring (threshold: {self.COMPLEXITY_THRESHOLDS['function_length']})",
                "category": "quality",
            })

        param_count = len(node.args.args) + len(node.args.kwonlyargs)
        if param_count > self.COMPLEXITY_THRESHOLDS["parameter_count"]:
            issues.append({
                "type": "too_many_params", "severity": "low", "line": node.lineno,
                "message": f"Function `{node.name}` has {param_count} parameters — consider using a dataclass/config object",
                "category": "quality",
            })

        max_depth = self._calculate_nesting_depth(node)
        if max_depth > self.COMPLEXITY_THRESHOLDS["nesting_depth"]:
            issues.append({
                "type": "deep_nesting", "severity": "medium", "line": node.lineno,
                "message": f"Function `{node.name}` has nesting depth {max_depth} — consider early returns or extraction",
                "category": "quality",
            })

        complexity = self._cyclomatic_complexity(node)
        if complexity > 10:
            severity = "high" if complexity > 20 else "medium"
            issues.append({
                "type": "high_complexity", "severity": severity, "line": node.lineno,
                "message": f"Function `{node.name}` has cyclomatic complexity {complexity} — consider splitting",
                "category": "quality",
            })

        return issues

    def _analyze_class(self, node: ast.ClassDef) -> list:
        issues = []
        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

        if len(methods) > self.COMPLEXITY_THRESHOLDS["class_methods"]:
            issues.append({
                "type": "god_class", "severity": "medium", "line": node.lineno,
                "message": f"Class `{node.name}` has {len(methods)} methods — consider splitting into smaller classes",
                "category": "architecture",
            })

        method_names = [m.name for m in methods]
        if methods and "__init__" not in method_names:
            issues.append({
                "type": "missing_init", "severity": "info", "line": node.lineno,
                "message": f"Class `{node.name}` has no __init__ method",
                "category": "quality",
            })

        return issues

    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        max_depth = current_depth
        nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.ExceptHandler)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, nesting_nodes):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
            else:
                child_depth = self._calculate_nesting_depth(child, current_depth)
            max_depth = max(max_depth, child_depth)
        return max_depth

    def _cyclomatic_complexity(self, node: ast.AST) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    @staticmethod
    def _get_call_name(node: ast.Call) -> str:
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""

    # ── Generic multi-language analysis ───────────────────────────

    def _analyze_generic(self, code: str, language: str) -> list:
        """Pattern-based analysis for non-Python languages."""
        issues = []
        lines = code.split("\n")
        lang_key = language.lower()

        # Map aliases
        lang_map = {"c++": "cpp", "c#": "csharp", "cs": "csharp", "ts": "typescript", "js": "javascript", "rb": "ruby"}
        lang_key = lang_map.get(lang_key, lang_key)

        dangerous = self.DANGEROUS_FUNCTIONS.get(lang_key, {})
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip comment lines
            if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("/*"):
                continue

            for pattern, description in dangerous.items():
                if re.search(rf'{re.escape(pattern)}', line):
                    issues.append({
                        "type": "dangerous_pattern", "severity": "high", "line": line_num,
                        "message": f"Dangerous pattern `{pattern}`: {description}",
                        "category": "security",
                    })

        # Language-specific structural checks
        issues.extend(self._check_language_patterns(code, lines, lang_key))

        return issues

    def _check_language_patterns(self, code: str, lines: list, lang: str) -> list:
        """Language-specific structural pattern checks."""
        issues = []

        # JavaScript/TypeScript checks
        if lang in ("javascript", "typescript"):
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if s.startswith("//") or s.startswith("/*"):
                    continue
                if re.search(r'\bvar\b', s):
                    issues.append({"type": "var_usage", "severity": "low", "line": i,
                                   "message": "`var` is function-scoped — use `let` or `const` instead", "category": "quality"})
                if re.search(r'[^=!<>]==[^=]', s) and '===' not in s:
                    issues.append({"type": "loose_equality", "severity": "medium", "line": i,
                                   "message": "Loose equality `==` — use strict equality `===` to avoid type coercion bugs", "category": "quality"})
                if re.search(r'console\.(log|warn|error|debug)', s):
                    issues.append({"type": "console_log", "severity": "info", "line": i,
                                   "message": "Console statement found — remove before production", "category": "quality"})
                if 'alert(' in s:
                    issues.append({"type": "alert_usage", "severity": "low", "line": i,
                                   "message": "`alert()` blocks UI thread — use a notification library", "category": "quality"})

        # Java checks
        if lang == "java":
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if s.startswith("//"):
                    continue
                if 'System.out.println' in s:
                    issues.append({"type": "sysout", "severity": "info", "line": i,
                                   "message": "`System.out.println` — use a logging framework (SLF4J/Log4j)", "category": "quality"})
                if 'catch (Exception ' in s or 'catch(Exception ' in s:
                    issues.append({"type": "broad_catch", "severity": "medium", "line": i,
                                   "message": "Catching generic `Exception` — catch specific exception types", "category": "quality"})
                if re.search(r'String\s+\w+\s*=\s*""\s*;', s):
                    if '+=' in lines[min(i, len(lines)-1)] if i < len(lines) else False:
                        issues.append({"type": "string_concat", "severity": "low", "line": i,
                                       "message": "String concatenation in loop — use StringBuilder", "category": "quality"})

        # C/C++ checks
        if lang in ("c", "cpp"):
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if s.startswith("//"):
                    continue
                if re.search(r'printf\s*\(\s*[a-zA-Z_]', s) and '%' not in s:
                    issues.append({"type": "format_string", "severity": "high", "line": i,
                                   "message": "Format string vulnerability — never pass user input directly to printf", "category": "security"})
                if 'goto ' in s:
                    issues.append({"type": "goto_usage", "severity": "low", "line": i,
                                   "message": "`goto` usage — makes control flow harder to follow", "category": "quality"})

        # Go checks
        if lang == "go":
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if s.startswith("//"):
                    continue
                if re.search(r'fmt\.Print(ln|f)?\(', s):
                    issues.append({"type": "fmt_print", "severity": "info", "line": i,
                                   "message": "`fmt.Print` — use structured logging (log/slog) in production", "category": "quality"})
                if 'panic(' in s:
                    issues.append({"type": "panic_usage", "severity": "medium", "line": i,
                                   "message": "`panic()` should be avoided — return errors instead", "category": "quality"})

        # Rust checks
        if lang == "rust":
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if s.startswith("//"):
                    continue
                if '.clone()' in s:
                    issues.append({"type": "unnecessary_clone", "severity": "info", "line": i,
                                   "message": "`.clone()` — verify if cloning is necessary (performance cost)", "category": "quality"})

        # PHP checks
        if lang == "php":
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if s.startswith("//") or s.startswith("#"):
                    continue
                if re.search(r'md5\s*\(', s):
                    issues.append({"type": "weak_hash", "severity": "high", "line": i,
                                   "message": "MD5 is cryptographically weak — use password_hash() or bcrypt", "category": "security"})
                if re.search(r'mysql_', s):
                    issues.append({"type": "deprecated_mysql", "severity": "high", "line": i,
                                   "message": "mysql_* functions are deprecated — use PDO or MySQLi", "category": "security"})

        # Ruby checks
        if lang == "ruby":
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if s.startswith("#"):
                    continue
                if 'puts ' in s or s == 'puts':
                    issues.append({"type": "puts_debug", "severity": "info", "line": i,
                                   "message": "`puts` — use a logger for production code", "category": "quality"})

        # HTML checks
        if lang == "html":
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if re.search(r'<(center|font|marquee|blink|frameset|frame)\b', s, re.IGNORECASE):
                    issues.append({"type": "deprecated_html", "severity": "medium", "line": i,
                                   "message": "Deprecated HTML tag — use CSS instead", "category": "quality"})
                if re.search(r'\bon(click|load|mouseover|submit)\s*=', s, re.IGNORECASE):
                    issues.append({"type": "inline_event", "severity": "low", "line": i,
                                   "message": "Inline event handler — use addEventListener in a JS file", "category": "quality"})
                if '<iframe' in s and 'sandbox' not in s:
                    issues.append({"type": "unsafe_iframe", "severity": "medium", "line": i,
                                   "message": "iframe without sandbox attribute — security risk", "category": "security"})

        # CSS checks
        if lang == "css":
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if '!important' in s:
                    issues.append({"type": "css_important", "severity": "low", "line": i,
                                   "message": "Overuse of !important can make CSS hard to maintain", "category": "quality"})
                if re.search(r'^\s*\*\s*\{', line):
                    issues.append({"type": "universal_selector", "severity": "info", "line": i,
                                   "message": "Universal selector (*) can cause performance issues if overused", "category": "performance"})

        return issues

    # ── Cross-language checks ─────────────────────────────────────

    def _check_hardcoded_secrets(self, code: str, language: str) -> list:
        issues = []
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            if language == "python":
                continue  # Handled by AST
            for pattern, message in self.HARDCODED_SECRET_REGEX:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "type": "hardcoded_secret", "severity": "critical", "line": i,
                        "message": message, "category": "security",
                    })
                    break
        return issues

    def _check_todos(self, code: str) -> list:
        issues = []
        for i, line in enumerate(code.split("\n"), 1):
            match = self.TODO_PATTERN.search(line)
            if match:
                issues.append({
                    "type": "todo_found", "severity": "info", "line": i,
                    "message": f"`{match.group()}` comment found — track in issue tracker",
                    "category": "quality",
                })
        return issues

    def _check_long_lines(self, code: str) -> list:
        issues = []
        for i, line in enumerate(code.split("\n"), 1):
            if len(line) > 120:
                issues.append({
                    "type": "long_line", "severity": "info", "line": i,
                    "message": f"Line is {len(line)} characters — consider keeping lines under 120 characters",
                    "category": "quality",
                })
        return issues

    def _check_empty_catches(self, code: str, language: str) -> list:
        issues = []
        lines = code.split("\n")
        lang_key = language.lower()

        catch_patterns = {
            "javascript": r'catch\s*\(', "typescript": r'catch\s*\(',
            "java": r'catch\s*\(', "csharp": r'catch\s*\(', "kotlin": r'catch\s*\(',
            "swift": r'catch\s*\{', "cpp": r'catch\s*\(',
            "php": r'catch\s*\(', "ruby": r'rescue',
        }
        pattern = catch_patterns.get(lang_key)
        if not pattern:
            return issues

        for i, line in enumerate(lines, 1):
            if re.search(pattern, line.strip()):
                # Check if next non-empty line is just a closing brace or empty
                for j in range(i, min(i + 3, len(lines))):
                    next_line = lines[j].strip()
                    if next_line in ("}", "end", "pass", ""):
                        issues.append({
                            "type": "empty_catch", "severity": "medium", "line": i,
                            "message": "Empty catch/rescue block — silently swallowing errors hides bugs",
                            "category": "quality",
                        })
                        break
                    elif next_line and next_line != "{":
                        break

        return issues
