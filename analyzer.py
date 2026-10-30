"""Beginner-friendly HTML quality checks used by the WebWiz API."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from bs4 import BeautifulSoup, Tag

MAX_HTML_LENGTH = 100_000


def _line_number(source: str, position: int | None) -> int | None:
    if position is None:
        return None
    return source.count("\n", 0, position) + 1


def _tag_line(source: str, soup: BeautifulSoup, tag: Tag) -> int | None:
    """Find a tag's source line without depending on parser-specific offsets."""
    matches = list(re.finditer(rf"<\s*{re.escape(tag.name)}\b[^>]*>", source, re.I))
    same_name = soup.find_all(tag.name)
    try:
        ordinal = same_name.index(tag)
    except ValueError:
        ordinal = 0
    return _line_number(source, matches[min(ordinal, len(matches) - 1)].start()) if matches else None


def _source_line(source: str, needle: str) -> int | None:
    position = source.lower().find(needle.lower())
    return _line_number(source, position) if position >= 0 else None


def _issue(
    *,
    rule: str,
    category: str,
    severity: str,
    line: int | None,
    message: str,
    why: str,
    fix: str,
    bad_example: str,
    good_example: str,
    fix_type: str | None = None,
) -> dict[str, Any]:
    return {
        "id": f"{rule}-{line or 'document'}",
        "rule": rule,
        "category": category,
        "severity": severity,
        "line": line,
        "message": message,
        "why": why,
        "fix": fix,
        "bad_example": bad_example,
        "good_example": good_example,
        "fix_type": fix_type,
    }


def _has_accessible_label(soup: BeautifulSoup, control: Tag) -> bool:
    if control.get("aria-label") or control.get("aria-labelledby"):
        return True
    control_id = control.get("id")
    if control_id and soup.find("label", attrs={"for": control_id}):
        return True
    return control.parent.name == "label" if control.parent else False


def analyze_html(source: str) -> dict[str, Any]:
    """Analyze a bounded HTML string and return findings plus a documented score."""
    source = source or ""
    if len(source) > MAX_HTML_LENGTH:
        raise ValueError(f"HTML is limited to {MAX_HTML_LENGTH:,} characters.")

    if not source.strip():
        return {
            "issues": [],
            "total": 0,
            "score": 100,
            "score_label": "Based on detected checks only",
            "severity_counts": {},
            "category_counts": {},
            "rules_checked": [
                "missing-alt",
                "missing-label",
                "empty-link",
                "empty-button",
                "duplicate-id",
                "missing-doctype",
                "missing-language",
                "missing-title",
            ],
        }

    soup = BeautifulSoup(source, "html.parser")
    issues: list[dict[str, Any]] = []

    # Accessibility: images need alt text, including an explicit empty alt for decorative art.
    for image in soup.find_all("img"):
        if image.get("alt") is None:
            issues.append(
                _issue(
                    rule="missing-alt",
                    category="Accessibility",
                    severity="warning",
                    line=_tag_line(source, soup, image),
                    message="Image is missing alternative text.",
                    why="Screen reader users need a text alternative, while decorative images should explicitly use alt=\"\".",
                    fix="Add a short description of the image's purpose, or use alt=\"\" when it is purely decorative.",
                    bad_example='<img src="student.jpg">',
                    good_example='<img src="student.jpg" alt="Student studying">',
                    fix_type="add-alt",
                )
            )

    # Accessibility: common form controls need a programmatic name.
    for control in soup.find_all(["input", "select", "textarea"]):
        raw_type = control.get("type")
        input_type = raw_type.lower() if isinstance(raw_type, str) else ""
        if input_type in {"hidden", "submit", "reset", "button", "image"}:
            continue
        if not _has_accessible_label(soup, control):
            issues.append(
                _issue(
                    rule="missing-label",
                    category="Accessibility",
                    severity="critical",
                    line=_tag_line(source, soup, control),
                    message="Form control has no accessible label.",
                    why="A visible label or accessible name tells keyboard and screen reader users what to enter.",
                    fix="Add a label with for=\"control-id\", wrap the control in a label, or provide aria-label when appropriate.",
                    bad_example='<input id="email" type="email">',
                    good_example='<label for="email">Email</label>\n<input id="email" type="email">',
                    fix_type="add-label",
                )
            )

    # Usability: links and buttons should communicate an action.
    for link in soup.find_all("a"):
        content = link.get_text(" ", strip=True)
        if not content and not (link.get("aria-label") or link.get("title")):
            issues.append(
                _issue(
                    rule="empty-link",
                    category="Usability",
                    severity="warning",
                    line=_tag_line(source, soup, link),
                    message="Link has no accessible text.",
                    why="People cannot understand or operate a link if its purpose is not exposed in text or an accessible name.",
                    fix="Add visible link text or an aria-label that describes the destination.",
                    bad_example='<a href="/profile"></a>',
                    good_example='<a href="/profile">View profile</a>',
                    fix_type="add-link-text",
                )
            )

    for button in soup.find_all("button"):
        content = button.get_text(" ", strip=True)
        if not content and not (button.get("aria-label") or button.get("title")):
            issues.append(
                _issue(
                    rule="empty-button",
                    category="Usability",
                    severity="warning",
                    line=_tag_line(source, soup, button),
                    message="Button has no accessible name.",
                    why="A button without a name leaves keyboard and assistive technology users guessing what it does.",
                    fix="Add concise visible text or an aria-label describing the action.",
                    bad_example="<button></button>",
                    good_example='<button type="button">Save changes</button>',
                    fix_type="add-button-text",
                )
            )

    # Maintainability: every id should be unique in the document.
    id_groups: defaultdict[str, list[Tag]] = defaultdict(list)
    for tag in soup.find_all(id=True):
        id_value = tag.get("id")
        if isinstance(id_value, str):
            id_groups[id_value].append(tag)
    for duplicate_id, tags in id_groups.items():
        if len(tags) > 1:
            for tag in tags[1:]:
                issues.append(
                    _issue(
                        rule="duplicate-id",
                        category="Structure",
                        severity="critical",
                        line=_tag_line(source, soup, tag),
                        message=f'ID "{duplicate_id}" is used more than once.',
                        why="Duplicate IDs break label relationships, fragment links, CSS selectors, and JavaScript queries.",
                        fix="Give each element a unique ID and update any for= or href=# references that point to it.",
                        bad_example='<section id="content"></section>\n<aside id="content"></aside>',
                        good_example='<section id="content"></section>\n<aside id="related-content"></aside>',
                        fix_type="rename-duplicate-id",
                    )
                )

    # Selected basic structure checks. These are teaching signals, not a full validator.
    if not re.search(r"<!doctype\s+html\s*>", source, re.I):
        issues.append(
            _issue(
                rule="missing-doctype",
                category="Structure",
                severity="warning",
                line=1 if source else None,
                message="Document is missing the HTML5 doctype.",
                why="The doctype asks browsers to use standards mode instead of legacy quirks mode.",
                fix="Put <!doctype html> at the very top of the document.",
                bad_example="<html>...</html>",
                good_example="<!doctype html>\n<html lang=\"en\">...</html>",
                fix_type="add-doctype",
            )
        )

    html_tag = soup.find("html")
    if html_tag and not html_tag.get("lang"):
        issues.append(
            _issue(
                rule="missing-language",
                category="Accessibility",
                severity="warning",
                line=_tag_line(source, soup, html_tag),
                message="HTML element is missing a lang attribute.",
                why="The language helps screen readers choose the correct pronunciation rules and helps translation tools.",
                fix="Add the primary document language, such as lang=\"en\", to the html element.",
                bad_example="<html>",
                good_example='<html lang="en">',
                fix_type="add-language",
            )
        )

    title = soup.find("title")
    if not title or not title.get_text(strip=True):
        issues.append(
            _issue(
                rule="missing-title",
                category="Structure",
                severity="warning",
                line=_source_line(source, "<head") or (_tag_line(source, soup, html_tag) if html_tag else 1 if source else None),
                message="Document is missing a descriptive title.",
                why="The title identifies the page in browser tabs, history, bookmarks, and assistive technology landmarks.",
                fix="Add a concise, descriptive title inside head.",
                bad_example="<head></head>",
                good_example="<head><title>Student dashboard</title></head>",
                fix_type="add-title",
            )
        )

    severity_counts = Counter(issue["severity"] for issue in issues)
    category_counts = Counter(issue["category"] for issue in issues)
    deductions = severity_counts["critical"] * 15 + severity_counts["warning"] * 8 + severity_counts["info"] * 3
    score = max(0, 100 - deductions)

    return {
        "issues": issues,
        "total": len(issues),
        "score": score,
        "score_label": "Based on detected checks only",
        "severity_counts": dict(severity_counts),
        "category_counts": dict(category_counts),
        "rules_checked": [
            "missing-alt",
            "missing-label",
            "empty-link",
            "empty-button",
            "duplicate-id",
            "missing-doctype",
            "missing-language",
            "missing-title",
        ],
    }
