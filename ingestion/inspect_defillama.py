import requests


URL = "https://api.llama.fi/protocols"

response = requests.get(URL, timeout=30)

print(f"Status code: {response.status_code}")

response.raise_for_status()

protocols = response.json()

print(f"Number of protocols: {len(protocols)}")

first_protocol = protocols[0]

print("\nFields:")
for field in first_protocol:
    print(f"  - {field}")

print("\nFirst protocol:")
for key, value in first_protocol.items():
    print(f"{key}: {value}")