users = {}

import _thread
import sys
import socket, select
import os
import time

os.system('clear')
host_name = socket.gethostname()
host_ip = "192.168.1.38"

PORT = 12345

## [<PacketId>,<data>]
class TCP:
    def __init__(self):
        self.PACKET_SIZE = 1500
        self.MAXID = 1000
        _thread.start_new_thread(self.receiver, () )
    
    def send_file(self, ip, path):
        headers = "[" + host_ip + ",file_transfer," + path.split("/")[-1] + ","
        with open( path, "rb" ) as f:
            packet_index = -1 
            while True:
                header_with_index = headers+str(packet_index+1) + ","
                chunk_size = self.PACKET_SIZE-len(str.encode(header_with_index+"]"))
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                packet_index += 1
                self.sender(ip, str.encode(header_with_index)+chunk+str.encode("]"))

    def sender(self, ip, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (ip, PORT))

    def receiver(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', PORT))
        sock.setblocking(False)
        while True:
            result = select.select([sock],[],[])
            msg = result[0][0].recv(self.PACKET_SIZE).decode('ascii')
            msgdata = msg.split(",")
            if len(msgdata) > 4 and  msgdata[1] == "file_transfer":
                filename = msgdata[2]
                index = msgdata[3]
                self.sender(msgdata[0][1:],str.encode("received"+ str(index)))
                data = str.encode("".join(msgdata[4:])[:-1])
                print("index ", index, "arrived")
                with open( filename, "wb+" ) as destination:
                    destination.write( data )
            else:
                print(msg)


tcp_over_udp = TCP()

target_ip = "192.168.1.37"
while True:
    path = input("EXIT or message:")
    if path == "exit":
        exit(0)
    else:
        tcp_over_udp.send_file(target_ip, path)