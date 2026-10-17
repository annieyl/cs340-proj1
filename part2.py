import socket
import asyncio

import json
import requests 


DOH_URL = "https://dns.google/resolve"

def query(name, qtype):
    params = {"name": name, "type": qtype}
    response = requests.get(DOH_URL, params=params, timeout=5)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    answer = query("github.com", "A")
    print(json.dumps(answer, indent=2))

    for record in answer.get("Answer", []):
        print(record["type"], record["data"])
