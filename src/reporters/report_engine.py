"""Report Engine — Generates formatted review reports."""

import json
import logging
from datetime import datetime

logger = logging.getLogger("CodeSentinel.Report")


class ReportEngine:
    """Generates review reports in multiple formats."""

    def __init__(self, config: dict = None):
        self.config = config or {}

    def generate(self, results: dict, fmt: str = "markdown") -> str:
        generators = {
            "markdown": self._markdown,
            "json": self._json,
            "html": self._html,
        }
        generator = generators.get(fmt, self._markdown)
        return generator(results)

    def _markdown(self, results: dict) -> str:
        lines = [
            "# 🛡️ CodeSentinel Review Report",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
        ]

        if results.get("type") in ("diff_review", "repo_review"):
            files = results.get("files", [])
            total_issues = sum(len(f.get("issues", [])) for f in files)
            lines.append(f"**Files reviewed:** {len(files)}")
            lines.append(f"**Total issues:** {total_issues}")
            lines.append("")

            for file_result in files:
                lines.extend(self._format_file_section(file_result))
        else:
            lines.extend(self._format_file_section(results))

        return "\n".join(lines)

    def _format_file_section(self, result: dict) -> list:
        lines = [
            f"## 📄 {result.get('file', 'Unknown')}",
            f"**Language:** {result.get('language', 'unknown')}",
            "",
        ]

        # Metrics
        metrics = result.get("metrics", {})
        if metrics:
            lines.append("### 📊 Quality Metrics")
            grade = metrics.get("grade", "?")
            score = metrics.get("overall_score", 0)
            lines.append(f"**Overall Grade: {grade} ({score}/100)**")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            for key, value in metrics.items():
                if key not in ("grade", "overall_score") and not isinstance(value, dict):
                    lines.append(f"| {key.replace('_', ' ').title()} | {value} |")
            lines.append("")

        # Issues
        issues = result.get("issues", [])
        if issues:
            severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}
            lines.append(f"### ⚠️ Issues ({len(issues)})")
            lines.append("")

            for issue in issues:
                sev = issue.get("severity", "info")
                icon = severity_icons.get(sev, "⚪")
                line_num = issue.get("line", "?")
                msg = issue.get("message", "")
                lines.append(f"- {icon} **[{sev.upper()}]** Line {line_num}: {msg}")

            lines.append("")

        # Fixes
        fixes = result.get("fixes", [])
        if fixes:
            lines.append("### 🔧 Suggested Fixes")
            for fix in fixes:
                lines.append(f"```\n{fix.get('raw_response', '')[:500]}\n```")
            lines.append("")

        lines.append("---")
        return lines

    def _json(self, results: dict) -> str:
        return json.dumps(results, indent=2, default=str)

    def _html(self, results: dict) -> str:
        md = self._markdown(results)
        return f"""<!DOCTYPE html>
<html><head><title>CodeSentinel Report</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; background: #0d1117; color: #c9d1d9; }}
h1 {{ color: #58a6ff; }} h2 {{ color: #79c0ff; }} h3 {{ color: #d2a8ff; }}
pre {{ background: #161b22; padding: 16px; border-radius: 6px; overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #30363d; padding: 8px 12px; text-align: left; }}
th {{ background: #161b22; }}
</style></head>
<body><pre>{md}</pre></body></html>"""
