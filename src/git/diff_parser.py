"""Git Diff Parser — Parses git diffs for targeted review."""

import subprocess
import logging
from pathlib import Path

logger = logging.getLogger("CodeSentinel.Git")


class DiffParser:
    """Parses git diffs and extracts changed files with context."""

    def parse_diff(self, base_ref: str = "HEAD~1") -> list:
        """Parse git diff and return list of changed files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-status", base_ref],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                logger.error(f"Git diff failed: {result.stderr}")
                return []

            files = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) >= 2:
                    status_map = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed"}
                    status = status_map.get(parts[0][0], "unknown")
                    file_path = parts[-1]
                    files.append({
                        "path": file_path,
                        "status": status,
                        "hunks": self._get_hunks(file_path, base_ref) if status != "deleted" else [],
                    })

            return files

        except subprocess.TimeoutExpired:
            logger.error("Git diff timed out")
            return []
        except FileNotFoundError:
            logger.error("Git not found in PATH")
            return []

    def _get_hunks(self, file_path: str, base_ref: str) -> list:
        """Get diff hunks for a specific file."""
        try:
            result = subprocess.run(
                ["git", "diff", "-U3", base_ref, "--", file_path],
                capture_output=True, text=True, timeout=30,
            )
            hunks = []
            current_hunk = None

            for line in result.stdout.split("\n"):
                if line.startswith("@@"):
                    if current_hunk:
                        hunks.append(current_hunk)
                    current_hunk = {"header": line, "lines": []}
                elif current_hunk is not None:
                    current_hunk["lines"].append(line)

            if current_hunk:
                hunks.append(current_hunk)

            return hunks
        except Exception:
            return []
