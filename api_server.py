from flask import Flask, jsonify, request
from flask_cors import CORS
from dictionary_service import DictionaryService

app = Flask(__name__)
# Allows your frontend to call this API regardless of port differences
CORS(app)  

# Shared instance of the updated, language-aware service
dictionary_service = DictionaryService("dictionary.json")

@app.route("/lookup", methods=["GET"])
def lookup():
    # 1. Extract parameters from the query string
    word = request.args.get("word", "").strip()
    # 2. Extract language (default to 'en' for backward compatibility)
    lang = request.args.get("lang", "en").strip().lower()

    if not word:
        return jsonify({
            "status": "error",
            "error": "No word provided.",
            "definition": None,
            "source": None
        }), 400

    # 3. Call the updated service method with both word and language
    result = dictionary_service.lookup(word, lang)

    if result:
        # Success response including the dynamic source (e.g., "API (FR)")
        return jsonify({
            "status": "success",
            "definition": result["definition"],
            "source": result["source"],
            "error": None
        }), 200
    else:
        suggestions = dictionary_service.get_suggestions(word)
        # Not found response
        return jsonify({
            "status": "not_found",
            "definition": None,
            "suggestions": suggestions,
            "source": None,
            "error": f"'{word}' was not found in {lang.upper()}. Did you mean: {', '.join(suggestions)}?" if suggestions else f"'{word}' was not found in {lang.upper()} and no close matches were found."
        }), 404


@app.route("/health", methods=["GET"])
def health():
    """Endpoint for the frontend status dot."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # Standard development port for your project
    app.run(host="0.0.0.0", port=5001, debug=True)