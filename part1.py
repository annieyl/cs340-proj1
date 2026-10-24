import argparse
import socket
import asyncio
import struct

#part 1
def forward(data, addr, upstream):
    for attempt in range(3):
        #send to upstream resolver
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as skt2:
            skt2.settimeout(5.0)
            try:
                skt2.sendto(data, (upstream, 53))
                data_response, _ = skt2.recvfrom(65535)
                return data_response
            except socket.timeout:
                print("timeout")
    print("failed after 3 retries.........")
    return None

async def handle_client(loop, skt, data, addr, upstream):
    name, qtype = parse_question(data)
    try:
        data_response = await asyncio.to_thread(forward, data, addr, upstream)
        print(f"query {name} of type {qtype} with length {len(data_response)}")
        await loop.sock_sendto(skt, data_response, addr)
    except Exception as e:
        print(f"error:{e}")

def parse_question(data):
    types = {1: "A", 2: "NS", 5: "CNAME", 6: "SOA", 12: "PTR", 15: "MX",
             16: "TXT", 28: "AAAA", 33: "SRV", 65: "HTTPS", 255: "ANY"}
    try:
        pos = 12
        labels = []
        while True:
            length = data[pos]
            if length == 0:
                pos += 1
                break
            if length & 0xC0:
                return None
            labels.append(data[pos + 1:pos + 1 + length].decode("ascii", "replace"))
            pos += 1 + length
        qtype, = struct.unpack("!H", data[pos:pos + 2])
        return ".".join(labels) or ".", types.get(qtype, str(qtype))
    except (IndexError, struct.error):
        return None

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=1053)
    parser.add_argument("--upstream", default="8.8.8.8")
    return parser.parse_args()

async def main(port, upstream):
    #make udp socket
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(("127.0.0.1", port))
    skt.setblocking(False)
    print(f"listening on 127.0.0.1:{port}, forwarding to {upstream}:53")

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