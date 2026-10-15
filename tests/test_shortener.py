import json
import sys
import time
import urllib.request

BASE = "http://localhost:8000"


def request_json(method: str, url: str, payload: dict | None = None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            return resp.status, body
    except Exception as exc:  # pragma: no cover
        print(f"Request failed: {method} {url} -> {exc}")
        raise


def main() -> None:
    try:
        status, _ = request_json("GET", f"{BASE}/health")
        print(f"API health: {status}")

        status, body = request_json(
            "POST",
            f"{BASE}/api/v1/urls/shorten",
            {"original_url": "https://example.com", "alias": "example"},
        )
        print(f"Create short URL: {status} {body}")

        status, _ = request_json("GET", f"{BASE}/api/v1/urls/example")
        print(f"Redirect short URL: {status}")

        status, body = request_json("GET", f"{BASE}/api/v1/analytics/summary")
        print(f"Analytics summary: {status} {body}")
        print("SMOKE_OK")
    except Exception:
        print("SMOKE_FAIL")
        sys.exit(1)


if __name__ == "__main__":
    time.sleep(2)
    main()
