import socket
import sys
import pickle


#python 3
# code list: 
# 000: invalid command
# 001: connection request
# 100: user name confirm, please enter password
# 101: new user, please enter password
# 102: unvalid password
# 103: login successfully
# 104: already login
# 105: successfully exit
# 106: thread title exist
# 107: thread title created
# 108: incorrect syntax
# 109: thread title do not exist
# 110: post successed
# 111: user cannot delete message
# 112: successfully deleted message
# 113: successfully edited
# 114: content transmission successed
# 115: no thread
# 116: thread list
# 117: Thread cannot be removed
# 118: Thread removed successfully
# 119: ready to upload
# 120: file existed
# 121: ready to download
# 122: file do not exist


server = '127.0.0.1'
SER_PORT = int(sys.argv[1])
ADDRESS = (server,SER_PORT)
conn = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

def sendMs(message):
    global conn
    message = message.encode()
    conn.sendto(message,ADDRESS)
def recvM():
    global conn
    data=conn.recvfrom(1024)
    return data[0]


#login process
sendMs('001')
port = recvM()
port = int(port.decode())
ADDRESS=(server,port) # set new port number
conn.connect(ADDRESS)
while True:
    message = input("Enter username: ")
    sendMs(message)
    data = recvM()
    recvMess = data.decode()
    if(recvMess=='100'):
        message = input("Enter password: ")
    elif(recvMess == '101'):
        message = input("New user, enter password: ")
    elif(recvMess == '104'):
        print(f'{message} has already logged in')
        continue
    sendMs(message)
    data = recvM()
    recvMess = data.decode()
    if(recvMess == '102'):
        print('Invalid password')
        continue
    elif(recvMess=='103'):
        print('Welcome to the forum')
        break

#other operation
while True:
    message = input("Enter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT: ")
    sendMs(message)
    data = recvM()
    recvMess = data.decode()

    if(recvMess =='105'):
        print('Goodbye')
        break
    elif(recvMess == '106'):
        tit = message.split()[1]
        print(f"Thread {tit} exists")
        continue
    elif(recvMess == '107'):
        tit = message.split()[1]
        print(f"Thread {tit} created")
        continue
    elif(recvMess == '000'):
        print('Invalid command')
        continue
    elif(recvMess == '109'):
        message = message.split()
        print(f'Thread {message[1]} do not exsist')
        continue
    elif(recvMess == '110'):
        message = message.split()
        print(f'Message posted to {message[1]} thread')
        continue
    elif(recvMess == '111'):
        print('The message belongs to another user and cannot be edited')
    elif(recvMess == '112'):
        print('The message has been deleted')
    elif(recvMess == '113'):
        print('The message has been edited')
    elif(recvMess == '114'):
        data = conn.recv(1024)
        words = pickle.loads(data)
        for w in words:
            print(str(w),end='')
    elif(recvMess == '108'):
        message = message.split()
        print(f'Incorrect syntax for {message[0]}')
    elif(recvMess == '115'):
        print('No threads to list')
    elif(recvMess == '116'):
        data = conn.recv(1024)
        lists = pickle.loads(data)
        print('The list of active threads:')
        for i in lists:
            print(i[:-4])
    elif(recvMess == '117'):
        print('Thread cannot be removed')
    elif(recvMess == '118'):
        print('Thread removed')
    elif(recvMess =='119'):
        message = message.split()
        filename = message[2]
        tcpSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        tcpSock.connect(ADDRESS)
        try:
            with open(filename,'rb') as f:
                while True:
                    data = f.read(1024)
                    if len(data)==0:
                        break
                    tcpSock.send(data)
            print(f'{filename} uploaded to {message[1]} thread')
            tcpSock.close()
        except:
            print(f'{filename} is not existed')
            tcpSock.close()
    elif(recvMess == '120'):
        message = message.split()
        print(f'file {message[2]} is already existed')
    elif(recvMess == '121'):
        message = message.split()
        filename = message[2]
        tcpSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        tcpSock.connect(ADDRESS)
        with open(filename,'wb') as f:
            while True:
                data = tcpSock.recv(1024)
                if not data:
                    break
                f.write(data)
        tcpSock.close()
        print(f'{filename} successfully downloaded')
    elif(recvMess == '122'):
        message = message.split()
        filename = message[2]
        print(f'{filename} do not exist')