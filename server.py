import socket
import sys
import os

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)





# Bind the socket to the port
index = []
files = []
IPs = []
def refreshList():
    global files, IPs
    lines = [line.rstrip('\n') for line in open('serverIndex.txt')]
    files = []
    IPs = []
    for l in lines:
        temp = l.split('|')
        files.append(temp[0])
        ##print(temp[0])
        IPs.append(temp[1])

refreshList()
##LINKED LIST STUFF IS HERE

class node:
    def __init__(self, fileName, addr):
        self.fileName = fileName
        self.addr = addr
        self.next = None

class linkedList:
    root = None
    def __init__(self, root):
        self.root = root

def buildList():
    refreshList()
    global files, IPs
    root = node("root", None)
    LL = linkedList(root)
    for f in files:
        index = IPs[files.index(f)]
        addListItem(f, index, LL)
    return LL

def printListValues(LL):
    temp = LL.root
    while(temp.next!=None):
        temp = temp.next
    return

def addListItem(fname, addr, LL):
    newNode = node(fname, addr)
    temp = LL.root
    while(temp.next!=None):
        temp = temp.next
    temp.next = newNode
    return LL

def searchLinkedList(fname, LL):
    temp = LL.root
    while(temp.next!=None):
        if(temp.fname==fname):
            return temp.addr
        temp = temp.next
    return None

print("FIles available on this server are:")
for f in files:
    print(f)
server_address = ('localhost', 10000)
##print('starting up on %s port %s' % server_address)
sock.bind(server_address)
# Listen for incoming connections
sock.listen(1)


def Listening():
    while True:
        # Wait for a connection
        ##print('waiting for a connection')
        connection, client_address = sock.accept()
        newpid = os.fork()
        if(newpid==0):
            print(" Child process")
        else:
            Listening()

        try:
            print('Connection Request From Client: ', client_address)

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(10000)
            
                if data:
                    data = data.decode()
                    temp = data.split('|')
                    reqType = temp[0]

                    fname = temp[1]
                    ##print("Recieved data", temp[0], temp[1])
                    if(reqType == "LIST"):
                        LL = buildList()
                        p2p = ','.join(files)
                        if(len(p2p)==0):
                            p2p = "No files registered"
                        connection.sendall(p2p.encode())
                    elif(reqType=="LOOKUP"):
                        LL = buildList()
                        if(fname in files):
                            print("The File Was Found!")
                            index = files.index(fname)
                            p2p = IPs[index]
                            p2p = str(p2p)
                            p2p = 'HTTP/1.0 200 OK\r\n'+'$'+p2p
                        else:
                            print("The File Requested By The Client Was Not Found.")
                            p2p = 'HTTP/1.0 404 NOT FOUND\r\n$None'
                        connection.sendall(p2p.encode())
                    elif(reqType=="ADD"):
                        if(fname in files):
                            p2p = "File Already Exists On This Server, Thank You"
                        else:
                            f = open("serverIndex.txt", "a")
                            ip_addr = client_address[0]
                            port_no = client_address[1]
                            ##print("Storing :- IP: ", ip_addr, "port: ", port_no, "File: ", fname)
                            lineToStore = str(fname)+"|"+str(ip_addr)+":"+str(port_no)+"\n"
                            with open("serverIndex.txt", "a") as f:
                                f.write(lineToStore)
                            p2p = "File stored, Thank you"
                            LL = buildList()
                        ##print('sending data back to the client')
                        connection.sendall(p2p.encode())
                else:
                    ##print('no more data from', client_address)
                    break
            
        finally:
            # Clean up the connection
            connection.close()

Listening()