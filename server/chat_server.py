import threading
import util

class ChatServer:
    def __init__(self,session):
        self.session = session

    def handle_chat(self, client_socket):
        while True:

            try:
                # Broadcasting Messages
                message = client_socket.recv(1024).decode('ascii')
                index = util.get_client_idx_by_socket(client_socket, self.session.chat_clients)

                name = self.session.players[index]['name']
                
                util.broadcast('{}: {}'.format(name, message), self.session.chat_clients )

            except:
                # Removing And Closing Clients
                index = util.get_client_idx_by_socket(client_socket, self.session.chat_clients)
                self.session.chat_clients.pop(index)
                client_socket.close()
                name = self.session.players[index]['name']

                util.broadcast('{} left!'.format(name), self.session.chat_clients)

                break
    
    def add_client(self, id, chat_client):
        self.session.chat_clients.append({ 'id': id, 'client': chat_client })
        self.client_thread = threading.Thread(target=self.handle_chat, args=(chat_client,))
        self.client_thread.start()