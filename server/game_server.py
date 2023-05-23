import threading
import time
import random

W, H = 1600, 830

class GameServer:
    def __init__(self):
        self.clients = []
        self.players = []
        self.senderThread = threading.Thread(target=self.sender_thread, args=())
        self.senderThread.start()
    
    def broadcast(self, message):
        for client in self.clients:
            client['client'].send(str.encode(message))

    def remove_client(self, idx):
        #client['client'].close()
        print("beginning of remove client")
        toBeDeleted_id = self.players[idx]['id']
        self.clients.pop(idx)
        print("in first pop")
        
        self.players.pop(idx)
        
        print("from send ", idx)

        print("boradcasting player leave", toBeDeleted_id)
        message = f"LEFT:{toBeDeleted_id}"
        self.broadcast(message=message)
        print("after broadcast")

    def sender_thread(self):
        while True:
            # print(self.clients)
            # print("session id:",self.session_id)
            # print(self.players)
            for idx , client in enumerate(self.clients):
                # print("in for loop kbera, ", idx)
                try:
                    for player in self.players:
                        player_id = player['id']
                        reply = f"LOCATION: {player_id}:{player['x']}:{player['y']}"
                        # reply = util.fill_data(reply)
                        while len(reply)<19:
                            reply+=' '
                        # print("sending ", reply)
                        client['client'].send(str.encode(reply))
                except:
                    print("in exception")
                    self.remove_client(idx=idx)

                    break

            time.sleep(16/1000)

    def parse_data(self, data):
        try:
            d = data.split(":")
            return d[0], int(d[1]), int(d[2]), int(d[3])
        except Exception as e:
            print("exception from parse data ", e)
            print(d)

        
    def get_client_idx_by_socket(self, client):
        for client_idx, client_itr in enumerate(self.clients):
            if client_itr['client'] == client:
                return client_idx
        return -1
    
    def get_player_idx_by_id(self, id):
        for player_idx, player in enumerate(self.players):
            if player['id'] == id:
                return player_idx
        return -1

    def player_handle(self,client):
        x, y = (10,10)
        
        while True:
            try:
                data = client.recv(19)
                if not data:
                    #client.send(str.encode("Goodbye"))
                    break
                else:
                    reply = data.decode()
                    header, id, x, y = self.parse_data(reply)
                    if header == "LOCATION":
                        idx = self.get_player_idx_by_id(id)
                        if (idx == -1):
                            continue
                        # print("in location condition")
                        self.players[idx]['x'] = x
                        self.players[idx]['y'] = y
            except Exception as e:
                print (e)
                break            
        print("Connection Closed")
        client.close()

    def add_client(self, id, game_client):
        self.clients.append({ 'id': id, 'client': game_client })
        self.players.append({'id': id, 'x':0, 'y':0})
        message = f"{id}:{len(self.players)}"
        game_client.send(str.encode(str(message))) 
        self.client_thread = threading.Thread(target=self.player_handle, args=(game_client,))
        self.client_thread.start()

    def get_start_locations(self):

        x = random.randrange(0,W)
        y = random.randrange(0,H)
        return (x,y)