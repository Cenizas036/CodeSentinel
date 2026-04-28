"""
AST Analyzer — Deep structural code analysis using Python AST and pattern matching.
"""

import ast
import re
import logging
from typing import Optional

logger = logging.getLogger("CodeSentinel.AST")


class ASTAnalyzer:
    """Analyzes code structure using Abstract Syntax Trees."""

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
            "innerHTML": "XSS vulnerability",
            "document.write": "XSS vulnerability",
            "setTimeout.*string": "Implicit eval via setTimeout",
        },
    }

    COMPLEXITY_THRESHOLDS = {
        "function_length": 50,
        "class_methods": 20,
        "nesting_depth": 4,
        "parameter_count": 7,
        "return_statements": 5,
    }

    def analyze(self, code: str, language: str) -> list:
        """Perform AST-based analysis on source code."""
        issues = []

        if language == "python":
            issues.extend(self._analyze_python(code))
        else:
            issues.extend(self._analyze_generic(code, language))

        return issues

    def _analyze_python(self, code: str) -> list:
        """Deep Python AST analysis."""
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [{"type": "syntax_error", "severity": "critical", "line": e.lineno or 0,
                      "message": f"Syntax error: {e.msg}", "category": "ast"}]

        # Walk the AST
        for node in ast.walk(tree):
            # Check dangerous function calls
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name in self.DANGEROUS_FUNCTIONS.get("python", {}):
                    issues.append({
                        "type": "dangerous_call",
                        "severity": "high",
                        "line": node.lineno,
                        "message": f"Dangerous function `{func_name}`: {self.DANGEROUS_FUNCTIONS['python'][func_name]}",
                        "category": "security",
                    })

            # Check function complexity
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_issues = self._analyze_function(node)
                issues.extend(func_issues)

            # Check class complexity
            if isinstance(node, ast.ClassDef):
                class_issues = self._analyze_class(node)
                issues.extend(class_issues)

            # Check bare except
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append({
                    "type": "bare_except",
                    "severity": "medium",
                    "line": node.lineno,
                    "message": "Bare `except:` catches all exceptions including SystemExit and KeyboardInterrupt",
                    "category": "quality",
                })

            # Check mutable default arguments
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults + node.args.kw_defaults:
                    if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append({
                            "type": "mutable_default",
                            "severity": "medium",
                            "line": node.lineno,
                            "message": f"Mutable default argument in `{node.name}()` — use None and assign inside function",
                            "category": "quality",
                        })

            # Check global variable usage
            if isinstance(node, ast.Global):
                issues.append({
                    "type": "global_usage",
                    "severity": "low",
                    "line": node.lineno,
                    "message": f"Global variable usage: {', '.join(node.names)} — consider passing as parameter",
                    "category": "quality",
                })

            # Check for hardcoded secrets
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name_lower = target.id.lower()
                        secret_patterns = ["password", "secret", "api_key", "token", "private_key"]
                        if any(p in name_lower for p in secret_patterns):
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                issues.append({
                                    "type": "hardcoded_secret",
                                    "severity": "critical",
                                    "line": node.lineno,
                                    "message": f"Potential hardcoded secret in variable `{target.id}` — use environment variables",
                                    "category": "security",
                                })

        return issues

    def _analyze_function(self, node: ast.FunctionDef) -> list:
        """Analyze individual function for complexity issues."""
        issues = []
        body_lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 0

        # Function too long
        if body_lines > self.COMPLEXITY_THRESHOLDS["function_length"]:
            issues.append({
                "type": "long_function",
                "severity": "medium",
                "line": node.lineno,
                "message": f"Function `{node.name}` is {body_lines} lines — consider refactoring (threshold: {self.COMPLEXITY_THRESHOLDS['function_length']})",
                "category": "quality",
            })

        # Too many parameters
        param_count = len(node.args.args) + len(node.args.kwonlyargs)
        if param_count > self.COMPLEXITY_THRESHOLDS["parameter_count"]:
            issues.append({
                "type": "too_many_params",
                "severity": "low",
                "line": node.lineno,
                "message": f"Function `{node.name}` has {param_count} parameters — consider using a dataclass/config object",
                "category": "quality",
            })

        # Deep nesting
        max_depth = self._calculate_nesting_depth(node)
        if max_depth > self.COMPLEXITY_THRESHOLDS["nesting_depth"]:
            issues.append({
                "type": "deep_nesting",
                "severity": "medium",
                "line": node.lineno,
                "message": f"Function `{node.name}` has nesting depth {max_depth} — consider early returns or extraction",
                "category": "quality",
            })

        # Cyclomatic complexity
        complexity = self._cyclomatic_complexity(node)
        if complexity > 10:
            severity = "high" if complexity > 20 else "medium"
            issues.append({
                "type": "high_complexity",
                "severity": severity,
                "line": node.lineno,
                "message": f"Function `{node.name}` has cyclomatic complexity {complexity} — consider splitting",
                "category": "quality",
            })

        return issues

    def _analyze_class(self, node: ast.ClassDef) -> list:
        """Analyze class for structural issues."""
        issues = []
        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

        if len(methods) > self.COMPLEXITY_THRESHOLDS["class_methods"]:
            issues.append({
                "type": "god_class",
                "severity": "medium",
                "line": node.lineno,
                "message": f"Class `{node.name}` has {len(methods)} methods — consider splitting into smaller classes",
                "category": "architecture",
            })

        # Check for missing __init__
        method_names = [m.name for m in methods]
        if methods and "__init__" not in method_names:
            issues.append({
                "type": "missing_init",
                "severity": "info",
                "line": node.lineno,
                "message": f"Class `{node.name}` has no __init__ method",
                "category": "quality",
            })

        return issues

    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = current_depth
        nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.ExceptHandler)

        for child in ast.iter_child_nodes(node):
            if isinstance(child, nesting_nodes):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        decision_nodes = (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert)

        for child in ast.walk(node):
            if isinstance(child, decision_nodes):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    @staticmethod
    def _get_call_name(node: ast.Call) -> str:
        """Extract function name from a Call node."""
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

    def _analyze_generic(self, code: str, language: str) -> list:
        """Generic pattern-based analysis for non-Python languages."""
        issues = []
        lines = code.split("\n")

        dangerous = self.DANGEROUS_FUNCTIONS.get(language, {})
        for line_num, line in enumerate(lines, 1):
            for pattern, description in dangerous.items():
                if re.search(rf'\b{re.escape(pattern)}\b', line):
                    issues.append({
                        "type": "dangerous_pattern",
                        "severity": "high",
                        "line": line_num,
                        "message": f"Dangerous pattern `{pattern}`: {description}",
                        "category": "security",
                    })

        return issues
