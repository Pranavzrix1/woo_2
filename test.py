import requests
import json

# Test the endpoint directly
response = requests.post(
    "https://newscnbnc.webserver9.com/wp-json/mcp/v1/rpc",
    json={
        "jsonrpc": "2.0",
        "method": "get_products", 
        "params": {},
        "id": 1
    },
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    data = response.json()
    print("Full Response:")
    print(json.dumps(data, indent=2))
    
    # Show first product's fields
    if "result" in data and data["result"]:
        first_product = data["result"][0]
        print("\n" + "="*50)
        print("FIELDS IN FIRST PRODUCT:")
        print("="*50)
        for key, value in first_product.items():
            print(f"{key}: {type(value).__name__} = {value}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)

