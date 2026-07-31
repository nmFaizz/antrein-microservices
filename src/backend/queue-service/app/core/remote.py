import httpx


def extract_message(response: httpx.Response, fallback: str) -> str:
    """Extract the `message` field from another service's response envelope."""
    try:
        return response.json().get("message") or fallback
    except ValueError:
        return fallback
