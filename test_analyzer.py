import json

import pytest

from analyzer import MAX_HTML_LENGTH, analyze_html
from app import app


def rules(result):
    return {issue["rule"] for issue in result["issues"]}


def test_missing_alt_and_line_number():
    result = analyze_html("<!doctype html>\n<img src=\"student.jpg\">\n")
    assert "missing-alt" in rules(result)
    issue = next(item for item in result["issues"] if item["rule"] == "missing-alt")
    assert issue["line"] == 2
    assert issue["category"] == "Accessibility"


def test_labeled_controls_are_not_flagged_but_unlabeled_are():
    html = '<label for="name">Name</label>\n<input id="name">\n<textarea aria-label="Notes"></textarea>\n<select></select>'
    result = analyze_html(html)
    assert "missing-label" in rules(result)
    assert sum(item["rule"] == "missing-label" for item in result["issues"]) == 1
    assert next(item for item in result["issues"] if item["rule"] == "missing-label")["line"] == 4


def test_empty_links_and_buttons():
    result = analyze_html('<a href="/profile"></a>\n<button></button>')
    assert "empty-link" in rules(result)
    assert "empty-button" in rules(result)
    assert next(item for item in result["issues"] if item["rule"] == "empty-link")["line"] == 1
    assert next(item for item in result["issues"] if item["rule"] == "empty-button")["line"] == 2


def test_duplicate_ids_report_each_duplicate_after_first():
    result = analyze_html('<div id="content"></div>\n<aside id="content"></aside>\n<footer id="content"></footer>')
    duplicate_issues = [item for item in result["issues"] if item["rule"] == "duplicate-id"]
    assert len(duplicate_issues) == 2
    assert {item["line"] for item in duplicate_issues} == {2, 3}


def test_title_and_structural_rules():
    result = analyze_html("<html><head></head><body></body></html>")
    assert {"missing-title", "missing-doctype", "missing-language"}.issubset(rules(result))
    assert result["score"] < 100


def test_clean_document_scores_full_marks_for_implemented_checks():
    html = '<!doctype html>\n<html lang="en"><head><title>Profile</title></head><body><main><img alt="Profile photo" src="x.jpg"><label for="email">Email</label><input id="email"><a href="/home">Home</a><button type="button">Save</button></main></body></html>'
    result = analyze_html(html)
    assert result["total"] == 0
    assert result["score"] == 100
    assert result["severity_counts"] == {}


def test_empty_and_malformed_html_are_safe():
    assert analyze_html("\n")["total"] == 0
    result = analyze_html("<div><img src='x'><span>")
    assert isinstance(result["issues"], list)
    assert "missing-alt" in rules(result)


def test_size_limit_is_enforced():
    with pytest.raises(ValueError):
        analyze_html("x" * (MAX_HTML_LENGTH + 1))


def test_api_validation_and_json_shape():
    client = app.test_client()
    assert client.get("/health").status_code == 200
    manifest = client.get("/manus-routes.json")
    assert manifest.status_code == 200
    assert manifest.get_json()["routes"][0]["path"] == "/"
    assert client.post("/api/analyze", data="not-json").status_code == 415
    response = client.post("/api/analyze", json={"html": "<img>"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] >= 1
    assert "score_label" in data


def test_api_rejects_oversized_input():
    client = app.test_client()
    response = client.post("/api/analyze", json={"html": "x" * (MAX_HTML_LENGTH + 1)})
    assert response.status_code == 413
