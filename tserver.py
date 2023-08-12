

#coding:gb2312
 
import socket,sys
import time
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
 
IP=socket.gethostbyname(socket.gethostname())
s.settimeout(30) #设置超时
s.bind(('127.0.0.1',1080))
print ('waiting')
while 1:
    try:
        s.settimeout(5)
        d,a=s.recvfrom(8192)
#        s.sendto('[%s] %s'%(time.ctime(),d),a)
#        print "收到数据并且返回到：",a
 
    except socket.timeout:
        print('time out!')
 
s.close()