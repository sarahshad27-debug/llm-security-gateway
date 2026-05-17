<<<<<<< HEAD
=======
# This is the main file that runs the gateway using flask

>>>>>>> 236d651ce38f5e861f8db3a99d6c3b7c9c7ddb78
from flask import Flask, request, jsonify, render_template
from policy_engine import process_input
<<<<<<< HEAD
import uuid
=======
import time  # to measure latency
>>>>>>> 236d651ce38f5e861f8db3a99d6c3b7c9c7ddb78

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
<<<<<<< HEAD
    data = request.get_json()

=======
    """
    Main gateway endpoint.
    User sends a message, gateway returns a decision.
    """

    # message from the request
    data = request.get_json()

    # If no message provided
>>>>>>> 236d651ce38f5e861f8db3a99d6c3b7c9c7ddb78
    if not data or "message" not in data:
        return jsonify({"error": "Please provide a message..."}), 400

    user_message = data["message"]
    language = data.get("language", "auto")

<<<<<<< HEAD
    result = process_input(user_message, language=language)

    # Add backward-compatible fields
    result["original_input"] = user_message
    result["injection_score"] = result["rule_score"]
    result["cleaned_input"] = result["safe_text"]
    result["pii_found"] = [e["type"] for e in result["pii_entities"]]
    result["reason"] = ", ".join(result["reason_codes"]) if result["reason_codes"] else "Input is clean"
=======
    # Measure latency
    start_time = time.time()
    result = process_input(user_message)
    end_time = time.time()

    # Adding latency 
    result["latency_ms"] = round((end_time - start_time) * 1000, 2)
>>>>>>> 236d651ce38f5e861f8db3a99d6c3b7c9c7ddb78

    return jsonify(result)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "LLM Security Gateway"})


@app.route("/ui")
def ui():
    return render_template("index.html")


if __name__ == "__main__":
<<<<<<< HEAD
    app.run(debug=True, port=5000)
=======
    app.run(debug=True)
>>>>>>> 236d651ce38f5e861f8db3a99d6c3b7c9c7ddb78
