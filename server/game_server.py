import threading
import time
import random
import util

W, H = 1600, 830

class GameServer:
    def __init__(self,session):
        self.session = session
        # self.session.game_clients = []
        # self.session.players = []
        self.senderThread = threading.Thread(target=self.sender_thread, args=())
        self.senderThread.start()
    
    def remove_client(self, idx):
        #client['client'].close()
        print("beginning of remove client")
        toBeDeleted_id = self.session.players[idx]['id']
        self.session.game_clients.pop(idx)
        print("in first pop")
        
        self.session.players.pop(idx)
        
        print("from send ", idx)

        print("boradcasting player leave", toBeDeleted_id)
        message = f"LEFT:{toBeDeleted_id}"
        util.broadcast(message=message, clients=self.session.game_clients)
        print("after broadcast")
        print("removing client from session")
        self.session.remove_client()

    def sender_thread(self):
        while True:
            # print(self.clients)
            # print("session id:",self.session_id)
            # print(self.players)
            for idx , client in enumerate(self.session.game_clients):
                # print("in for loop kbera, ", idx)
                try:
                    for player in self.session.players:
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
                        idx = util.get_player_idx_by_id(id, self.session.players)
                        if (idx == -1):
                            continue
                        # print("in location condition")
                        self.session.players[idx]['x'] = x
                        self.session.players[idx]['y'] = y
            except Exception as e:
                print (e)
                break            
        print("Connection Closed")
        client.close()

    def add_client(self, id, game_client, score):
        self.session.game_clients.append({ 'id': id, 'client': game_client })
        self.session.players.append({'id': id, 'x':0, 'y':0, 'score':score})
        message = f"{id}:{len(self.session.players)}"
        game_client.send(str.encode(str(message))) 
        self.client_thread = threading.Thread(target=self.player_handle, args=(game_client,))
        self.client_thread.start()

    def get_start_locations(self):

        x = random.randrange(0,W)
        y = random.randrange(0,H)
        return (x,y)