# This is the main file that runs the gateway
# It creates a simple web API using Flask

from flask import Flask, request, jsonify, render_template
from flask import Flask, request, jsonify
from policy_engine import process_input
import time  # for measuring latency

app = Flask(__name__)

@app.route("/")
def home():
    """Simple home route to check if server is running"""
    return "LLM Security Gateway is running!"


@app.route("/check", methods=["POST"])
def check_input():
    """
    Main gateway endpoint.
    User sends a message, gateway returns a decision.
    """

    # Get the message from the request
    data = request.get_json()

    # If no message provided, return error
    if not data or "message" not in data:
        return jsonify({"error": "Please provide a message..."}), 400

    user_message = data["message"]

    # Measure how long the gateway takes (latency)
    start_time = time.time()
    result = process_input(user_message)
    end_time = time.time()

    # Add latency to result (in milliseconds)
    result["latency_ms"] = round((end_time - start_time) * 1000, 2)

    return jsonify(result)
@app.route("/ui")
def ui():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)