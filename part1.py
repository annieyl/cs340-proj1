import socket
import asyncio

#part 1

def receive(skt):
    data, addr = skt.recvfrom(65535)
    print(f"received data:{data}, receivedaddr:{addr}")
    return data, addr, skt

async def forward(data,addr):
    #send to upstream 8.8.8.8 
    skt2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    skt2.sendto(data, ('8.8.8.8', 53))
    data_response,addr_response = skt2.recvfrom(53)
    print(f"data from google:{data}, addr receipt:{addr}")
    return data_response, addr_response

# async def response(data_response,addr,skt):
#     #map it back to request
#     skt.sendto(data_response,addr)

# while True:
#     pass

async def main():
    try:
        #make udp socket
        skt = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        skt.bind(("127.0.0.1", 1053))
        data,addr,skt = receive(skt)

        data_response, _ = asyncio.to_thread(forward(data,addr))
        


        skt.sendto(data_response,addr)
        
    except:
        pass


asyncio.run((main))



#tcp socket
# skt = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
