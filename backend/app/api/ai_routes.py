from flask import Blueprint, request, jsonify
from app.utility.ai.ai_gemini import generate_text

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/generate", methods=["POST"])
def generate():
    payload = request.get_json(silent=True) or {}
    prompt = payload.get("prompt") or payload.get("message") or ""
    if not prompt or not isinstance(prompt, str):
        return jsonify({"error": "prompt is required"}), 400

    try:
        result_text = generate_text(prompt)
        return jsonify({"result": result_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500