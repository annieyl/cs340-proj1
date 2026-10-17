import socket
import asyncio
import struct

#part 1
def forward(data,addr):
    #send to upstream 8.8.8.8 
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as skt2:
        skt2.settimeout(5.0)
        skt2.sendto(data, ('8.8.8.8', 53))
        data_response,_ = skt2.recvfrom(65535)
    print(f"data from google:{data}, addr receipt:{addr}")
    return data_response


async def handle_client(loop,skt,data,addr):
    data_response = await asyncio.to_thread(forward,data,addr)
    await loop.sock_sendto(skt,data_response,addr)


async def main():
    try:
        #make udp socket
        skt = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        skt.bind(("127.0.0.1", 1053))
        skt.setblocking(False)

        loop=asyncio.get_running_loop()
        
        while True:
            data, addr = await loop.sock_recvfrom(skt,65535)
            if len(data) < 12:
                raise ValueError("malformed data")

            #retries
            for attempt in range(3):
                try: 
                    asyncio.create_task(handle_client(loop,skt,data,addr)) 
                    print(f"received data:{data}, receivedaddr:{addr}")
                except asyncio.TimeoutError as e:
                    if attempt < 4:
                        print("retrying...")
                    else:
                        print(f"failure :(")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main()) 


#tcp socket
# skt = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
