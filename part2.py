import argparse
import socket
import asyncio

import requests
from dnslib import DNSRecord, QTYPE, DNSError, RR, A, CNAME


def query(name, qtype, upstream):
    params = {"name": name, "type": qtype}
    headers = {"accept": "application/dns-json"}
    response = requests.get(upstream, params=params, headers=headers, timeout=5)
    response.raise_for_status()
    return response.json()

def parse_query(data):
    try:
        request = DNSRecord.parse(data)
        name = str(request.q.qname)
        qtype = request.q.qtype
        return request, name, qtype
    except DNSError:
        return None

def build_response(request, answer):
    reply = request.reply()
    reply.header.aa = 0
    reply.header.rcode = answer["Status"]

    for record in answer.get("Answer", []):
        if record["type"] == 1:
            rdata = A(record["data"])
        elif record["type"] == 5:
            rdata = CNAME(record["data"])
        else:
            continue
        reply.add_answer(RR(record["name"], record["type"], rdata=rdata, ttl=record["TTL"]))

    return reply.pack()

async def handle_client(loop, skt, data, addr, upstream):
    parsed = parse_query(data)
    if parsed is None:
        return
    request, name, qtype = parsed

    try:
        answer = await asyncio.to_thread(query, name, qtype, upstream)
        reply_bytes = build_response(request, answer)

    except requests.RequestException:
        reply = request.reply()
        reply.header.aa = 0
        reply.header.rcode = 2
        reply_bytes = reply.pack()

    print(f"query {name} type {QTYPE[qtype]}, response {len(reply_bytes)} bytes")
    await loop.sock_sendto(skt, reply_bytes, addr)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=1053)
    parser.add_argument("--upstream", default="https://dns.google/resolve")
    return parser.parse_args()

async def main(port, upstream):
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(("127.0.0.1", port))
    skt.setblocking(False)
    print(f"listening on 127.0.0.1:{port}, forwarding to {upstream}")

    loop = asyncio.get_running_loop()

    while True:
        data, addr = await loop.sock_recvfrom(skt, 65535)
        if len(data) < 12:
            print(f"malformed packet from {addr}")
            continue

        asyncio.create_task(handle_client(loop, skt, data, addr, upstream))

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.port, args.upstream))