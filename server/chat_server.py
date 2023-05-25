import threading
import util

class ChatServer:
    def __init__(self,session):
        self.session = session
        self.session.chat_clients = []
        # self.session.nicknames = []


    
    def handle_chat(self, client_socket):
        while True:
            print(self.session.nicknames)
            try:
                # Broadcasting Messages
                message = client_socket.recv(1024).decode('ascii')
                index = util.get_client_idx_by_socket(client_socket, self.session.chat_clients)
                nickname = self.session.nicknames[index]
                
                util.broadcast('{}: {}'.format(nickname, message), self.session.chat_clients )
                #self.broadcast(message)
            except:
                # Removing And Closing Clients
                index = util.get_client_idx_by_socket(client_socket, self.session.chat_clients)
                self.session.chat_clients.pop(index)
                client_socket.close()
                nickname = self.session.nicknames[index]
                util.broadcast('{} left!'.format(nickname), self.session.chat_clients)
                self.session.nicknames.remove(nickname)
                break
    
    def add_client(self, id, chat_client, username):
        self.session.nicknames.append(username)
        self.session.chat_clients.append({ 'id': id, 'client': chat_client })
        self.client_thread = threading.Thread(target=self.handle_chat, args=(chat_client,))
        self.client_thread.start()