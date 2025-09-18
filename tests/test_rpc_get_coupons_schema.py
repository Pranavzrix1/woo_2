# tests/test_rpc_get_coupons_schema.py
import os
import json
import requests
import pytest
from datetime import datetime

# Optional dotenv loader
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

PRODUCT_ENDPOINT = os.getenv("PRODUCT_ENDPOINT")
REQUEST_TIMEOUT = 10

CANDIDATE_METHOD = "get_coupons"
JSONRPC_PAYLOAD = {
    "jsonrpc": "2.0",
    "method": CANDIDATE_METHOD,
    "params": {},
    "id": 1
}

def _post_rpc():
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    r = requests.post(PRODUCT_ENDPOINT, json=JSONRPC_PAYLOAD, headers=headers, timeout=REQUEST_TIMEOUT)
    try:
        body = r.json()
    except Exception:
        body = None
    return r.status_code, body, r.text

def _is_iso_date(s: str) -> bool:
    # try a few common formats; adapt if your endpoint uses different format
    if s is None:
        return True
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            datetime.strptime(s, fmt)
            return True
        except Exception:
            continue
    return False

def test_rpc_get_coupons_schema():
    if not PRODUCT_ENDPOINT:
        pytest.skip("PRODUCT_ENDPOINT not set in environment / .env")

    status, body, raw = _post_rpc()
    print("HTTP status:", status)
    print("Response (truncated):", json.dumps(body, indent=2)[:1500] if isinstance(body, dict) else raw[:1500])

    assert status == 200, f"Expected 200 from RPC endpoint, got {status}. Raw: {raw[:800]}"
    assert isinstance(body, dict), f"Response body not JSON object: {raw[:800]}"
    assert "result" in body, f"JSON-RPC response missing 'result' field: {body}"
    result = body["result"]
    assert isinstance(result, list), f"'result' expected to be a list, got {type(result)}"

    # expected keys
    expected_keys = {"id", "code", "amount", "discount_type", "description", "date_expires", "usage_count"}
    for i, item in enumerate(result):
        assert isinstance(item, dict), f"coupon at index {i} is not an object: {item}"
        missing = expected_keys - set(item.keys())
        assert not missing, f"coupon at index {i} missing keys: {missing}"
        # type checks
        assert isinstance(item["id"], int), f"id should be int at index {i}"
        assert isinstance(item["code"], str) and item["code"].strip(), f"code should be non-empty str at index {i}"
        assert isinstance(item["amount"], (str, float, int)), f"amount should be str/num at index {i}"
        assert isinstance(item["discount_type"], str) and item["discount_type"].strip(), f"discount_type missing at index {i}"
        assert isinstance(item["usage_count"], int), f"usage_count should be int at index {i}"
        # date_expires can be null or a parsable date
        date_val = item.get("date_expires")
        if date_val is not None:
            assert isinstance(date_val, str), f"date_expires should be string or null at index {i}"
            assert _is_iso_date(date_val), f"date_expires at index {i} not in supported formats: {date_val}"
