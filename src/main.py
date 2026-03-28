"""
CodeSentinel — AI-Powered Code Review Agent
Main CLI entry point with Click-based command interface.

Usage (from within 01-CodeSentinel/ directory):
    python -m src.main review -f path/to/file.py
    python -m src.main review -f path/to/file.py --format json
    python -m src.main review -f path/to/file.py -o report.md
"""

import click
import asyncio
import sys
import json
from pathlib import Path
from typing import Optional

import yaml
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("CodeSentinel")


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        logger.warning(f"Config not found at {config_path}, using defaults.")
        return get_default_config()
    with open(path) as f:
        return yaml.safe_load(f)


def get_default_config() -> dict:
    return {
        "llm": {
            "primary": "openai",
            "fallback": "anthropic",
            "models": {
                "openai": "gpt-4o",
                "anthropic": "claude-3-5-sonnet-20241022",
                "ollama": "llama3:70b",
            },
        },
        "analysis": {
            "security": True,
            "quality": True,
            "architecture": True,
            "max_file_size_kb": 500,
        },
        "reporting": {
            "format": "markdown",
            "include_fixes": True,
            "severity_threshold": "medium",
        },
    }


class CodeSentinelEngine:
    """Core engine that orchestrates all analysis components."""

    SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

    def __init__(self, config: dict, local_only: bool = False):
        self.config = config
        self.local_only = local_only

        # Always available (no LLM needed)
        from .analyzers.ast_analyzer import ASTAnalyzer
        from .analyzers.quality_scorer import QualityScorer
        from .reporters.report_engine import ReportEngine

        self.ast_analyzer = ASTAnalyzer()
        self.quality_scorer = QualityScorer()
        self.report_engine = ReportEngine(config.get("reporting", {}))

        # LLM-powered components (only if not local-only)
        self.llm = None
        self.security_scanner = None
        self.architecture_reviewer = None

        if not local_only:
            try:
                from .llm.orchestrator import LLMOrchestrator
                from .analyzers.security_scanner import SecurityScanner
                from .analyzers.architecture_reviewer import ArchitectureReviewer
                self.llm = LLMOrchestrator(config.get("llm", {}))
                self.security_scanner = SecurityScanner(self.llm)
                self.architecture_reviewer = ArchitectureReviewer(self.llm)
            except Exception as e:
                logger.warning(f"LLM components unavailable ({e}), running in local-only mode")
                self.local_only = True

    async def review_file(self, file_path: str, generate_fixes: bool = True) -> dict:
        """Perform comprehensive review of a single file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        size_kb = path.stat().st_size / 1024
        max_size = self.config.get("analysis", {}).get("max_file_size_kb", 500)
        if size_kb > max_size:
            raise ValueError(f"File too large: {size_kb:.1f}KB > {max_size}KB limit")

        code = path.read_text(encoding="utf-8", errors="replace")
        language = self._detect_language(path)

        logger.info(f"Reviewing {file_path} ({language}, {size_kb:.1f}KB)")

        results = {"file": str(path), "language": language, "issues": [], "metrics": {}}

        # --- AST Analysis (always runs, no LLM needed) ---
        ast_issues = self.ast_analyzer.analyze(code, language)
        results["issues"].extend(ast_issues)

        # --- Security Scanning (LLM-powered, skip in local mode) ---
        if not self.local_only and self.security_scanner:
            if self.config.get("analysis", {}).get("security", True):
                security_issues = await self.security_scanner.scan(code, language)
                results["issues"].extend(security_issues)

        # --- Quality Scoring (always runs, no LLM needed) ---
        if self.config.get("analysis", {}).get("quality", True):
            metrics = self.quality_scorer.score(code, language)
            results["metrics"] = metrics

        # --- Architecture Review (LLM-powered, skip in local mode) ---
        if not self.local_only and self.architecture_reviewer:
            if self.config.get("analysis", {}).get("architecture", True):
                arch_issues = await self.architecture_reviewer.review(code, language, str(path))
                results["issues"].extend(arch_issues)

        # --- Generate fixes via LLM (skip in local mode) ---
        if not self.local_only and generate_fixes and results["issues"] and self.llm:
            critical_issues = [
                i for i in results["issues"]
                if self.SEVERITY_ORDER.get(i.get("severity", "info"), 4) <= 2
            ]
            if critical_issues:
                fixes = await self._generate_fixes(code, critical_issues, language)
                results["fixes"] = fixes

        # Sort by severity
        results["issues"].sort(
            key=lambda x: self.SEVERITY_ORDER.get(x.get("severity", "info"), 4)
        )

        return results

    async def review_repo(self, repo_path: str, depth: str = "standard") -> dict:
        """Review entire repository."""
        repo = Path(repo_path)
        extensions = {".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c"}
        files = [f for f in repo.rglob("*") if f.suffix in extensions and ".git" not in str(f)]

        if depth == "standard":
            files = files[:50]

        all_results = []
        for file in files:
            try:
                result = await self.review_file(str(file))
                all_results.append(result)
            except Exception as e:
                logger.warning(f"Skipping {file}: {e}")

        return {"type": "repo_review", "repo": str(repo), "depth": depth, "files": all_results}

    async def _generate_fixes(self, code: str, issues: list, language: str) -> list:
        """Use LLM to generate fix suggestions."""
        fixes = []
        issues_text = "\n".join(
            f"- [{i['severity'].upper()}] Line {i.get('line', '?')}: {i['message']}"
            for i in issues[:10]
        )
        prompt = f"""You are an expert code reviewer. Given the following {language} code and issues, provide fix suggestions.

CODE:
```{language}
{code[:3000]}
```

ISSUES FOUND:
{issues_text}

For each issue provide: the fix, why it's needed, and any side effects."""

        try:
            response = await self.llm.generate(prompt, max_tokens=2000)
            fixes.append({"raw_response": response, "issue_count": len(issues)})
        except Exception as e:
            logger.error(f"Fix generation failed: {e}")

        return fixes

    @staticmethod
    def _detect_language(path: Path) -> str:
        ext_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".go": "go", ".rs": "rust", ".java": "java",
            ".cpp": "cpp", ".c": "c", ".rb": "ruby",
            ".php": "php", ".swift": "swift", ".kt": "kotlin",
        }
        return ext_map.get(path.suffix.lower(), "unknown")


# ─── CLI ────────────────────────────────────────────

@click.group()
@click.option("--config", "-c", default="config/config.yaml", help="Config file path")
@click.pass_context
def cli(ctx, config):
    """CodeSentinel — AI-Powered Code Review Agent"""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)


@cli.command()
@click.option("--file", "-f", required=True, help="File to review")
@click.option("--output", "-o", default=None, help="Output report file path")
@click.option("--format", "fmt", type=click.Choice(["markdown", "json", "html"]), default="markdown")
@click.option("--local", is_flag=True, default=True, help="Run in local-only mode (no LLM API keys needed)")
@click.pass_context
def review(ctx, file, output, fmt, local):
    """Review a file for issues, vulnerabilities, and quality."""
    config = ctx.obj["config"]
    engine = CodeSentinelEngine(config, local_only=local)

    async def _run():
        result = await engine.review_file(file)

        # Print to terminal
        issues = result.get("issues", [])
        metrics = result.get("metrics", {})
        severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}

        click.echo(f"\n{'='*60}")
        click.echo(f"🛡️  CodeSentinel — Review Report")
        click.echo(f"{'='*60}")
        click.echo(f"📄 File: {result['file']}")
        click.echo(f"🔤 Language: {result['language']}")
        click.echo(f"⚠️  Issues found: {len(issues)}")
        click.echo(f"{'─'*60}")

        if issues:
            for issue in issues:
                sev = issue.get("severity", "info")
                icon = severity_icons.get(sev, "⚪")
                line = issue.get("line", "?")
                msg = issue.get("message", "")
                click.echo(f"  {icon} [{sev.upper():8s}] Line {line:>3}: {msg}")
        else:
            click.echo("  ✅ No issues found!")

        if metrics:
            click.echo(f"\n{'─'*60}")
            click.echo(f"📊 Quality Metrics")
            click.echo(f"{'─'*60}")
            click.echo(f"  Score: {metrics.get('overall_score', 0)}/100 (Grade: {metrics.get('grade', '?')})")
            click.echo(f"  Functions: {metrics.get('function_count', 0)} | Classes: {metrics.get('class_count', 0)}")
            click.echo(f"  Avg Complexity: {metrics.get('avg_cyclomatic_complexity', 0)}")
            click.echo(f"  Maintainability: {metrics.get('maintainability_index', 0)}")
            loc = metrics.get("lines_of_code", {})
            click.echo(f"  LOC: {loc.get('code', 0)} code, {loc.get('comments', 0)} comments, {loc.get('blank', 0)} blank")
            dup = metrics.get("duplication_score", {})
            click.echo(f"  Duplication: {dup.get('duplication_percentage', 0)}%")

        # Save report
        if output:
            if fmt == "json":
                Path(output).write_text(json.dumps(result, indent=2))
            else:
                report = engine.report_engine.generate(result, fmt)
                Path(output).write_text(report)
            click.echo(f"\n💾 Report saved to: {output}")

    asyncio.run(_run())


@cli.command()
@click.option("--repo", "-r", default=".", help="Repository path")
@click.option("--depth", type=click.Choice(["standard", "full"]), default="standard")
@click.option("--output", "-o", default="codesentinel-report.md")
@click.pass_context
def scan(ctx, repo, depth, output):
    """Scan an entire repository."""
    config = ctx.obj["config"]
    engine = CodeSentinelEngine(config, local_only=True)

    async def _run():
        result = await engine.review_repo(repo, depth)
        files = result.get("files", [])
        total_issues = sum(len(f.get("issues", [])) for f in files)
        click.echo(f"\n🛡️  Scanned {len(files)} files, found {total_issues} issues")

        for f in files:
            issues = f.get("issues", [])
            grade = f.get("metrics", {}).get("grade", "?")
            click.echo(f"  [{grade}] {f['file']} — {len(issues)} issues")

    asyncio.run(_run())


if __name__ == "__main__":
    cli()
