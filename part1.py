import socket
import asyncio
import struct

#part 1
def forward(data,addr):
    for attempt in range(3):
        #send to upstream 8.8.8.8 
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as skt2:
            skt2.settimeout(5.0)
            try:
                skt2.sendto(data, ('8.8.8.8', 53))
                data_response,_ = skt2.recvfrom(65535)
                return data_response
            except socket.timeout:
                print(f"timeout")
        # print(f"data from google:{data_response}, addr receipt:{addr}")
    print("failed after 3 retries.........")
    return None
 

async def handle_client(loop,skt,data,addr):
    name, qtype = parse_question(data)
    try:
        data_response = await asyncio.to_thread(forward,data,addr)
        print(f"query {name} of type {qtype} with length {len(data_response)}")
        await loop.sock_sendto(skt,data_response,addr)
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

async def main():
    #make udp socket
    skt = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    skt.bind(("127.0.0.1", 1053))
    skt.setblocking(False)

    loop=asyncio.get_running_loop()

    while True:
        data, addr = await loop.sock_recvfrom(skt,65535)
        if len(data) < 12:
            print(f"malformed packet from {addr}")
            continue

        asyncio.create_task(handle_client(loop,skt,data,addr)) 

if __name__ == "__main__":
    asyncio.run(main()) 


#tcp socket
# skt = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
