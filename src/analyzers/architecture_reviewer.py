"""Architecture Reviewer — LLM-powered architectural analysis."""

import logging

logger = logging.getLogger("CodeSentinel.Architecture")


class ArchitectureReviewer:
    """Uses LLM to review code architecture and design patterns."""

    def __init__(self, llm_orchestrator):
        self.llm = llm_orchestrator

    async def review(self, code: str, language: str, file_path: str) -> list:
        """Review code for architectural issues using LLM."""
        if len(code) < 100:
            return []

        prompt = f"""Analyze this {language} code for architectural issues and design pattern violations.

File: {file_path}

```{language}
{code[:4000]}
```

Check for:
1. SOLID principle violations
2. Anti-patterns (God class, spaghetti code, tight coupling)
3. Missing design patterns that would improve the code
4. Separation of concerns issues
5. Dependency injection opportunities

Return findings as a JSON array of objects with keys:
- type: string (e.g., "solid_violation", "anti_pattern", "missing_pattern")
- severity: "high" | "medium" | "low"  
- line: int (approximate line number, 0 if general)
- message: string (clear description)
- category: "architecture"
- suggestion: string (how to fix it)

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
                return findings[:10]
        except Exception as e:
            logger.debug(f"Architecture review parsing failed: {e}")

        return []
