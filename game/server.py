import math
import pickle
import random
import socket
import threading
import time

# Connection Data
host = ''

port = 55555

W, H = 1600, 830

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
server.bind((host, port))
server.listen()

class Session:

    # Lists For Clients and Their Nicknames
    clients = []
    nicknames = []
    players =[]
    current_id = 0

    def __init__(self):
        self.clients = []
        self.nicknames = []
        self.senderThread = threading.Thread(target=self.sender_thread, args=())
        self.senderThread.start()

    #Sending Messages To All Connected Clients
    def broadcast(self, message):
        for client in self.clients:
            client['client'].send(str.encode(message))
    
    def get_start_locations(self):

        x = random.randrange(0,W)
        y = random.randrange(0,H)
        return (x,y)
    
    def sender_thread(self):
        while True:
            print(self.clients)
            for idx , client in enumerate(self.clients):
                print("in for loop kbera, ", idx)
                client_id = client["id"]
                try:
                    for player in self.players:
                        player_id = player['id']
                        if player_id == client_id:
                            continue
                        reply = f"LOCATION: {player_id}:{player['x']}:{player['y']}"
                        while len(reply)<19:
                            reply+=' '
                        #print("sending ", reply, "to", client)
                        client['client'].send(str.encode(reply))
                except:
                    
                    #client['client'].close()

                    
                    self.clients.pop(idx)
                    print("in first pop")
                    
                    self.players.pop(idx)
                    
                    print("from send ", idx)

                    # reply = f"LEFT:{player_id}"
                    # while len(reply) < 19:
                    #     reply += ' '
                    #self.broadcast(reply) 
                    #nickname = self.nicknames[idx]
                    # send to other players that player left
                    #self.nicknames.remove(nickname)
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
                        print("in location condition")
                        self.players[idx]['x'] = x
                        self.players[idx]['y'] = y
            except Exception as e:
                print (e)
                # idx = self.get_client_idx_by_socket(client)
                # if (idx != -1):
                #     print(idx)
                #     self.clients.pop(idx)
                #     self.players.pop(idx)   

                # reply = f"LEFT:{player_id}"
                # while len(reply) < 19:
                #     reply += ' '
                break            
        print("Connection Closed")
        client.close()

 
    def add_client(self, client):
        

        # Request And Store Nickname
        #client.send('NICK'.encode('ascii'))
        # nickname = client.recv(1024).decode('ascii')

        # self.nicknames.append(nickname)
        self.clients.append({ 'id': self.current_id, 'client': client })
        self.players.append({'id':self.current_id, 'x':0, 'y':0})
        client.send(str.encode(str(self.current_id))) 


        thread = threading.Thread(target=self.player_handle, args=(client,))
        thread.start()  
        self.current_id += 1



sessions = []


# Receiving / Listening Function
def create_session():
        newSession = Session()
        sessions.append(newSession)
        while True:
            # Accept Connection
            client, address = server.accept()
            print("Connected with {}".format(str(address)))


            newSession.add_client(client=client)
            
create_session()