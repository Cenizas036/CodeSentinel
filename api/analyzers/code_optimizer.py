"""
Code Optimizer — Rule-based code optimization engine.
Applies best-practice transformations for multiple languages.
"""

import ast
import re
import copy
import logging

logger = logging.getLogger("CodeSentinel.Optimizer")


class CodeOptimizer:
    """Applies automated code optimizations and returns optimized code + explanations."""

    def optimize(self, code: str, language: str) -> dict:
        lang = language.lower()
        lang_map = {"c++": "cpp", "c#": "csharp", "cs": "csharp",
                    "ts": "typescript", "js": "javascript", "rb": "ruby"}
        lang = lang_map.get(lang, lang)

        optimizations = []
        optimized_code = code

        if lang == "python":
            optimized_code, optimizations = self._optimize_python(code)
        else:
            optimized_code, optimizations = self._optimize_generic(code, lang)

        # Cross-language optimizations
        optimized_code, cross_opts = self._cross_language_optimize(optimized_code, lang)
        optimizations.extend(cross_opts)

        return {
            "original_code": code,
            "optimized_code": optimized_code,
            "optimizations": optimizations,
            "total_optimizations": len(optimizations),
            "changed": optimized_code.strip() != code.strip(),
        }

    # ── Python Optimizations ──────────────────────────────────────

    def _optimize_python(self, code: str) -> tuple:
        optimizations = []
        lines = code.split("\n")
        new_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            indent = line[:len(line) - len(line.lstrip())]
            modified = False

            # Replace eval() with ast.literal_eval()
            if re.search(r'\beval\s*\(', stripped) and 'literal_eval' not in stripped:
                new_line = line.replace('eval(', 'ast.literal_eval(')
                new_lines.append(new_line)
                optimizations.append({
                    "line": i + 1, "type": "security",
                    "original": stripped,
                    "optimized": new_line.strip(),
                    "reason": "Replaced `eval()` with `ast.literal_eval()` — prevents arbitrary code execution while still parsing literals"
                })
                modified = True

            # Replace os.system with subprocess.run
            if 'os.system(' in stripped and not modified:
                match = re.search(r'os\.system\((.+)\)', stripped)
                if match:
                    arg = match.group(1)
                    new_stripped = f"subprocess.run({arg}, shell=True, check=True)"
                    new_line = indent + new_stripped
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "security",
                        "original": stripped,
                        "optimized": new_stripped,
                        "reason": "Replaced `os.system()` with `subprocess.run()` — better error handling and security"
                    })
                    modified = True

            # Replace bare except with except Exception
            if stripped == 'except:' and not modified:
                new_line = indent + 'except Exception as e:'
                new_lines.append(new_line)
                optimizations.append({
                    "line": i + 1, "type": "quality",
                    "original": "except:",
                    "optimized": "except Exception as e:",
                    "reason": "Bare `except:` catches SystemExit and KeyboardInterrupt — use `except Exception as e:` instead"
                })
                modified = True

            # Replace pickle.loads with json.loads where possible
            if 'pickle.loads(' in stripped and not modified:
                new_line = line.replace('pickle.loads(', 'json.loads(')
                new_lines.append(new_line)
                optimizations.append({
                    "line": i + 1, "type": "security",
                    "original": stripped,
                    "optimized": new_line.strip(),
                    "reason": "Replaced `pickle.loads()` with `json.loads()` — pickle deserialization is a code execution vulnerability"
                })
                modified = True

            # Replace string concatenation with f-strings
            if re.search(r'"[^"]*"\s*\+\s*\w+|\'[^\']*\'\s*\+\s*\w+', stripped) and 'print' not in stripped and not modified:
                # Simple case: "text " + var
                match = re.search(r'["\']([^"\']*)["\'](\s*)\+(\s*)(\w+)', stripped)
                if match:
                    text, _, _, var_name = match.groups()
                    new_expr = f'f"{text}{{{var_name}}}"'
                    new_stripped = stripped[:stripped.find(match.group())] + new_expr + stripped[stripped.find(match.group()) + len(match.group()):]
                    new_line = indent + new_stripped
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "performance",
                        "original": stripped,
                        "optimized": new_stripped,
                        "reason": "Replaced string concatenation with f-string — more readable and slightly faster"
                    })
                    modified = True

            # Add pass -> proper logging in empty except
            if stripped == 'pass' and i > 0 and 'except' in lines[i - 1] and not modified:
                new_line = indent + 'logging.exception("An error occurred")'
                new_lines.append(new_line)
                optimizations.append({
                    "line": i + 1, "type": "quality",
                    "original": "pass",
                    "optimized": 'logging.exception("An error occurred")',
                    "reason": "Empty except blocks silently swallow errors — log the exception instead"
                })
                modified = True

            if not modified:
                new_lines.append(line)

        return "\n".join(new_lines), optimizations

    # ── Generic Language Optimizations ────────────────────────────

    def _optimize_generic(self, code: str, lang: str) -> tuple:
        optimizations = []
        lines = code.split("\n")
        new_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            indent = line[:len(line) - len(line.lstrip())]
            modified = False

            if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("/*"):
                new_lines.append(line)
                continue

            # JavaScript/TypeScript optimizations
            if lang in ("javascript", "typescript"):
                # var -> let/const
                if re.match(r'^var\s+', stripped):
                    new_line = line.replace('var ', 'const ', 1)
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "quality",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "`var` is function-scoped and hoisted — `const` (or `let`) is block-scoped and safer"
                    })
                    modified = True

                # == to ===
                if not modified and re.search(r'[^=!<>]==[^=]', stripped):
                    new_line = line.replace(' == ', ' === ')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "quality",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "Loose equality `==` performs type coercion — use strict equality `===`"
                    })
                    modified = True

                # eval -> safer alternative
                if not modified and re.search(r'\beval\s*\(', stripped):
                    new_line = line.replace('eval(', 'JSON.parse(')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "security",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "Replaced `eval()` with `JSON.parse()` — prevents arbitrary code execution"
                    })
                    modified = True

                # innerHTML -> textContent
                if not modified and '.innerHTML' in stripped and '=' in stripped:
                    new_line = line.replace('.innerHTML', '.textContent')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "security",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "Replaced `innerHTML` with `textContent` — prevents XSS attacks"
                    })
                    modified = True

                # console.log -> remove/comment
                if not modified and re.search(r'console\.(log|warn|debug)\(', stripped):
                    new_line = indent + '// ' + stripped + '  // TODO: Remove debug statement'
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "quality",
                        "original": stripped,
                        "optimized": '// ' + stripped,
                        "reason": "Console statements should be removed in production — commented out"
                    })
                    modified = True

                # alert -> commented
                if not modified and 'alert(' in stripped:
                    new_line = indent + '// ' + stripped + '  // TODO: Replace with notification'
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "quality",
                        "original": stripped,
                        "optimized": '// ' + stripped,
                        "reason": "`alert()` blocks UI — use a notification library instead"
                    })
                    modified = True

            # C/C++ optimizations
            if lang in ("c", "cpp"):
                if not modified and 'gets(' in stripped:
                    new_line = line.replace('gets(', 'fgets(')
                    if ')' in new_line and 'stdin' not in new_line:
                        new_line = new_line.rstrip().rstrip(';').rstrip(')') + ', sizeof(buffer), stdin);'
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "security",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "`gets()` has no bounds checking — replaced with `fgets()` to prevent buffer overflow"
                    })
                    modified = True

                if not modified and 'strcpy(' in stripped:
                    new_line = line.replace('strcpy(', 'strncpy(')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "security",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "`strcpy()` has no bounds checking — replaced with `strncpy()` to prevent buffer overflow"
                    })
                    modified = True

                if not modified and re.search(r'\bsprintf\(', stripped):
                    new_line = line.replace('sprintf(', 'snprintf(')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "security",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "`sprintf()` can overflow — replaced with `snprintf()` for bounded writing"
                    })
                    modified = True

                if not modified and 'system(' in stripped:
                    new_line = indent + '// SECURITY: ' + stripped + '  // Replace with execvp() or popen()'
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "security",
                        "original": stripped,
                        "optimized": '// ' + stripped,
                        "reason": "`system()` is vulnerable to command injection — use `execvp()` family instead"
                    })
                    modified = True

            # Java optimizations
            if lang == "java":
                if not modified and 'System.out.println' in stripped:
                    new_line = line.replace('System.out.println', 'logger.info')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "quality",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "Replaced `System.out.println` with `logger.info` — use structured logging in production"
                    })
                    modified = True

                if not modified and 'createStatement()' in stripped:
                    new_line = line.replace('createStatement()', 'prepareStatement(sql)')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "security",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "`Statement` is vulnerable to SQL injection — use `PreparedStatement` with parameterized queries"
                    })
                    modified = True

            # Go optimizations
            if lang == "go":
                if not modified and 'fmt.Println(' in stripped:
                    new_line = line.replace('fmt.Println(', 'log.Println(')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "quality",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "Replaced `fmt.Println` with `log.Println` — use structured logging in production"
                    })
                    modified = True

                if not modified and 'panic(' in stripped:
                    new_line = line.replace('panic(', 'return fmt.Errorf(')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "quality",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "`panic()` crashes the program — return an error instead for graceful handling"
                    })
                    modified = True

            # Rust optimizations
            if lang == "rust":
                if not modified and '.unwrap()' in stripped:
                    new_line = line.replace('.unwrap()', '.unwrap_or_default()')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "quality",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "`.unwrap()` panics on None/Err — `.unwrap_or_default()` provides a safe fallback"
                    })
                    modified = True

            # PHP optimizations
            if lang == "php":
                if not modified and re.search(r'mysql_query\(', stripped):
                    new_line = indent + '// DEPRECATED: ' + stripped + '  // Use PDO::query() instead'
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "security",
                        "original": stripped,
                        "optimized": '// ' + stripped,
                        "reason": "`mysql_query` is deprecated and insecure — migrate to PDO with prepared statements"
                    })
                    modified = True

                if not modified and re.search(r'\bmd5\s*\(', stripped):
                    new_line = line.replace('md5(', 'password_hash(')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "security",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "MD5 is cryptographically broken — use `password_hash()` with bcrypt"
                    })
                    modified = True

            # Ruby optimizations
            if lang == "ruby":
                if not modified and stripped.startswith('puts '):
                    new_line = line.replace('puts ', 'Rails.logger.info ')
                    new_lines.append(new_line)
                    optimizations.append({
                        "line": i + 1, "type": "quality",
                        "original": stripped,
                        "optimized": new_line.strip(),
                        "reason": "`puts` is for debugging — use a proper logger in production"
                    })
                    modified = True

            if not modified:
                new_lines.append(line)

        return "\n".join(new_lines), optimizations

    # ── Cross-Language Optimizations ──────────────────────────────

    def _cross_language_optimize(self, code: str, lang: str) -> tuple:
        optimizations = []
        lines = code.split("\n")
        new_lines = []

        secret_pattern = re.compile(
            r'''((?:password|passwd|pwd|secret|api_?key|token|auth|private_?key|credentials)\s*[:=]\s*)["\']([^"\']{3,})["\']''',
            re.IGNORECASE
        )

        env_func = {
            "python": 'os.environ.get("SECRET_KEY")',
            "javascript": 'process.env.SECRET_KEY',
            "typescript": 'process.env.SECRET_KEY',
            "java": 'System.getenv("SECRET_KEY")',
            "go": 'os.Getenv("SECRET_KEY")',
            "rust": 'std::env::var("SECRET_KEY").unwrap_or_default()',
            "ruby": 'ENV["SECRET_KEY"]',
            "php": '$_ENV["SECRET_KEY"]',
            "csharp": 'Environment.GetEnvironmentVariable("SECRET_KEY")',
            "swift": 'ProcessInfo.processInfo.environment["SECRET_KEY"]',
            "kotlin": 'System.getenv("SECRET_KEY")',
        }

        for i, line in enumerate(lines):
            match = secret_pattern.search(line)
            if match:
                env_replacement = env_func.get(lang, 'os.environ["SECRET_KEY"]')
                indent = line[:len(line) - len(line.lstrip())]
                prefix = match.group(1)
                new_line = indent + prefix + env_replacement
                new_lines.append(new_line)
                optimizations.append({
                    "line": i + 1, "type": "security",
                    "original": line.strip(),
                    "optimized": new_line.strip(),
                    "reason": "Hardcoded secret detected — replaced with environment variable lookup"
                })
            else:
                new_lines.append(line)

        return "\n".join(new_lines), optimizations
