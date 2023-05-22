import math
import pickle
import random
import socket
import threading
import time
# import util

# Connection Data
host = ''

port = 55555

W, H = 1600, 830

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
server.bind((host, port))
server.listen()

class Chat:
    def __init__(self):
        pass

class Session:
    
    # Lists For Clients and Their Nicknames

    def __init__(self, id):
        self.current_id = 0
        self.session_id = id
        self.clients = []
        self.players = []
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
    
    def remove_client(self, idx):
        #client['client'].close()
        #print("beginning of remove client")
        toBeDeleted_id = self.players[idx]['id']
        self.clients.pop(idx)
        #print("in first pop")
        
        self.players.pop(idx)
        
        #print("from send ", idx)

        #print("boradcasting player leave", toBeDeleted_id)
        message = f"LEFT:{toBeDeleted_id}"
        self.broadcast(message=message)
        #print("after broadcast")
    
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
                        #print("sending ", reply, "to", client)
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
            #print(d)

        
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
    def getHeader(self, data):
            try:
                d = data.split(":")
                return d[0]
            except:
                pass
    def parse_message(self, message):
        try:
            d = message.split(":")
            return d[1]
        except:
            pass
    def receiver_thread(self,client):
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


    # Handling Messages From Clients
    def chat_handle(self, client):
        while True:
            #print("Session id", self.session_id)
            
            try:
                # Broadcasting Messages
                message = client.recv(1024).decode('ascii')
                header = self.getHeader(message)
                if (header != "MESSAGE"):
                    continue
                message = self.parse_message(message)
                print(self.clients)
                index = self.get_client_idx_by_socket(client)
                #index = self.clients.index(client)
                name = self.players[index]['name']
                #nickname = self.nicknames[index]
                
                self.broadcast('MESSAGE:{}: {}'.format(name, message))
                #self.broadcast(message)
            except:
                # # Removing And Closing Clients
                # index = self.clients.index(client)
                # self.remove_client()
                # self.clients.remove(client)
                # client.close()
                # name = self.players[index]
                index = self.get_client_idx_by_socket(client)
                name = self.players[index]['name']                
                self.broadcast('{} left!'.format(name))

                #self.nicknames.remove(nickname)
                break


 
    def add_client(self, client):
        
        # Request And Store Nickname
        name = client.recv(1024).decode('ascii')  

        #print("adding client in session", self.session_id)
        self.clients.append({ 'id': self.current_id, 'client': client })
        self.players.append({'id':self.current_id, 'name': name,'x':0, 'y':0})

        message = f"{self.current_id}:{len(self.players)}"
        client.send(str.encode(str(message))) 


        self.thread = threading.Thread(target=self.receiver_thread, args=(client,))
        self.thread.start()  

        self.chat_thread = threading.Thread(target=self.chat_handle, args=(client,))
        self.chat_thread.start()  
        self.current_id += 1



sessions = []


# Receiving / Listening Function
def create_session():
        # newSession = Session()
        # sessions.append(newSession)
        while True:
            # Accept Connection
            client, address = server.accept()
            print("Connected with {}".format(str(address)))

            # Request And Store Nickname
            # client.send('NEW_SESSION'.encode('ascii'))
            newSession = client.recv(1024).decode('ascii')

            # newSession.add_client(client=client)
            #print(newSession)
            if newSession == 'yes':
                # start new session
                newSession = Session(id=len(sessions))
                sessions.append(newSession)

                newSession.add_client(client=client)

            if newSession == 'no':


                # client.send('SESSION_NUM'.encode('ascii'))

                sessionNum = client.recv(1024).decode('ascii')

                session = sessions[int(sessionNum)]
                session.add_client(client)
            
create_session()