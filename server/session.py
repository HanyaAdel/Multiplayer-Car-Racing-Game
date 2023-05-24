from chat_server import ChatServer
from game_server import GameServer

class Session:
    def __init__(self, id):
        self.current_id = 0
        self.session_id = id
        self.game_server = GameServer()
        self.chat_server = ChatServer()

    def add_client(self, game_client, chat_client, name):
        self.game_server.add_client(id=self.current_id,game_client=game_client, nickname = name)
        self.chat_server.add_client(id=self.current_id, chat_client=chat_client)
        self.current_id += 1
