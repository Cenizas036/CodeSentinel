"""
Quality Scorer — Calculates code quality metrics for multiple languages.
"""

import ast
import re
import math
import logging

logger = logging.getLogger("CodeSentinel.Quality")

# Comment patterns per language
COMMENT_PATTERNS = {
    "python": {"line": ["#"], "block_start": '"""', "block_end": '"""'},
    "javascript": {"line": ["//"], "block_start": "/*", "block_end": "*/"},
    "typescript": {"line": ["//"], "block_start": "/*", "block_end": "*/"},
    "java": {"line": ["//"], "block_start": "/*", "block_end": "*/"},
    "c": {"line": ["//"], "block_start": "/*", "block_end": "*/"},
    "cpp": {"line": ["//"], "block_start": "/*", "block_end": "*/"},
    "csharp": {"line": ["//"], "block_start": "/*", "block_end": "*/"},
    "go": {"line": ["//"], "block_start": "/*", "block_end": "*/"},
    "rust": {"line": ["//"], "block_start": "/*", "block_end": "*/"},
    "ruby": {"line": ["#"], "block_start": "=begin", "block_end": "=end"},
    "php": {"line": ["//", "#"], "block_start": "/*", "block_end": "*/"},
    "swift": {"line": ["//"], "block_start": "/*", "block_end": "*/"},
    "kotlin": {"line": ["//"], "block_start": "/*", "block_end": "*/"},
    "html": {"line": ["<!--"], "block_start": "<!--", "block_end": "-->"},
    "css": {"line": ["/*"], "block_start": "/*", "block_end": "*/"},
}

# Function/method definition patterns per language
FUNC_PATTERNS = {
    "javascript": r'(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>|\w+\s*=>))',
    "typescript": r'(?:function\s+\w+|(?:const|let|var)\s+\w+\s*(?::\s*\w+)?\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))',
    "java": r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{',
    "c": r'(?:\w+\s+)+\w+\s*\([^)]*\)\s*\{',
    "cpp": r'(?:\w+\s+)+\w+\s*\([^)]*\)\s*(?:const)?\s*\{',
    "go": r'func\s+(?:\([^)]+\)\s+)?\w+\s*\(',
    "rust": r'fn\s+\w+',
    "ruby": r'def\s+\w+',
    "php": r'(?:public|private|protected|static|\s)*function\s+\w+',
    "csharp": r'(?:public|private|protected|internal|static|\s)+[\w<>\[\]]+\s+\w+\s*\([^)]*\)',
    "swift": r'func\s+\w+',
    "kotlin": r'fun\s+\w+',
}

CLASS_PATTERNS = {
    "javascript": r'class\s+\w+',
    "typescript": r'(?:export\s+)?(?:abstract\s+)?class\s+\w+',
    "java": r'(?:public|private|protected|abstract|static|\s)*class\s+\w+',
    "cpp": r'class\s+\w+',
    "csharp": r'(?:public|private|protected|internal|abstract|static|\s)*class\s+\w+',
    "ruby": r'class\s+\w+',
    "php": r'(?:abstract\s+)?class\s+\w+',
    "swift": r'class\s+\w+',
    "kotlin": r'(?:open\s+|abstract\s+|data\s+)?class\s+\w+',
    "rust": r'(?:pub\s+)?struct\s+\w+',
    "go": r'type\s+\w+\s+struct',
}


class QualityScorer:
    """Calculates comprehensive code quality metrics."""

    def score(self, code: str, language: str) -> dict:
        lang = language.lower()
        lang_map = {"c++": "cpp", "c#": "csharp", "cs": "csharp", "ts": "typescript", "js": "javascript", "rb": "ruby"}
        lang = lang_map.get(lang, lang)

        metrics = {
            "lines_of_code": self._count_loc(code, lang),
            "comment_ratio": self._comment_ratio(code, lang),
            "duplication_score": self._detect_duplication(code),
            "naming_quality": self._check_naming(code, lang),
        }

        if lang == "python":
            metrics.update(self._python_metrics(code))
        else:
            metrics.update(self._generic_metrics(code, lang))

        metrics["overall_score"] = self._calculate_overall(metrics)
        metrics["grade"] = self._grade(metrics["overall_score"])
        return metrics

    def _count_loc(self, code: str, lang: str) -> dict:
        lines = code.split("\n")
        total = len(lines)
        blank = sum(1 for l in lines if not l.strip())
        comment_prefixes = COMMENT_PATTERNS.get(lang, {"line": ["#", "//"]}).get("line", ["#", "//"])
        comments = sum(1 for l in lines if any(l.strip().startswith(p) for p in comment_prefixes))
        return {"total": total, "blank": blank, "comments": comments, "code": total - blank - comments}

    def _comment_ratio(self, code: str, lang: str) -> float:
        loc = self._count_loc(code, lang)
        if loc["code"] == 0:
            return 0.0
        return round(loc["comments"] / loc["code"], 3)

    def _detect_duplication(self, code: str) -> dict:
        lines = [l.strip() for l in code.split("\n") if l.strip() and not l.strip().startswith(("#", "//", "/*", "*"))]
        total = len(lines)
        if total == 0:
            return {"duplicate_lines": 0, "duplication_percentage": 0.0}

        seen = {}
        for line in lines:
            if len(line) > 10:
                seen[line] = seen.get(line, 0) + 1

        duplicates = sum(count - 1 for count in seen.values() if count > 1)
        return {"duplicate_lines": duplicates, "duplication_percentage": round(duplicates / total * 100, 1)}

    def _check_naming(self, code: str, lang: str) -> dict:
        issues = 0
        total_names = 0

        if lang == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_names += 1
                        if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and node.name != "__init__":
                            issues += 1
                    elif isinstance(node, ast.ClassDef):
                        total_names += 1
                        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                            issues += 1
            except SyntaxError:
                pass
        else:
            # Generic naming check via regex
            func_pat = FUNC_PATTERNS.get(lang)
            if func_pat:
                for match in re.finditer(func_pat, code):
                    total_names += 1

        conformance = 1.0 - (issues / max(total_names, 1))
        return {"naming_conformance": round(conformance, 3), "naming_issues": issues}

    def _python_metrics(self, code: str) -> dict:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"function_count": 0, "class_count": 0, "avg_cyclomatic_complexity": 0,
                    "maintainability_index": 0, "operator_count": 0, "operand_count": 0}

        functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        avg_complexity = 0
        if functions:
            complexities = [self._cyclomatic(f) for f in functions]
            avg_complexity = sum(complexities) / len(complexities)

        operators = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare)))
        operands = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.Name, ast.Constant)))

        loc = self._count_loc(code, "python")["code"]
        if loc > 0 and avg_complexity > 0:
            mi = max(0, (171 - 5.2 * math.log(max(operators + operands, 1))
                         - 0.23 * avg_complexity
                         - 16.2 * math.log(max(loc, 1))) * 100 / 171)
        else:
            mi = 100.0

        return {
            "function_count": len(functions), "class_count": len(classes),
            "avg_cyclomatic_complexity": round(avg_complexity, 2),
            "maintainability_index": round(mi, 1),
            "operator_count": operators, "operand_count": operands,
        }

    def _generic_metrics(self, code: str, lang: str) -> dict:
        """Compute metrics for non-Python languages using regex patterns."""
        func_pat = FUNC_PATTERNS.get(lang)
        class_pat = CLASS_PATTERNS.get(lang)

        func_count = len(re.findall(func_pat, code)) if func_pat else 0
        class_count = len(re.findall(class_pat, code)) if class_pat else 0

        # Estimate cyclomatic complexity from branching keywords
        branch_keywords = r'\b(if|else\s+if|elif|elsif|elseif|switch|case|for|while|do|foreach|catch|rescue|match)\b'
        branches = len(re.findall(branch_keywords, code))
        avg_complexity = round(branches / max(func_count, 1), 2)

        # Approximate maintainability
        loc = self._count_loc(code, lang)["code"]
        if loc > 0 and avg_complexity > 0:
            mi = max(0, (171 - 5.2 * math.log(max(loc, 1))
                         - 0.23 * avg_complexity * func_count
                         - 16.2 * math.log(max(loc, 1))) * 100 / 171)
        else:
            mi = 85.0

        return {
            "function_count": func_count, "class_count": class_count,
            "avg_cyclomatic_complexity": avg_complexity,
            "maintainability_index": round(min(mi, 100), 1),
            "operator_count": 0, "operand_count": 0,
        }

    def _cyclomatic(self, node: ast.AST) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _calculate_overall(self, metrics: dict) -> float:
        score = 100.0
        cr = metrics.get("comment_ratio", 0)
        if cr < 0.05:
            score -= 25
        elif cr < 0.1:
            score -= 15

        dup = metrics.get("duplication_score", {}).get("duplication_percentage", 0)
        if dup > 20:
            score -= 20
        elif dup > 10:
            score -= 10

        naming = metrics.get("naming_quality", {}).get("naming_conformance", 1.0)
        score -= (1 - naming) * 20

        complexity = metrics.get("avg_cyclomatic_complexity", 0)
        if complexity > 15:
            score -= 25
        elif complexity > 10:
            score -= 15
        elif complexity > 5:
            score -= 5

        mi = metrics.get("maintainability_index", 100)
        if mi > 80:
            score = min(100, score + 5)
        elif mi < 40:
            score -= 15

        return max(0, min(100, round(score, 1)))

    @staticmethod
    def _grade(score: float) -> str:
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"
