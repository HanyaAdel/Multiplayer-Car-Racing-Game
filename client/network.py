import socket
import  pickle
import util


class Network:
    """
    class to connect, send and recieve information from the server

    need to hardcode the host attirbute to be the server's ip
    """
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.game_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.chat_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chat_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.host = '98.66.137.14'
        self.port = 55555
        self.addr = (self.host, self.port)

    def connect(self, name):
        """
        connects to server and returns the id of the client that connected
        :param name: str
        :return: int reprsenting id
        """
        self.client.connect(self.addr)
        self.chat_client.connect(self.addr)
        self.game_client.connect(self.addr)
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
        print("sending nickname")
        print(self.chat_client)
        self.chat_client.send(name.encode('ascii'))
        print("sent nickname")

        reply = self.game_client.recv(5)
        d = reply.decode().split(":")
        return int(d[0]), int(d[1])
        # return int(val.decode()) # can be int because will be an int id

    def disconnect(self):
        """
        disconnects from the server
        :return: None
        """
        self.client.close()

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
            self.game_client.send(str.encode(data))

        except socket.error as e:
            print(e)
            pass
    
    def send_chat(self, data, pick=False):
        """
        sends information to the server

        :param data: str
        :param pick: boolean if should pickle or not
        :return: str
        """
        try:
            self.chat_client.send(data.encode('ascii'))
            # while (len(data) < 19):
            #     data += ' '
            # self.game_client.send(str.encode(data))

        except socket.error as e:
            print(e)
            pass
    
    def receive_game(self):
        reply = self.game_client.recv(19)
        # print("reply", reply)
        reply = reply.decode()
        return reply
        
    def receive_chat(self):
        try:
            message = self.chat_client.recv(1024).decode('ascii')
            print(message)
            return message
        except:
            # Close Connection When Error
            print("An error occured!")
            # client.close()
