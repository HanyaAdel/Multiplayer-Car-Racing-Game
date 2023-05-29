import socket
import  pickle
import util

#HOST = 'localhost'
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


        util.send_data(f"{username}:{password}", self.client)

        header = util.receive_data(self.client)
        if header != "SUCCESS":
            print("Login failed, already logged in or incorrect username or password")
            return None, None

        new_session = ""
        while (new_session != "yes" and new_session != "no" ):
            new_session = input("Do you want to start a new session? enter yes or no \n")
            new_session = new_session.lower()

        util.send_data(new_session, self.client)

        if new_session == 'yes':
            num_players = input("Enter number of players (max 4)")
            util.send_data(num_players,self.client)
            session_code = util.receive_data(self.client)
            print (session_code)
        

        if new_session == 'no':
            valid_session = False
            while not valid_session:
                session_num = input("Enter session number: ")
                util.send_data(session_num, self.client)
                header = util.receive_data(self.client)
                print (header)
                if header != 'FAIL' and header != "FULL":
                    valid_session = True
                elif header == "FULL":
                    print("Session is full. Please enter another session number\n")

        

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
        reply = util.receive_data(self.client)
        print("message received: ", reply)
        d = reply.split(":")
        return int(d[0]), int(d[1]), int(d[2]), int(d[3])
    
    def send_game(self, data, pick=False):
        """
        sends information to the server

        :param data: str
        :param pick: boolean if should pickle or not
        :return: str
        """
        try:

            util.send_data(data, self.client)

        except socket.error as e:
            print(e)
            raise(e)

    def receive_game(self):

        reply = util.receive_data(self.client)
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
            util.send_data(data, self.client)

        except socket.error as e:
            print(e)
            pass
    
    def receive_chat(self):
        try:
            message = util.receive_data(self.client)
            print(message)
            return message
        except:
            # Close Connection When Error
            print("An error occured!")
