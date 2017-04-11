import socket
import sys
import os

print("Enter the port number for this client")
portNo = int(input())

def sendToServer(message):
	try:
		# Create a TCP/IP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		addr = ('localhost', portNo)
		##print("Attempted bounding in sendToServer is ", addr)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(addr)
		# Connect the socket to the port where the server is listening
		server_address = ('localhost', 10000)
		print("__________________________________________________________________")
		print('Connecting to  Server: %s port %s' % server_address)
		print("__________________________________________________________________")
		sock.connect(server_address)

		## Request a File from server
		## Use the returned Address to connect and LOOKUP file
		## Register a file with a server
		##print('sending "%s"' % message)
		sock.sendall(str.encode(message))
		amount_received = 0
		amount_expected = len(message)
		print("__________________________________________________________________")
		while amount_received < amount_expected:
			data = sock.recv(10000)
			amount_received += len(data)
			print('Response From Server: "%s"' % data.decode())
			data = data.decode()
			sock.close()
			return data
	finally:
		#print('closing socket from SERVER')
		sock.close()

def sendToClient(IP_ADDRESS, fname):
	try:
		ip_port = str(IP_ADDRESS).split(':')
		IP = ip_port[0].strip()
		PORT = ip_port[1].strip()
		# Create a TCP/IP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Connect the socket to the port where the server is listening
		server_address = (IP, int(PORT)+1)
		sock.connect(server_address)

		## Request a File from server
		## Use the returned Address to connect and LOOKUP file
		## Register a file with a server
		message = "GET HTTP/1.1|"+fname
		print("__________________________________________________________________")
		print('Connecting to Client:  %s port %s' % server_address)
		##print('Sending "%s"' % message)
		sock.sendall(str.encode(message))
		amount_received = 0
		amount_expected = len(message)
		dataToSave = ""
		while amount_received < amount_expected:
			data = sock.recv(10000)
			amount_received += len(data)
			print('"%s"' % data.decode())
			dataToSave+=data.decode()
			sock.close()
		print("__________________________________________________________________")
		print('Do you want to save the contents of this file?:	Y/N')
		choice = input()
		if(choice=='Y'):
			print("Enter the file name to save these contents")
			newFile = input()
			f = open(newFile, 'w')
			f.write(dataToSave)
			print("File Saved!!")
	except:
		print("There was a problem connecting..")
	finally:
		print('closing socket from CLIENT')
		sock.close()



# Bind the socket to the port



def server():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_address = ('localhost', int(portNo)+1)
	print('starting up on %s port %s' % server_address)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(server_address)

	# Listen for incoming connections
	sock.listen(1)
	while True:
		##print('waiting for a connection')
		connection, client_address = sock.accept()

		try:
			print('Conection Request From: ', client_address)

		# Receive the data in small chunks and retransmit it
			while True:
				data = connection.recv(10000)
				if data:
					data = data.decode()
					data = data.split('|')
					reqType = data[0]
					fname = data[1]
					try:
						if(reqType=="GET HTTP/1.1"):
							lines = [line.rstrip('\n') for line in open(fname)]
							dataToSend = ''.join(lines)
						connection.sendall(dataToSend.encode())
					except:
						dataToSend = "File Is Currently Not Available, Sorry."
						connection.sendall(dataToSend.encode())

					##connection.close()
				else:
					##connection.close()
					break
            
		finally:
			A = "A"
        # Clean up the connection
				##connection.close()





LOOKUP = "LOOKUP|"
ADD = "ADD|"

newpid = os.fork()
if(newpid==0):
	while(1):
		print("__________________________________________________________________")
		print("Select 1 to view all files offered on this Server")
		print("Select 2 to request a file")
		print("Select 3 to register a file with the server")
		choice = input()
		if(choice=="1"):
			print("The files offered on this server are:-")
			filesOffered = sendToServer("LIST|ALL")
			filesOffered = filesOffered.split(',')
			count = 1
			for file in filesOffered:
				print(count, ": ", file)
				count+=1
			print("__________________________________________________________________")
			fnum = int(input("Press 0 to go Back, Enter The Index Of The File You Want:	"))
			if(fnum==0):
				continue
			fnum-=1
			fname = filesOffered[fnum]
			LOOKUP+=fname
			response = sendToServer(LOOKUP)
			LOOKUP = "LOOKUP|"
			HEADER = response.split('$')
			IP = HEADER[1]
			if(HEADER[0]=='HTTP/1.0 404 NOT FOUND\r\n'):
				print("Error 404, The requested file was not found.")
			else:	
				sendToClient(IP, fname)
			print("__________________________________________________________________")

		elif(choice=="2"):
			fname = input("Enter The File Name. We'll Connect You Automatically:	")
			LOOKUP+=fname
			response = sendToServer(LOOKUP)
			LOOKUP = "LOOKUP|"
			HEADER = response.split('$')
			IP = HEADER[1]
			if(HEADER[0]=='HTTP/1.0 404 NOT FOUND\r\n'):
				print("Error 404, The requested file was not found.")
			else:	
				sendToClient(IP, fname)
			print("__________________________________________________________________")

		elif(choice=="3"):
			print("Enter the name of the file you want to offer")
			fname = input("Enter the file you want to offer")
			ADD+=fname
			status = sendToServer(ADD)
			ADD = "ADD|"
			print("__________________________________________________________________")
else:
	server()
