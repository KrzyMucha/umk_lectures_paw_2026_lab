import json
import os
import urllib.error
import urllib.request

BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8080").rstrip("/")


def request_json(path: str, method: str = "GET", payload: dict | None = None, expected_status: int = 200):
    url = f"{BASE_URL}{path}"
    body = None
    headers = {}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, method=method, data=body, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = response.getcode()
            raw_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        status = error.code
        raw_body = error.read().decode("utf-8")
        # Detect common DB authentication error in HTML/error body and raise clearer message
        if 'password authentication failed for user' in raw_body:
            raise AssertionError( 
                "Service returned DB authentication error (password authentication failed for user).\n"
                "Check that the service's DATABASE_URL / DB_* environment variables and CI secrets are correct."
            )
    except urllib.error.URLError as error:
        raise AssertionError(f"Request to {url} failed: {error}") from error

    assert status == expected_status, f"Expected HTTP {expected_status} for {url}, got {status}, body={raw_body}"

    try:
        return json.loads(raw_body)
    except json.JSONDecodeError as error:
        raise AssertionError(f"Response from {url} is not valid JSON") from error
