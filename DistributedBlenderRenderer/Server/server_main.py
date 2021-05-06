##
## Main class for running and handling the server.
## Uses python sockets to achieve most of what it needs to do.
##

import socket
from _thread import *
import threading

class Client_Connection():

	def __init__(self, connection, address):
		self.connection = connection
		self.address = address
		
		##Tags for what they have or haven't done.
		self.in_queue = False
		self.file_uuids = []
		self.rendering = False ##False when not rendering, the directory of the file when rendering.

	def enter_queue(self):
		self.in_queue = True

	def exit_queue(self):
		self.in_queue = False

	def add_file_uuid(self, uuid):
		self.file_uuids.append(uuid)

	def remove_uuid(self, uuid):
		self.file_uuids.remove(uuid)

	def empty_uuids(self):
		self.file_uuids= []

	def enter_render(self):
		self.rendering = True

	def leave_render(self):
		self.rendering = False

##Globals
accepting_clients = True
accepting_queue = True

##Misc Functions
def Send_Message(Client : Client_Connection, message):
	Client.connection.send(message.encode('ascii'))

class Host_Server():

	def __init__(self, ip, port, max_connections):
		self.ip = ip
		self.port = port
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.socket.bind((self.ip, self.port))

		self.max_connections = max_connections

		self.online = False

		self.receiving = False

		self.responses = {'1101' : self.Response_1101, '2101' : self.Response_2101, '3101' : self.Response_3101}

	def run_server(self):
		thread_lock = threading.Lock()

		self._listen_loop(thread_lock)

	def _listen_loop(self, thread_lock):
		self.socket.listen(self.max_connections)

		while self.online:

			conn, addr = self.socket.accept()
			c = Client_Connection(conn, addr)

			thread_lock.acquire()
			print("SERVER LOG : CONNECTION FROM " + addr[0])

			start_new_thread(self._thread_loop, (c,))

	def _thread_loop(self, Client):
		while self.online:
			if self.receiving == False:
				data = Client.connection.recv(1024)
				if not data:
					Send_Message(Client, '1102')
				else:
					try:
						print(data.decode('ascii'))
					except:
						pass
					answer = self.Parse_Response(Client, data.decode('ascii'))
			else:
				##data = Client.connection.recv(1024)
				##try:
					##print(data[:22].decode())
				##except:
					##print(data[:22])
				pass

	def Parse_Response(self, Client, message):
		try:
			self.responses[message](Client)
		except KeyError:
			return False

	##11XX Functions
	def Response_1101(self, Client : Client_Connection):
		if accepting_clients == True:
			Send_Message(Client, '1101')
		else:
			Send_Message(Client, '1102')

	#21XX Functions
	def Response_2101(self, Client : Client_Connection):
		if accepting_queue == True:
			Send_Message(Client, '2101')
			Client.enter_queue()
		else:
			Send_Message(Client, '2102')
			Client.exit_queue()
			Client.empty_uuids()
			Client.leave_render()
			Client.connection.close()

	#31XX Functions
	def Response_3101(self, Client : Client_Connection):
		##This one is for when the server receives a command asking for receiving a file.
		self.receiving = True
		Send_Message(Client, '3101')
		Client.rendering = 'airports.csv'
		if Client.rendering != False:
			try:
				with open(Client.rendering, 'wb') as f:
					l = Client.connection.recv(1024)
					while l:
						
						f.write(l)
						l = Client.connection.recv(1024)
						
						try:
							decoded = l.decode()
						except:
							decoded = l

						print(decoded)

						if decoded[:22] == '{DBRENDOFFILESEQUENCE}':
							print("True")
							break

					print("Finished Receiving")
					f.close()
					Send_Message(Client, '3105')
			except IOError:
				Send_Message(Client, '3102')
		else:
			Send_Message(Client, '3102')

	#41XX Functions
	def Response_4101(self, Client : Client_Connection):
		Send_Message(Client, '4101')

server = Host_Server('127.0.0.1', 5555, 64)
server.online = True
server.run_server()