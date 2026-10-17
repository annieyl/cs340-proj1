import socket
import asyncio

#part 1

async def handle_client(skt,data,addr):
    data_response = await asyncio.to_thread(forward,data)
    skt.sendto(data_response,addr)

def forward(data,addr):
    #send to upstream 8.8.8.8 
    skt2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    skt2.sendto(data, ('8.8.8.8', 53))
    data_response,_ = skt2.recvfrom(53,65535)
    print(f"data from google:{data}, addr receipt:{addr}")
    
    return data_response

async def main():
    try:
        #make udp socket
        skt = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        skt.bind(("127.0.0.1", 1053))
        skt.setblocking(False)

        loop=asyncio.get_running_loop()
        
        print(f"received data:{data}, receivedaddr:{addr}")
        
        while True:
            data, addr = skt.recvfrom(65535)
            asyncio.create_task(handle_client(skt,data,addr)) 
        
    except:
        pass

if __name__ == "__main__":
    asyncio.run((main)) 



#tcp socket
# skt = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
