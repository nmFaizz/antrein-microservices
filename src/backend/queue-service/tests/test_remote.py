import httpx

from app.core.remote import extract_message


def test_extract_message_from_envelope():
    response = httpx.Response(
        409,
        json={
            "success": False,
            "data": None,
            "message": "Current time is outside the configured operating hours",
        },
    )
    assert (
        extract_message(response, "fallback")
        == "Current time is outside the configured operating hours"
    )


def test_extract_message_empty_message_falls_back():
    response = httpx.Response(500, json={"success": False, "data": None, "message": ""})
    assert extract_message(response, "fallback") == "fallback"


def test_extract_message_non_json_falls_back():
    response = httpx.Response(502, text="<html>bad gateway</html>")
    assert extract_message(response, "fallback") == "fallback"
