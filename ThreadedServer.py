import socket
import threading

class PyTrekServer(object):
    # Must also define a callback function that handles client messages
    def __init__(self, host, port, callback):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.callbackFunc = callback
        self.isClose = False

    def start(self):
        print("Server started on port", self.port)
        threading.Thread(target = self.listen).start()
        
    def close(self):
        # Hack: Currently satisfies wait condition by opening a new socket. 
        # Good for cleanly closing server.
        print("Closing server.")
        self.isClose = True
        socket.socket(socket.AF_INET, 
                  socket.SOCK_STREAM).connect( (self.host, self.port))
        self.sock.close()
        
    def listen(self):
        self.sock.listen(5)
        while not self.isClose:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()
            
    def setClientConnectCallback(self, callback):
        self.clientConnected = callback

    def listenToClient(self, client, address):
        size = 1024
        clientInit = False
        while not self.isClose:
            # Keep trying to send a message until the client sends one back
            if not clientInit:
                if hasattr(self, 'clientConnected'): self.clientConnected(client, address)
                
            data = client.recv(size)
            if data:
                clientInit = True
                # Set the response to echo back the recieved data 
                response = data;
                self.callbackFunc(client, response)
            else:
                print('Client', client, 'disconnected')
                return True
