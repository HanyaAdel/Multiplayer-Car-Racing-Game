import socket
import  pickle
import util

# HOST = 'localhost'
HOST = '98.66.137.14'
PORT = 55555

class Network:
    """
    class to connect, send and recieve information from the server

    need to hardcode the host attirbute to be the server's ip
    """
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        
        
        self.addr = (HOST, PORT)

    def connect(self, username, password):
        """
        connects to server and returns the id of the client that connected
        :param name: str
        :return: int reprsenting id
        """
        self.client.connect(self.addr)
        self.chat_connection = ChatNetwork(addr=self.addr)
        self.game_connection = GameNetwork(addr=self.addr)

        self.client.send(f"{username}:{password}".encode('ascii'))
        # self.client.send(password.encode('ascii'))

        header = self.client.recv(1024).decode('ascii')
        if header != "SUCCESS":
            return None, None

        
        #the following two lines have to be in that order
        # self.client.send(str.encode(name))


        new_session = input("Do you want to start a new session? yes, no ")
        self.client.send(new_session.encode('ascii'))

        if new_session == 'no':
            # message = self.client.recv(1024).decode('ascii')
            session_num = input("Enter session number: ")
            self.client.send(session_num.encode('ascii'))

        # If 'NICK' Send Nickname
        # message = client.recv(1024).decode('ascii')
        # nickname = input("Choose your nickname: ")
        

        # reply = self.game_client.recv(5)
        # d = reply.decode().split(":")
        # return int(d[0]), int(d[1])
        # return int(val.decode()) # can be int because will be an int id
        return self.game_connection, self.chat_connection

    def disconnect(self):
        """
        disconnects from the server
        :return: None
        """
        self.client.close()

class GameNetwork:
    def __init__(self, addr):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.client.connect(addr)
        
    def getInitialGameData(self):
        reply = self.client.recv(5)
        d = reply.decode().split(":")
        return int(d[0]), int(d[1])
    
    def send_game(self, data, pick=False):
        """
        sends information to the server

        :param data: str
        :param pick: boolean if should pickle or not
        :return: str
        """
        try:
            data = util.fill_data(data)
            # while (len(data) < 19):
            #     data += ' '
            self.client.send(str.encode(data))

        except socket.error as e:
            print(e)
            raise(e)
            pass

    def receive_game(self):
        reply = self.client.recv(19)
        # print("reply", reply)
        reply = reply.decode()
        return reply
    
    def disconnect(self):
        """
        disconnects from the server
        :return: None
        """
        self.client.close()


class ChatNetwork:
    def __init__(self, addr):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.client.connect(addr)
        # print("sending nickname")
        # print(self.client)
        # self.client.send(name.encode('ascii'))
        # print("sent nickname")
        
    def disconnect(self):
        """
        disconnects from the server
        :return: None
        """
        self.client.close()
    
    def send_chat(self, data, pick=False):
        """
        sends information to the server

        :param data: str
        :param pick: boolean if should pickle or not
        :return: str
        """
        try:
            self.client.send(data.encode('ascii'))
            # while (len(data) < 19):
            #     data += ' '
            # self.game_client.send(str.encode(data))

        except socket.error as e:
            print(e)
            pass
    
    def receive_chat(self):
        try:
            message = self.client.recv(1024).decode('ascii')
            print(message)
            return message
        except:
            # Close Connection When Error
            print("An error occured!")
            # client.close()