import socket
import sys
import pickle
from threading import Thread
import os
import random




#python3
# code list: 
# 002: client message recived
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
# 111: user cannot edit message
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


portN=[]
online = []
command =[] #address and command

class ClientThread(Thread):
    def __init__(self, clientAddress,port,server):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.port = port
        self.serverSocket = server
        self.clientAlive = False
        self.logined = False
        self.name = ''
        self.title =''
        self.clientAlive = True

#function of send message

    def recvM(self):
        recvMess = self.serverSocket.recvfrom(1024)
        message = recvMess[0]
        return message 
    def sendM(self,message):
        message = message.encode()
        self.serverSocket.sendto(message,self.clientAddress)
        # while True:
        #     try:
        #         server.settimeout(5) #wait for 5 seconds
        #         m = self.recvM()
        #         break
        #     except:
        #         print('Time out, retransmit packet!')
        #         self.serverSocket.sendto(message,self.clientAddress)
    def login(self):
        global online
        name = ''
        password = ''
        data = self.recvM()
        name = data.decode()
        mark = True
        with open('credentials.txt','a+') as f:
            f.seek(0)
            nP = f.readlines()
            for n in nP:
                if (name == n.split()[0]):
                    if name in online:
                        self.sendM('104')
                        print(f'{name} has already logged in')
                        return False
                    self.sendM('100')
                    data = self.recvM()
                    password = data.decode()
                    if password == n.split()[1]:
                        self.sendM('103')
                        self.logined = True
                        self.name = name
                        print(f'{self.name} successful login')
                        online.append(self.name)
                        return mark
                    else:
                        self.sendM('102')
                        print('Incorrect password')
                        mark = False
                        return mark
            if mark:
                self.sendM('101')
                print('New user')
                data = self.recvM()
                password = data.decode()
                f.write(f'{name} {password} \n')
                self.name = name
                self.logined = True
                self.sendM('103')
                print(f'{self.name} successfully logged in')
                online.append(self.name)
        print(len(online))
        return mark
    def userExit(self):
        global online
        global portN
        self.clientAlive = False
        online.remove(self.name)
        portN.remove(self.port)
        print(f"{self.name} exited")
        self.sendM('105')
    def createT(self,title):
        Ttitle = os.listdir('./titles/')
        if title +'.txt' in Ttitle:
            self.sendM('106')
            print(f'Thread {title} exists')
            return False
        Ttitle.append(title)
        with open('titles/'+title+'.txt','a+') as f:
            f.write(f'{self.name}\n')
        self.sendM('107')
        print(f'Thread {title} created')
        return True
    def msgT(self,title,words):
        Ttitle = os.listdir('./titles/')
        if title+'.txt' not in Ttitle:
            self.sendM('109')
            print(f"Thread {title} do not exsist")
            return False
        with open('titles/'+title+'.txt','a+') as f:
            f.seek(0)
            content = f.readlines()
            number = self.findN(content[1:])+1
            string = ' '.join(words)
            string = f'{number} ' + f'{self.name}: ' + string +'\n'
            f.write(string)
        self.sendM('110')
        print(f'Message posted to {title} thread')
        return True
    def deleteM(self, title,number):
        Ttitle = os.listdir('./titles/')
        if title+'.txt' not in Ttitle:
            self.sendM('109')
            print(f"Thread {title} do not exsist")
            return False
        name=''
        words=[]
        with open('titles/'+title+'.txt','r') as f:
            content = f.readlines()
            name = content[0]
            content = content[1:]
            words.append(name)
            index = 1
            for m in content:
                r = m.split()
                if r[1] == 'uploaded':
                    words.append(m)
                elif r[0]!=str(number):
                    words.append(str(index)+m[1:])
                    index+=1
                else:
                    user = m.split()[1]
                    if user[:-1] != self.name:
                        self.sendM('111')
                        print(f'Message cannot be deleted')
                        return False
        with open('titles/'+title+'.txt','w+') as f:
            for m in words:
                f.write(str(m))
            self.sendM('112')
            print('Message has been deleted')         
    def editM(self,title,number,message):
        Ttitle = os.listdir('./titles/')
        if title+'.txt' not in Ttitle:
            self.sendM('109')
            print(f"Thread {title} do not exsist")
            return False
        name=''
        words=[]
        string = ' '.join(message)
        with open('titles/'+title+'.txt','r') as f:
            content = f.readlines()
            name = content[0]
            content = content[1:]
            words.append(name)
            for m in content:
                if m[1] == 'uploaded':
                    words.append(m)
                elif m[0]!=str(number):
                    words.append(m)
                else:
                    index = m.split()[0]
                    user = m.split()[1]
                    if user[:-1] != self.name:
                        self.sendM('111')
                        print(f'Message cannot be deleted')
                        return False
                    else:
                        words.append(index+' '+user+' '+string+'\n')
        with open('titles/'+title+'.txt','w+') as f:
            for m in words:
                f.write(str(m))
            self.sendM('113')
            print('Message has been edited')
    def readT(self,title):
        Ttitle = os.listdir('./titles/')
        if title+'.txt' not in Ttitle:
            self.sendM('109')
            print(f"Thread {title} do not exsist")
            return False
        words=[]
        with open('titles/'+title+'.txt','r') as f:
            content = f.readlines()
            content = content[1:]
            for m in content:
                words.append(m)
        self.sendM('114')
        data = pickle.dumps(words)
        self.serverSocket.sendto(data,self.clientAddress)
        print(f'Thread {title} read')
    def listT(self):
        Ttitle = os.listdir('./titles/')
        if len(Ttitle) == 0:
            self.sendM('115')
            return False
        self.sendM('116')
        data = pickle.dumps(Ttitle)
        self.serverSocket.sendto(data,self.clientAddress)
    def removeT(self,title):
        Ttitle = os.listdir('./titles/')
        if title+'.txt' not in Ttitle:
            self.sendM('109')
            print(f"Thread {title} do not exsist")
            return False
        name= ''
        with open('titles/'+title+'.txt','r') as f:
            content = f.readlines()
            name = content[0][:-1]
        if name!=self.name:
            self.sendM('117')
            print(f'Thread {title} cannot be removed')
            return False
        os.remove('titles/'+title+'.txt')
        self.sendM('118')
        print(f'Thread {title} removed')
    def findN(self,words):#find number of messages of thread
        number=0
        for w in words:
            r=w.split()
            if(r[1]=='uploaded'):
                continue
            else:
                number+=1
        return number
    def upF(self,title,filename):
        Ttitle = os.listdir('./titles/')
        if title+'.txt' not in Ttitle:
            self.sendM('109')
            print(f"Thread {title} do not exsist")
            return False
        files = os.listdir('./uploadF/')
        if title+'-'+filename in files:
            self.sendM('120')
            print(f"File {filename} exsists")
            return False

        self.sendM('119') # ready to receive file
        tcpSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        tcpSock.bind(('127.0.0.1',self.port))
        tcpSock.listen()
        csocket,caddr = tcpSock.accept()

        with open('uploadF/'+title+'-'+filename,'wb') as f:
            while True:
                data = csocket.recv(1024)
                if not data:
                    break
                f.write(data)

        tcpSock.close()
        print(f'{self.name} uploaded file {filename} to {title} thread')
        with open('titles/'+title+'.txt','a+') as f:
            string = f'{self.name} uploaded {filename}\n'
            f.write(string)

    def dwnF(self,title,filename):
        Ttitle = os.listdir('./titles/')
        if title+'.txt' not in Ttitle:
            self.sendM('109')
            print(f"Thread {title} do not exist")
            return False
        files = os.listdir('./uploadF/')
        if title+'-'+filename not in files:
            self.sendM('122')
            print(f"File {filename} do not exist")
            return False
        
        self.sendM('121')
        tSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        tSock.bind(('127.0.0.1',self.port))
        tSock.listen(5)
        cket,ca = tSock.accept()
        
        with open('uploadF/'+title+'-'+filename,'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                cket.send(data)

        print(f'{filename} downloaded from {title} thread')
        tSock.close()
    
        


    def run(self):
        global online
        print('Client authenticating')
        while(self.login()==False):
            continue
        message = ''
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.recvM()
            message = data.decode()
            message = message.split()
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            
            if message[0] == 'XIT':
                self.userExit()
                break
            elif message[0] == 'CRT':
                if (len(message)!=2):
                    self.sendM('108')
                    continue
                print(f'{self.name} issued {message[0]} command')
                title = message[1]
                self.createT(title)
            elif message[0] == 'MSG':
                if(len(message)<=2):
                    self.sendM('108')
                    continue
                print(f'{self.name} issued {message[0]} command')
                self.msgT(message[1],message[2:])
            elif message[0] == 'DLT':
                if(len(message)!=3):
                    self.sendM('108')
                    continue
                print(f'{self.name} issued {message[0]} command')
                self.deleteM(message[1],message[2])
            elif message[0] == 'EDT':
                if(len(message)<4):
                    self.sendM('108')
                    continue
                print(f'{self.name} issued {message[0]} command')
                self.editM(message[1],message[2],message[3:])
            elif message[0] == 'RDT':
                if(len(message)!=2):
                    self.sendM('108')
                    continue
                print(f'{self.name} issued {message[0]} command')
                self.readT(message[1])
            elif message[0] == 'LST':
                if (len(message)!=1):
                    self.sendM('108')
                    continue
                print(f'{self.name} issued {message[0]} command')
                self.listT()
            elif message[0] == 'UPD':
                if (len(message)!=3):
                    self.sendM('108')
                    continue
                print(f'{self.name} issued {message[0]} command')
                self.upF(message[1],message[2])
            elif message[0] == 'RMV':
                if (len(message)!=2):
                    self.sendM('108')
                    continue
                print(f'{self.name} issued {message[0]} command')
                self.removeT(message[1])
            elif message[0] == 'DWN':
                if (len(message)!=3):
                    self.sendM('108')
                    continue
                print(f'{self.name} issued {message[0]} command')
                self.dwnF(message[1],message[2])
            else:
                self.sendM('000')


def creatTH():#create thread
        global portN
        port = random.randint(20000,60000)
        while port in portN:
            port = random.randint(20000,60000)
        addr = ('127.0.0.1',port)
        ssock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        ssock.bind(addr)
        portN.append(port)
        return port,ssock

if not os.path.exists('./titles'):
    os.mkdir('./titles')
if not os.path.exists('./uploadF'):
    os.mkdir('./uploadF')

PORT = int(sys.argv[1])
ADDRESS = ('127.0.0.1',PORT)
global server
server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.bind(ADDRESS)
print('Waiting for clients')

while True:
    recvMess = server.recvfrom(1024)
    cAddress = recvMess[1]
    port,subsock = creatTH() #create an new socket with unique port number to specific client
    pp = str(port).encode() # send new port number to client
    server.sendto(pp,cAddress)
    thr = ClientThread(cAddress,port,subsock)
    thr.start()
    




    
    