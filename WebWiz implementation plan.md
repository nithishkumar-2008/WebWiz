# WebWiz implementation plan

## Architecture

WebWiz is a small Flask application with no database. Flask serves `templates/index.html`, the CSS and JavaScript assets, and a JSON endpoint at `/api/analyze`. The browser owns the editing experience: it keeps the source in a textarea, renders line numbers beside it, sends bounded source to the analyzer, renders preview HTML only into a sandboxed iframe via `srcdoc`, and renders analyzer results using safe text/DOM APIs rather than interpolating user HTML into the application page.

`analyzer.py` uses BeautifulSoup with the built-in `html.parser` backend. It reports a stable issue object with `id`, `category`, `severity`, `line`, `message`, `why`, `fix`, `bad_example`, `good_example`, and optional `fix_type`. Line numbers are inferred from source offsets so findings remain useful even when the parser repairs malformed markup. `app.py` enforces a 100 KB analysis limit and returns friendly JSON errors.

## Folder structure

- `app.py`: Flask routes, request validation, and development entry point.
- `analyzer.py`: pure HTML analysis rules and score/report aggregation.
- `templates/index.html`: semantic application shell and accessible controls.
- `static/css/style.css`: responsive dark/light developer-tool styling.
- `static/js/script.js`: editor state, API calls, preview, report, click-to-fix, learn mode, undo, and theme behavior.
- `tests/test_analyzer.py`: rule, line-number, malformed-input, empty-input, score, and size-limit coverage.
- `requirements.txt`: pinned runtime/test dependencies.
- `README.md`: setup, feature, limitation, and GitHub handoff documentation.
- `manus-routes.json`: declared page route for managed preview discovery.

## Design direction

Three candidate directions: Terminal Atelier (0.06): a focused code-workbench with warm paper accents. Signal Blueprint (0.08): an editorial developer tool with electric blue diagnostics. Quiet Compiler (0.04): restrained monochrome panels with precise status colors.

Chosen style: **Signal Blueprint**.

- **Design Movement:** Editorial developer tooling, borrowing the hierarchy of IDEs and the calm precision of technical blueprints.
- **Core Principles:** Make the next action obvious; pair every warning with a reason; use color as a diagnostic signal, not decoration; keep dense information breathable.
- **Color Philosophy:** Deep navy surfaces create focus, off-white text preserves reading comfort, and electric cyan is WebWiz’s own signal color for active tooling. Amber and coral are reserved for severity so the palette teaches priority.
- **Layout Paradigm:** A split workbench: a narrow orientation rail, a dominant editor/preview workspace, and a report column that can collapse below the workbench on small screens.
- **Signature Elements:** Cyan top rule, numbered editor gutter, and compact issue cards with severity rails.
- **Interaction Philosophy:** Every click should either reveal context, move the learner to the source, or make a safe reversible change.
- **Animation:** Use short 160–220ms transitions for panels and focus states; no looping motion. Newly selected issues get a brief cyan glow; score changes use a subtle count-up feel without delaying interaction.
- **Typography System:** Inter for interface copy and JetBrains Mono for code, line numbers, issue IDs, and metrics. Headings are compact and high-contrast; body copy remains readable at 15–16px.
- **Brand Essence:** A friendly HTML quality workbench for learners who want to understand mistakes, not just silence warnings; precise, encouraging, practical.
- **Brand Voice:** Headlines are direct and confidence-building. CTAs say “Analyze my HTML” and “Show me the fix”; helper copy says “Start with one issue. Leave with a pattern you can reuse.”
- **Wordmark & Logo:** “WebWiz” is paired with a small bracket-and-spark mark suggesting source code becoming insight.
- **Signature Brand Color:** Signal cyan `#63e6ff`.

## Build workflow

1. Implement and test pure analyzer rules.
2. Add Flask routes and the semantic HTML shell.
3. Add the responsive editor, line gutter, preview isolation, report, and theme state.
4. Add issue selection, source focus, safe manual fix actions, undo, and learn content.
5. Run automated tests, syntax checks, and a live HTTP smoke test; correct defects.
6. Finish README and prepare a clean Git checkpoint.

The first version intentionally covers selected common issues, not every HTML error and not full WCAG conformance.
