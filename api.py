"""
CodeSentinel — Lightweight Flask API for the frontend.
Exposes the AST Analyzer, Quality Scorer, and Code Optimizer as REST endpoints.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent dir to path so we can import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from api.analyzers.ast_analyzer import ASTAnalyzer
from api.analyzers.quality_scorer import QualityScorer
from api.analyzers.code_optimizer import CodeOptimizer

app = Flask(__name__)
CORS(app)  # Allow frontend to call API

ast_analyzer = ASTAnalyzer()
quality_scorer = QualityScorer()
code_optimizer = CodeOptimizer()


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Analyze code and return issues + quality metrics."""
    data = request.get_json()
    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field in request body"}), 400

    code = data["code"]
    language = data.get("language", "python")

    try:
        issues = ast_analyzer.analyze(code, language)
        metrics = quality_scorer.score(code, language)

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


@app.route("/api/optimize", methods=["POST"])
def optimize():
    """Optimize code and return optimized version with explanations."""
    data = request.get_json()
    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field in request body"}), 400

    code = data["code"]
    language = data.get("language", "python")

    try:
        result = code_optimizer.optimize(code, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "engine": "CodeSentinel v3.0"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
