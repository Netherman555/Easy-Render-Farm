##
## Main class for speaking to server and handling rendering
## This file just handles the communication aspect and not the blender one.
##

import socket

##Misc Functions
def Send_Message(socket : socket.socket, message):
	socket.send(message.encode('ascii'))

##Main Class
class Client():

	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		##Tags
		self.connected = False
		self.in_queue = False
		self.file_uuids = []
		self.rendering = False

	def connect(self, address, port):
		if self.connected == False:
			self.socket.connect((address, port))
		self.connected = True

	def disconnect(self):
		if self.connected == True:
		   self.socket.close()
		self.connected = False

	def receive_data(self, bytes):
		return self.socket.recv(bytes).decode('ascii')

	def Send_1101(self):
		Send_Message(self.socket, '1101')
		data = self.receive_data(1024)
		print(data)
		if data == '1101':
			self.connected = True
		elif data == '1102':
			self.socket.close()

	def Send_2101(self):
		Send_Message(self.socket, '2101')
		data = self.receive_data(1024)
		print(data)
		if data == '2101':
			self.in_queue = True
	
	def Send_3101(self, file_directory):
		Send_Message(self.socket, '3101')
		data = self.receive_data(1024)
		if data == '3101':
			self._send_file(file_directory)
			data = self.receive_data(1024)

	def _send_file(self, directory):
		try:
			with open(directory, 'rb') as f:
				l = f.read(1024)
				while (l):
					self.socket.send(l)
					l = f.read(1024)
				Send_Message(self.socket, '{DBRENDOFFILESEQUENCE}')
				f.close()
				print("Finished Sending File")
		except IOError:
			return False

cl = Client()
cl.connect('127.0.0.1', 5555)
cl.Send_1101()
cl.Send_2101()
cl.Send_3101('airports.csv')