"""
Security Scanner — LLM-enhanced security vulnerability detection.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger("CodeSentinel.Security")


class SecurityScanner:
    """Scans code for security vulnerabilities using pattern matching + LLM analysis."""

    OWASP_PATTERNS = {
        "sql_injection": {
            "patterns": [
                r'f["\'].*(?:SELECT|INSERT|UPDATE|DELETE|DROP).*{',
                r'\.format\(.*(?:SELECT|INSERT|UPDATE|DELETE)',
                r'%\s*(?:SELECT|INSERT|UPDATE|DELETE)',
                r'\+\s*["\'].*(?:SELECT|INSERT|UPDATE|DELETE)',
            ],
            "severity": "critical",
            "cwe": "CWE-89",
            "description": "SQL Injection vulnerability — use parameterized queries",
        },
        "xss": {
            "patterns": [
                r'innerHTML\s*=',
                r'document\.write\s*\(',
                r'\.html\s*\([^)]*\+',
                r'dangerouslySetInnerHTML',
            ],
            "severity": "high",
            "cwe": "CWE-79",
            "description": "Cross-Site Scripting (XSS) vulnerability",
        },
        "path_traversal": {
            "patterns": [
                r'open\s*\([^)]*\+',
                r'os\.path\.join\s*\([^)]*request',
                r'Path\s*\([^)]*request',
            ],
            "severity": "high",
            "cwe": "CWE-22",
            "description": "Path traversal vulnerability — sanitize file paths",
        },
        "command_injection": {
            "patterns": [
                r'os\.system\s*\([^)]*\+',
                r'subprocess\.call\s*\([^)]*shell\s*=\s*True',
                r'subprocess\.Popen\s*\([^)]*shell\s*=\s*True',
            ],
            "severity": "critical",
            "cwe": "CWE-78",
            "description": "OS Command Injection — avoid shell=True and sanitize inputs",
        },
        "insecure_deserialization": {
            "patterns": [
                r'pickle\.loads?\s*\(',
                r'yaml\.load\s*\([^)]*(?!Loader)',
                r'marshal\.loads?\s*\(',
                r'shelve\.open\s*\(',
            ],
            "severity": "high",
            "cwe": "CWE-502",
            "description": "Insecure deserialization — use safe loading methods",
        },
        "hardcoded_credentials": {
            "patterns": [
                r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
                r'(?:api_key|apikey|secret)\s*=\s*["\'][^"\']+["\']',
                r'(?:token|auth)\s*=\s*["\'][A-Za-z0-9+/=]{20,}["\']',
            ],
            "severity": "critical",
            "cwe": "CWE-798",
            "description": "Hardcoded credentials detected — use environment variables or secret management",
        },
        "weak_crypto": {
            "patterns": [
                r'(?:md5|MD5)\s*\(',
                r'(?:sha1|SHA1)\s*\(',
                r'hashlib\.md5',
                r'hashlib\.sha1',
                r'DES\.',
                r'RC4\.',
            ],
            "severity": "medium",
            "cwe": "CWE-327",
            "description": "Weak cryptographic algorithm — use SHA-256+ or bcrypt",
        },
        "insecure_random": {
            "patterns": [
                r'random\.random\s*\(',
                r'random\.randint\s*\(',
                r'Math\.random\s*\(',
            ],
            "severity": "medium",
            "cwe": "CWE-330",
            "description": "Insecure randomness — use secrets module or crypto.getRandomValues()",
        },
    }

    def __init__(self, llm_orchestrator=None):
        self.llm = llm_orchestrator

    async def scan(self, code: str, language: str) -> list:
        """Perform comprehensive security scan."""
        issues = []

        # Pattern-based scanning
        pattern_issues = self._pattern_scan(code)
        issues.extend(pattern_issues)

        # Dependency check (for requirements files)
        dep_issues = self._check_dependencies(code, language)
        issues.extend(dep_issues)

        # LLM-enhanced deep analysis for critical code
        if self.llm and len(code) < 5000:
            try:
                llm_issues = await self._llm_security_review(code, language)
                issues.extend(llm_issues)
            except Exception as e:
                logger.warning(f"LLM security review failed: {e}")

        return issues

    def _pattern_scan(self, code: str) -> list:
        """Scan code against OWASP vulnerability patterns."""
        issues = []
        lines = code.split("\n")

        for vuln_type, vuln_info in self.OWASP_PATTERNS.items():
            for pattern in vuln_info["patterns"]:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append({
                            "type": vuln_type,
                            "severity": vuln_info["severity"],
                            "line": line_num,
                            "message": f"[{vuln_info['cwe']}] {vuln_info['description']}",
                            "category": "security",
                            "code_snippet": line.strip()[:100],
                        })

        return issues

    def _check_dependencies(self, code: str, language: str) -> list:
        """Check for known vulnerable dependency patterns."""
        issues = []
        vulnerable_packages = {
            "python": {
                "pyyaml<5.4": "CVE-2020-14343: Arbitrary code execution",
                "django<3.2": "Multiple security vulnerabilities",
                "flask<2.0": "Multiple security improvements in 2.0+",
                "requests<2.20": "CVE-2018-18074: Session fixation",
                "urllib3<1.26.5": "CVE-2021-33503: ReDoS vulnerability",
                "pillow<9.0": "Multiple buffer overflow vulnerabilities",
                "cryptography<3.3": "CVE-2020-36242: Buffer overflow",
                "jinja2<3.1": "XSS vulnerabilities in older versions",
            }
        }

        # Simple version detection in import statements or requirements
        for pkg, vuln in vulnerable_packages.get(language, {}).items():
            pkg_name = pkg.split("<")[0]
            if pkg_name in code:
                issues.append({
                    "type": "vulnerable_dependency",
                    "severity": "medium",
                    "line": 0,
                    "message": f"Potentially vulnerable dependency `{pkg}`: {vuln}. Verify version.",
                    "category": "security",
                })

        return issues

    async def _llm_security_review(self, code: str, language: str) -> list:
        """Use LLM for deep security analysis beyond pattern matching."""
        prompt = f"""Analyze this {language} code for security vulnerabilities that pattern matching might miss.
Focus on:
1. Business logic flaws
2. Authentication/authorization issues
3. Data validation gaps
4. Race conditions
5. Information disclosure

CODE:
```{language}
{code[:4000]}
```

Return findings as a JSON array of objects with keys: type, severity (critical/high/medium/low), line (int), message, category (always "security").
Return empty array [] if no issues found. Return ONLY the JSON array."""

        try:
            import json
            response = await self.llm.generate(prompt, max_tokens=1500)
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
            findings = json.loads(response)
            if isinstance(findings, list):
                for f in findings:
                    f["source"] = "llm_analysis"
                return findings
        except Exception as e:
            logger.debug(f"LLM security parsing failed: {e}")

        return []
