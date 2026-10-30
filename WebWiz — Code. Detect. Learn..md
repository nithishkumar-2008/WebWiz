# WebWiz — Code. Detect. Learn.

WebWiz is a beginner-friendly HTML quality workbench. Students can edit a small HTML document, preview it in an isolated frame, analyze selected common mistakes, and learn the reasoning behind each suggested correction.

## Project overview

WebWiz uses a Flask backend and a plain HTML/CSS/vanilla JavaScript frontend. The backend parses bounded HTML using BeautifulSoup and returns structured findings. The frontend keeps the source in the browser, displays line numbers, renders reports, and applies only small reversible client-side fixes. No database, paid API, React, or Node.js is required.

## Features

The playground includes sample code, clear/load controls, line numbers, a safe preview, character limits, theme switching, and an undo stack. The analyzer checks for missing image alternative text, form controls without accessible labels, empty links, empty buttons, duplicate IDs, missing HTML5 doctype, a missing `lang` attribute, and a missing or empty document title. Each result includes a category, severity, line when available, explanation, reason, fix guidance, and before/after examples.

Click-to-Fix focuses the relevant source line, opens the suggested correction, and offers safe fixes for supported patterns. Learn Mode provides the “what, why, and how” lesson for the selected issue. The quality score is deliberately documented: it starts at 100, subtracts 15 points per critical issue, 8 per warning, and 3 per info issue, and never claims to measure checks that are not implemented.

## Technology

- Python 3.10+
- Flask
- BeautifulSoup 4 with Python’s built-in `html.parser`
- HTML5, CSS3, and vanilla JavaScript
- pytest for automated tests

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:3000` in a browser. To run the test suite:

```bash
pytest -q
```

The Flask server honors the `PORT` environment variable and binds to `0.0.0.0` for managed preview environments.

## Architecture and folder structure

`app.py` contains the Flask page, health check, and JSON analysis endpoint. `analyzer.py` is a pure, testable module with the supported rules and scoring. `templates/index.html` is the semantic page shell. `static/css/style.css` owns the Signal Blueprint visual system and responsive layout. `static/js/script.js` owns editor state, reports, preview, Click-to-Fix, Learn Mode, undo, and theme persistence. `tests/test_analyzer.py` covers each rule and the API contract. `manus-routes.json` declares the page route for managed preview discovery.

## Security notes

User HTML is never executed on the server. The preview uses an iframe with an empty `sandbox` attribute, so scripts and form submission are not enabled. The main application does not insert submitted HTML into its DOM; issue explanations and examples are written as text nodes. The API enforces a 100 KB input limit. This is a learning tool, not a security scanner: users should still avoid placing sensitive information in sample code.

## Screenshots

Run the application locally and capture the main workbench here when publishing the repository. The managed preview is the recommended source for a current screenshot.

![WebWiz workbench screenshot](https://private-us-east-1.manuscdn.com/sessionFile/Ch8iEkHIkucvRfiAsFt8Bt/sandbox/bVN2aV2jVbV5vw1la1wkDw-images_1793364841331_na1fn_L2hvbWUvdWJ1bnR1L3dlYndpei9kb2NzL3dlYndpei13b3JrYmVuY2g.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvQ2g4aUVrSElrdWN2UmZpQXNGdDhCdC9zYW5kYm94L2JWTjJhVjJqVmJWNXZ3MWxhMXdrRHctaW1hZ2VzXzE3OTMzNjQ4NDEzMzFfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzZGxZbmRwZWk5a2IyTnpMM2RsWW5kcGVpMTNiM0pyWW1WdVkyZy5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTQ3MDA4MDB9fX1dfQ__&Key-Pair-Id=K2QY5QTL8JSY6C&Signature=MEUCIQDH4APjfgP3chz~yjwcJ6y89tBZjXNqFgSEi1I~ScKEDAIgKZga1ULvx2etMDHBRliztUXtYxEyvGwkdoeExhoF4VY_)

## Limitations

WebWiz intentionally detects only the documented set of common issues. BeautifulSoup repairs malformed markup while parsing, so it is not a standards validator and cannot reliably report every nesting or closing-tag error. The score reflects implemented checks only; it is not a WCAG conformance score, a security audit, or a guarantee that a page is fully accessible.

## Future improvements

Possible next steps include richer structural validation, direct visual editor highlighting, downloadable reports, more accessibility checks, before-and-after code comparison, and HTML file upload support.

## GitHub preparation

The repository is designed to be understandable to a college student. Keep `.venv`, caches, and environment files out of Git, commit the source and tests, and add a real screenshot under `docs/` before publishing the README image.
