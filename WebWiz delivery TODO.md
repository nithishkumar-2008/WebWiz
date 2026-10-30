# WebWiz delivery TODO

- [x] **Backend and analyzer:** Flask serves the application and bounded `/api/analyze` requests; the Python analyzer detects missing image alt attributes, form controls without accessible labels, empty links and buttons, duplicate IDs, missing title, and selected structural issues; findings include category, severity, explanation, and line when available.
- [x] **HTML playground:** Provide sample HTML, editable source with line numbers, clear/load sample controls, a Run Preview button, and a sandboxed iframe preview.
- [x] **Analysis report:** Show total issues, category/severity groupings, and a documented score based only on implemented checks; allow re-analysis after edits.
- [x] **Click-to-Fix and Learn Mode:** Clicking a finding focuses its source line, shows a suggested correction, supports safe reversible fixes for supported findings, preserves original source through undo, and explains each issue with incorrect/correct examples.
- [x] **Responsive UI:** Provide professional desktop/mobile layouts, dark/light theme toggle, clear typography, spacing, active states, and helpful error messages.
- [x] **Security boundaries:** Treat submitted HTML as untrusted, cap input size, never execute it on the server, avoid putting source HTML into the main DOM, and isolate preview content in a sandboxed iframe.
- [x] **Testing and handoff:** Test each rule, empty/malformed HTML, line numbers, score behavior, and Flask API validation; document setup, features, screenshots section, limitations, and future improvements.
