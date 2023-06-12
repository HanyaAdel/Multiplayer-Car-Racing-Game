import threading
import time
import random
import util

W, H = 1600, 830

class GameServer:
    def __init__(self,session):
        self.session = session
        self.senderThread = threading.Thread(target=self.sender_thread, args=())
    

    def start_sender(self):
        self.senderThread.start()
        
    def remove_client(self, idx):

        print("beginning of remove client")
        toBeDeleted_id = self.session.players[idx]['id']
        self.session.game_clients.pop(idx)
        print("in first pop")
        

        
        print("from send ", idx)

        print("boradcasting player leave", toBeDeleted_id)
        message = f"LEFT:{toBeDeleted_id}"
        util.broadcast(message=message, clients=self.session.game_clients)
        print("after broadcast")
        print("removing client from session")
        self.session.remove_client(idx)

    def sender_thread(self):
        counter = 0
        while True:
            counter += 1
            if counter == 350:
                counter = 0
                reply = f"OBSTACLE: {random.randrange(80,240)}"
                util.broadcast(message= reply, clients=self.session.game_clients)
            
            if self.session.started and time.time() - self.session.start_time >= 10000:
                print("session time expired")
                message = "END:"
                util.broadcast(message, self.session.game_clients)
                self.session.started = False

               
            for idx , client in enumerate(self.session.game_clients):
                # print("in for loop kbera, ", idx)
                try:
                    for player in self.session.players:
                        player_id = player['id']
                        reply = f"LOCATION: {player_id}:{player['name']}:{player['x']}:{player['y']}:{player['lane']}:{player['score']}"

                        util.send_data(reply, client['client'])
                except:
                    print("in exception")
                    self.remove_client(idx=idx)

                    break

            time.sleep(16/1000)

    def parse_data(self, data):
        #print (data)
        try:
            d = data.split(":")
            return d[0], int(d[1]), int(d[2]), int(d[3]), int(d[4])
        except Exception as e:
            print("exception from parse data ", e)
            print(d)




    def player_handle(self,client):
        x, y = (10,10)
        
        while True:
            try:
                data = util.receive_data(client)

                if not data:
                    #client.send(str.encode("Goodbye"))
                    break
                else:
                    reply = data
                    header, id, x, y, score = self.parse_data(reply)
                    if header == "LOCATION":
                        idx = util.get_player_idx_by_id(id, self.session.players)
                        if (idx == -1):
                            continue
                        self.session.players[idx]['x'] = x
                        self.session.players[idx]['y'] = y
                        self.session.players[idx]['score'] = score
            except Exception as e:
                print (e)
                break            
        print("Connection Closed")
        client.close()

    def add_client(self, id, game_client):
        self.session.game_clients.append({ 'id': id, 'client': game_client })
        index = util.get_player_idx_by_id(id, self.session.players)
        message = f"{id}:{self.session.players[index]['name']}: {len(self.session.players)}:{self.session.players[index]['lane']}:{self.session.players[index]['score']}"

        util.send_data(message, game_client)

        self.client_thread = threading.Thread(target=self.player_handle, args=(game_client,))
        self.client_thread.start()
