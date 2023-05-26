from chat_server import ChatServer
from game_server import GameServer
import time
import threading

class Session:
    def __init__(self, model):
        self.model = model
        self.numPlayers = 0
        self.game_clients = []
        self.chat_clients = []
        self.exist = True
        self.available_lanes = [1,2,3,4,5]

        self.players = []
        self.session_code = model.addSession()
        self.game_server = GameServer(session = self)
        self.chat_server = ChatServer(session= self)
        self.syncThread = threading.Thread(target=self.syncDatabase)
        self.syncThread.start()

    def add_client(self, game_client, chat_client, username, client_id):
        score = self.model.addPlayerToSession(player_id = client_id, session_code = self.session_code)
        print(f"{username}'s score is {score}")
        self.players.append({'id': client_id, 'x':0, 'y':0, 'score':score, 'name':username, 'lane':self.get_lane()})
        messages = self.model.getSessionMessages(self.session_code)
        self.game_server.add_client(id=client_id,game_client=game_client)
        self.chat_server.add_client(id=client_id, chat_client=chat_client, messages=messages)
        self.numPlayers += 1
    
    def get_lane(self):
        self.available_lanes.sort()
        return self.available_lanes.pop(0)

    def remove_client(self, idx):
        player = self.players.pop(idx)
        self.available_lanes.append(player['lane'])
        print("in session remove client")
        self.numPlayers -= 1
        if self.numPlayers == 0:
            print("closing session")
            self.closeSession()
            print("session Closed")

    def closeSession(self):
        self.model.deleteSession(self.session_code)
        self.exist = False

    def syncDatabase(self):
        while self.exist:
            for player in self.players:
                player['score']+=1
            self.model.updateRecords([tuple([d['score'],d['id'],self.session_code]) for d in self.players])
            time.sleep(1) #update records once every second
            