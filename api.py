"""
CodeSentinel — Lightweight Flask API for the frontend.
Exposes the AST Analyzer and Quality Scorer as REST endpoints.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent dir to path so we can import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.analyzers.ast_analyzer import ASTAnalyzer
from src.analyzers.quality_scorer import QualityScorer

app = Flask(__name__)
CORS(app)  # Allow frontend to call API

ast_analyzer = ASTAnalyzer()
quality_scorer = QualityScorer()


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Analyze code and return issues + quality metrics."""
    data = request.get_json()
    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field in request body"}), 400

    code = data["code"]
    language = data.get("language", "python")

    try:
        # Run AST analysis
        issues = ast_analyzer.analyze(code, language)

        # Run quality scoring
        metrics = quality_scorer.score(code, language)

        # Sort issues by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        issues.sort(key=lambda x: severity_order.get(x.get("severity", "info"), 4))

        return jsonify({
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
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "engine": "CodeSentinel v2.4"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
