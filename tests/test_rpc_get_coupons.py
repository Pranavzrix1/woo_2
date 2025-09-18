# tests/test_rpc_get_coupons.py
import os
import json
import requests
import pytest

# Optional: load .env if you rely on it (python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

PRODUCT_ENDPOINT = os.getenv("PRODUCT_ENDPOINT")
REQUEST_TIMEOUT = 10  # seconds

# Candidate JSON-RPC method names to try (primary first)
CANDIDATE_METHODS = [
    "get_coupons",
    "getCoupons",
    "coupons",
    "get_all_coupons",
]

JSONRPC_TEMPLATE = lambda method: {
    "jsonrpc": "2.0",
    "method": method,
    "params": {},
    "id": 1
}


def _try_rpc(method: str):
    """Send JSON-RPC POST to PRODUCT_ENDPOINT for given method."""
    if not PRODUCT_ENDPOINT:
        raise RuntimeError("PRODUCT_ENDPOINT not set in environment or .env")

    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = JSONRPC_TEMPLATE(method)
    try:
        r = requests.post(PRODUCT_ENDPOINT, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        return {"error": "network", "exc": exc, "method": method, "response": None}

    # Try to parse JSON response if any
    parsed = None
    try:
        parsed = r.json()
    except Exception:
        parsed = None

    return {"status_code": r.status_code, "method": method, "response_raw": r.text, "response_json": parsed}


def _pretty_print_result(res):
    print("\n--- RPC Attempt ---")
    print("Method:", res.get("method"))
    print("HTTP status:", res.get("status_code"))
    print("Response JSON (truncated):")
    if res.get("response_json") is not None:
        try:
            print(json.dumps(res["response_json"], indent=2)[:2000])
        except Exception:
            print(str(res["response_json"])[:2000])
    else:
        print(res.get("response_raw")[:2000])


def test_rpc_get_coupons_responds():
    """
    Try a few JSON-RPC method names against PRODUCT_ENDPOINT and assert at least one returns a valid JSON-RPC result.
    Successful JSON-RPC response considered:
      - HTTP status 200 and JSON body with either "result" (preferred) or "error" (still informative).
    """
    if not PRODUCT_ENDPOINT:
        pytest.skip("PRODUCT_ENDPOINT not set. Set PRODUCT_ENDPOINT in your environment or .env and re-run tests.")

    successes = []
    failures = []

    for method in CANDIDATE_METHODS:
        res = _try_rpc(method)
        _pretty_print_result(res)

        # Basic heuristics for "worked"
        if res.get("status_code") == 200 and isinstance(res.get("response_json"), dict):
            body = res["response_json"]
            if "result" in body:
                successes.append((method, "result", body["result"]))
                break  # prefer first with result
            elif "error" in body:
                # record error as info (authentication / method-not-found etc.)
                failures.append((method, "jsonrpc_error", body["error"]))
            else:
                failures.append((method, "200_no_jsonrpc_fields", body))
        else:
            failures.append((method, "http_or_parse_failure", res.get("status_code"), res.get("response_raw")[:400]))

    print("\n--- Summary ---")
    print("Successes:", len(successes))
    print("Failures (examples):")
    for f in failures[:6]:
        print(" ", f)

    assert successes, (
        "None of the JSON-RPC methods returned a JSON-RPC 'result'. "
        "See printed output for details. Tried PRODUCT_ENDPOINT: %s" % PRODUCT_ENDPOINT
    )

    # Optional: perform light assertions on returned result shape (if you expect certain fields)
    # Example if you expect list of coupons:
    method, kind, payload = successes[0]
    assert kind == "result"
    assert payload is not None
    # If you expect a list of coupons:
    # assert isinstance(payload, list), "Expected JSON-RPC result to be a list of coupons"
    # If you expect objects with 'code' / 'amount', you can assert below:
    # if isinstance(payload, list) and payload:
    #     assert isinstance(payload[0], dict)
    #     assert "code" in payload[0]
