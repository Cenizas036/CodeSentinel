"""
Vercel Serverless Function — /api/analyze
Runs AST analysis and quality scoring on submitted code.
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add the api directory to path so we can import analyzers
sys.path.insert(0, os.path.dirname(__file__))

from analyzers.ast_analyzer import ASTAnalyzer
from analyzers.quality_scorer import QualityScorer

ast_analyzer = ASTAnalyzer()
quality_scorer = QualityScorer()


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            code = data.get("code", "")
            language = data.get("language", "python")

            if not code.strip():
                self._send_json(400, {"error": "Missing 'code' field"})
                return

            # Run AST analysis
            issues = ast_analyzer.analyze(code, language)

            # Run quality scoring
            metrics = quality_scorer.score(code, language)

            # Sort issues by severity
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            issues.sort(key=lambda x: severity_order.get(x.get("severity", "info"), 4))

            result = {
                "success": True,
                "issues": issues,
                "metrics": metrics,
                "summary": {
                    "total_issues": len(issues),
                    "critical": sum(1 for i in issues if i.get("severity") == "critical"),
                    "high": sum(1 for i in issues if i.get("severity") == "high"),
                    "medium": sum(1 for i in issues if i.get("severity") == "medium"),
                    "low": sum(1 for i in issues if i.get("severity") == "low"),
                    "info": sum(1 for i in issues if i.get("severity") == "info"),
                },
            }

            self._send_json(200, result)

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
