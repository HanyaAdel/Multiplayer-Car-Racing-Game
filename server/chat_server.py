import threading

class ChatServer:
    def __init__(self,session):
        self.session = session
        self.session.chat_clients = []
        # self.session.nicknames = []

    def broadcast(self, message):
        for client in self.session.chat_clients:
            client['client'].send(str.encode(message))
    
    def get_client_idx_by_socket(self, client):
        for client_idx, client_itr in enumerate(self.session.chat_clients):
            if client_itr['client'] == client:
                return client_idx  
        return -1
    
    def handle_chat(self, client_socket):
        while True:
            print(self.session.nicknames)
            try:
                # Broadcasting Messages
                message = client_socket.recv(1024).decode('ascii')
                index = self.get_client_idx_by_socket(client_socket)
                nickname = self.session.nicknames[index]
                
                self.broadcast('{}: {}'.format(nickname, message))
                #self.broadcast(message)
            except:
                # Removing And Closing Clients
                index = self.get_client_idx_by_socket(client_socket)
                self.session.chat_clients.pop(index)
                client_socket.close()
                nickname = self.session.nicknames[index]
                self.broadcast('{} left!'.format(nickname))
                self.session.nicknames.remove(nickname)
                break
    
    def add_client(self, id, chat_client, username):
        # print("waiting for nickname")
        # nickname = chat_client.recv(1024).decode('ascii')
        # print("received nickname")
        # print("adding client in session", self.session_id)
        self.session.nicknames.append(username)
        self.session.chat_clients.append({ 'id': id, 'client': chat_client })
        self.client_thread = threading.Thread(target=self.handle_chat, args=(chat_client,))
        self.client_thread.start()