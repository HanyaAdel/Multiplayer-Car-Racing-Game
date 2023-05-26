import threading
import util

class ChatServer:
    def __init__(self,session):
        self.session = session

    def broadcast_messages(self, message):
        for client in self.session.chat_clients:

            message_length = len(message.encode('utf-8'))

            header = message_length.to_bytes(4, byteorder='big')
            client['client'].sendall(header + message.encode('utf-8'))            

    def handle_chat(self, client_socket):
        while True:

            try:
                # Broadcasting Messages
                message = util.receive_data(client_socket)
                index = util.get_client_idx_by_socket(client_socket, self.session.chat_clients)

                name = self.session.players[index]['name']

                id = self.session.players[index]['id']
                session_code = self.session.session_code

                self.session.model.addMessage(id, session_code, message)
                
                self.broadcast_messages('{}: {}'.format(name, message) )

            except:
                # Removing And Closing Clients
                index = util.get_client_idx_by_socket(client_socket, self.session.chat_clients)
                self.session.chat_clients.pop(index)
                client_socket.close()
                name = self.session.players[index]['name']

                self.broadcast_messages('{} left!'.format(name))

                break
    
    def send_messages_history(self, chat_client, messages):
        for message in messages:
            id = message[0]
            message_text = message[1]

            index = util.get_player_idx_by_id(id, self.session.players)

            name = self.session.players[index]['name']
            to_send = name + ': ' + message_text
            message_length = len(to_send.encode('utf-8'))


            header = message_length.to_bytes(4, byteorder='big')
            chat_client.sendall(header + to_send.encode('utf-8'))

    def add_client(self, id, chat_client, messages):
        self.session.chat_clients.append({ 'id': id, 'client': chat_client })
        self.send_messages_history(chat_client, messages)
        self.client_thread = threading.Thread(target=self.handle_chat, args=(chat_client,))
        self.client_thread.start()