from flask import Flask, jsonify, request
from flask_cors import CORS
from dictionary_service import DictionaryService

app = Flask(__name__)
CORS(app)  # Allows the browser frontend to call this API

# One shared instance — same pattern as the TCP server
dictionary_service = DictionaryService("dictionary.json")

@app.route("/lookup", methods=["GET"])
def lookup():
    word = request.args.get("word", "").strip()

    if not word:
        return jsonify({
            "status": "error",
            "error": "No word provided.",
            "definition": None,
            "source": None
        }), 400

    result = dictionary_service.lookup(word)

    if result:
        return jsonify({
            "status": "success",
            "definition": result["definition"],
            "source": result["source"],
            "error": None
        }), 200
    else:
        return jsonify({
            "status": "not_found",
            "definition": None,
            "source": None,
            "error": f"'{word}' was not found."
        }), 404


@app.route("/health", methods=["GET"])
def health():
    """Simple endpoint to check if the API server is alive."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)