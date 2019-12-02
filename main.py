users = {}
from config import *
from tcp import TCP

# def send_message( host_name, target_ip, message ):
#     import socket
#     response_message = '[' + host_name + ',' + host_ip + ',message,' + message + ']'
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((target_ip,12345))
    #     s.sendall(str.encode(response_message))

def announcement_listener(host_name, host_ip, tsocket ):
    import select, socket
    import time
    import _thread
    global users

    bufferSize = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', UDP_PORT))
    s.setblocking(False)
    while True:
        result = select.select([s],[],[])
        msg = result[0][0].recv(bufferSize).decode('ascii')
        usr, ip, tp = msg.split(',')
        usr = usr.strip()[1:]
        tp = tp.strip()[:-1]
        ip = ip.strip()
        if tp.strip() == 'announce' and ip != host_ip:
            if (usr not in users) or (usr in users and time.time()-users[usr][1] > 5):
                users[usr] = (ip,time.time())
                response_message = '[' + host_name + ',' + host_ip + ',response]'
                tsocket.send( ip, str.encode(response_message) )

def tcp_listener(host_ip, dataStream):
    import socket
    import time
    global users

    while True:
        data = dataStream.get(block=True)
        if len(data) < 3:
            print("unsupported message type")
        elif data[2].strip() == 'response':
            if (data[0].strip() not in users) or (data[0].strip() in users and time.time()-users[data[0].strip()][1] > 5):
                users[data[0].strip()] = (data[1].strip(),time.time())
        elif data[2].strip() == 'message':
            print(data[0].strip() + ": " + data[3].strip())
        print(data.decode('ascii'))    


import _thread
import sys
import socket
import os
import queue
import time

os.system('clear')
username = input("Enter your username: ")
host_ip = HOST_IP
listenerQueue = queue.Queue()
tsocket = TCP( listenerQueue )

try:
    _thread.start_new_thread( announcement_listener, ( username, host_ip, tsocket, ) )
    _thread.start_new_thread( tcp_listener, (host_ip, listenerQueue,  ) )
except:
    print ("Error: unable to start thread")

announce_message = '[' + username + ',' + host_ip + ',announce]'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
print("Broadcasting...")
for _ in range(3):
    sock.sendto(str.encode(announce_message),('<broadcast>',UDP_PORT))

while True:
    command = input("Enter command(exit, list, message): \n")
    if command == 'exit':
        break
    if command == 'list':
        print( list(users.keys()) )
    elif 'message' in command:
        cmd = command.split(" ")
        _thread.start_new_thread( send_message , ( username, users[cmd[1].strip()][0] , cmd[2].strip() , ) )

