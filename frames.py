import time
from concurrent.futures import ThreadPoolExecutor, wait
import socket
import sys
def SimuFrames(addr):
	imgs = [open(f + '.jpg', 'rb').read() for f in ['1', '2', '3']]
	while True:
		time.sleep(1)
		yield imgs[int(time.time()) % 3]
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf
def request_data(s):
	s.send('acquire'.encode())
	#print("send acquire")
	length = recvall(s,16)
	stringdata = recvall(s,int(length))
	return stringdata
def RemoteFrames(addr):
	try:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect(addr)
		s.setblocking(1)
	except socket.error as msg:
		print(msg)	
		sys.exit(1)
	pool = ThreadPoolExecutor(1)
	s.send('acquire'.encode())
	#print("send acquire")
	length = recvall(s,16)
	stringdata = recvall(s,int(length))
	future = pool.submit(request_data,s)		
	#print(length)
	yield	stringdata
	while True:
		wait([future])
		stringdata = future.result()
		future = pool.submit(request_data,s)
		yield stringdata
	s.send('acquire'.encode())
	s.close()


