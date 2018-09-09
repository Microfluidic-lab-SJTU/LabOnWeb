# -*- coding=utf-8-*-
from concurrent.futures import ThreadPoolExecutor, wait
import socket
import sys
from base_camera import BaseCamera
addr=('10.164.33.222',6666)

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def socket_client():
	try:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect(addr)
	except socket.error as msg:
		print(msg)
		sys.exit(1)
	while 1:
		data = raw_input('please input work:')
		s.send(data)
		print(s.recv(1024))
		if data == 'exit':
			break
	s.close()
def request_data(s):
	s.send('acquire'.encode())
	#print("send acquire")
	length = recvall(s,16)
	stringdata = recvall(s,int(length))
	return stringdata
class Camera(BaseCamera):
	@staticmethod
	def frames():
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
			
if __name__ == '__main__':
	socket_client()

