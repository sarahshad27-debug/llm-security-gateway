from flask import Flask, request, jsonify, render_template
from policy_engine import process_input
import uuid

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "service": "LLM Security Gateway",
        "version": "2.0 (Lab Final)",
        "endpoints": ["/analyze", "/health", "/ui"]
    })


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Please provide a 'message' field."}), 400

    user_message = data["message"]
    language = data.get("language", "auto")
    input_id = data.get("input_id", str(uuid.uuid4())[:8])

    result = process_input(user_message, language=language, input_id=input_id)
    return jsonify(result)


@app.route("/check", methods=["POST"])
def check_input():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Please provide a message..."}), 400

    user_message = data["message"]
    language = data.get("language", "auto")

    result = process_input(user_message, language=language)

    # Add backward-compatible fields
    result["original_input"] = user_message
    result["injection_score"] = result["rule_score"]
    result["cleaned_input"] = result["safe_text"]
    result["pii_found"] = [e["type"] for e in result["pii_entities"]]
    result["reason"] = ", ".join(result["reason_codes"]) if result["reason_codes"] else "Input is clean"

    return jsonify(result)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "LLM Security Gateway"})


@app.route("/ui")
def ui():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)