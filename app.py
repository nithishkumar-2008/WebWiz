"""Flask entry point for WebWiz."""

import os

from flask import Flask, jsonify, render_template, request, send_from_directory

from analyzer import MAX_HTML_LENGTH, analyze_html

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_HTML_LENGTH + 4_096


@app.get("/")
def index():
    return render_template("index.html", max_html_length=MAX_HTML_LENGTH)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "webwiz"})


@app.get("/manus-routes.json")
def route_manifest():
    return send_from_directory(app.root_path, "manus-routes.json", mimetype="application/json")


@app.post("/api/analyze")
def analyze():
    if not request.is_json:
        return jsonify({"error": "Send JSON with an html field."}), 415
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("html"), str):
        return jsonify({"error": "The html field must be a string."}), 400
    source = payload["html"]
    if len(source) > MAX_HTML_LENGTH:
        return jsonify({"error": f"HTML is limited to {MAX_HTML_LENGTH:,} characters."}), 413
    try:
        return jsonify(analyze_html(source))
    except ValueError as error:
        return jsonify({"error": str(error)}), 413
    except Exception:
        app.logger.exception("Unexpected analyzer failure")
        return jsonify({"error": "WebWiz could not analyze that input. Try simplifying the HTML."}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "3000")), debug=True)
