import socket
import threading

# Connection Data
host = '127.0.0.1'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

class Session:

    # Lists For Clients and Their Nicknames
    clients = []
    nicknames = []

    def __init__(self):
        self.clients = []
        self.nicknames = []

    # Sending Messages To All Connected Clients
    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    # Handling Messages From Clients
    def handle(self, client):
        while True:
            try:
                # Broadcasting Messages
                message = client.recv(1024).decode('ascii')
                index = self.clients.index(client)
                nickname = self.nicknames[index]
                
                self.broadcast('{}: {}'.format(nickname, message).encode('ascii'))
                #self.broadcast(message)
            except:
                # Removing And Closing Clients
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.broadcast('{} left!'.format(nickname).encode('ascii'))
                self.nicknames.remove(nickname)
                break


    
    def add_client(self, client):
        print("Connected")

        # Request And Store Nickname
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        self.nicknames.append(nickname)
        self.clients.append(client)

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        self.broadcast("{} joined!".format(nickname).encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))        


        thread = threading.Thread(target=self.handle, args=(client,))
        thread.start()        



sessions = []


# Receiving / Listening Function
def join_session():
        while True:
            # Accept Connection
            client, address = server.accept()
            print("Connected with {}".format(str(address)))

            # Request And Store Nickname
            client.send('NEW_SESSION'.encode('ascii'))
            newSession = client.recv(1024).decode('ascii')
            print(newSession)
            if newSession == 'yes':
                # start new session
                newSession = Session()
                sessions.append(newSession)

                newSession.add_client(client=client)

            if newSession == 'no':


                client.send('SESSION_NUM'.encode('ascii'))

                sessionNum = client.recv(1024).decode('ascii')

                session = sessions[int(sessionNum)]
                session.add_client(client)

join_session()