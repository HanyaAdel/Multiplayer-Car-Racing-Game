import math
import pickle
import random
import socket
import threading
import time

# Connection Data
host = '20.111.24.134'

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

    # Sending Messages To All Connected Clients
    # def broadcast(self, message):
    #     for client in self.clients:
    #         client.send(message)
    
    def get_start_locations(self):

        x = random.randrange(0,W)
        y = random.randrange(0,H)
        return (x,y)
    
    def sender_thread(self):
        while True:
            for idx , client in enumerate(self.clients):
                for player_idx, player in enumerate(self.players):
                    if player_idx == idx:
                        continue
                    reply = f"LOCATION: {player_idx}:{player['x']}:{player['y']}"
                    while len(reply)<19:
                        reply+=' '
                    print("sending ", reply, "to", client)
                    client.send(str.encode(reply))

                # reply = ''
                # if idx == 0:
                #     reply = pos[1]
                # else:
                #     reply = pos[0]
                # print("Sending: " + reply)
                # conn.send(str.encode(reply))
            time.sleep(16/1000)


    def parse_data(self, data):
        try:
            print("in parse data")

            d = data.split(":")
            print(d)
            return d[0], int(d[1]), int(d[2]), int(d[3])
        except:
            pass

    def player_handle(self,client):
        x, y = (10,10)
        
        while True:
            try:
                data = client.recv(19)
                print(data)
                if not data:
                    client.send(str.encode("Goodbye"))
                    break
                else:
                    reply = data.decode()
                    print(reply)
                    header, id, x, y = self.parse_data(reply)
                    print("after parse data")
                    if header == "LOCATION":
                        print("in condition")
                        self.players[id]['x'] = x
                        print("in second line of condtion")
                        self.players[id]['y'] = y
                        print("end of condition")
                    print("here2")
                    # # print("Recieved: " + reply)
                    # arr = reply.split(":")
                    # id = int(arr[0])
                    # pos[id] = reply
            except:
                break
        print("Connection Closed")
        client.close()

    # # Handling Messages From Clients
    # def handle(self, client, nickname):

    #     x, y = self.get_start_locations()
    #     self.players[self.current_id] = {"current_id": self.current_id,"x":x, "y":y,"color":(255, 128, 0),"score":0,"name":nickname}  # x, y color, score, name

    #     client.send(str(self.current_id).encode('ascii'))

    #     while True:
    #         try:

    #             # Broadcasting Messages
    #             message = client.recv(1024).decode('ascii')
    #             index = self.clients.index(client)
    #             nickname = self.nicknames[index]

    #             if message == 'get':
    #                 send_data = pickle.dumps(self.players)
    #                 client.send(send_data)

    #             else:      
    #                 message = message.encode('ascii')          
    #                 #send locations of all other players
    #                 #print("Recieved: " + message)

    #                 player = pickle.loads(message)

    #                 id = int(player["current_id"]) # id sent by client

    #                 self.players[id] = player

    #                 send_data = pickle.dumps(self.players)
    #                 client.send(send_data)

                
    #         except:
    #             # Removing And Closing Clients
    #             index = self.clients.index(client)
    #             self.clients.remove(client)
    #             client.close()
    #             nickname = self.nicknames[index]
    #             self.broadcast('{} left!'.format(nickname).encode('ascii'))
    #             self.nicknames.remove(nickname)
    #             break

    def add_client(self, client):
        

        # Request And Store Nickname
        #client.send('NICK'.encode('ascii'))
        # nickname = client.recv(1024).decode('ascii')

        # self.nicknames.append(nickname)
        self.clients.append(client)
        self.players.append({'id':self.current_id, 'x':0, 'y':0})
        # Print And Broadcast Nickname
        # print("Nickname is {}".format(nickname))

        #self.broadcast("{} joined!".format(nickname).encode('ascii'))

        print("before send id")
        print(self.current_id)
        client.send(str.encode(str(self.current_id))) 
        print("after send id")       


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