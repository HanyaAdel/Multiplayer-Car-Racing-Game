import socket
import  pickle


class Network:
    """
    class to connect, send and recieve information from the server

    need to hardcode the host attirbute to be the server's ip
    """
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        #self.client.settimeout(10.0)
        self.host = '20.111.24.134'
        self.port = 55555
        self.addr = (self.host, self.port)

    def connect(self, name):
        """
        connects to server and returns the id of the client that connected
        :param name: str
        :return: int reprsenting id
        """
        self.client.connect(self.addr)
        # self.client.send(str.encode(name))
        val = self.client.recv(1)
        return int(val.decode()) # can be int because will be an int id

    def disconnect(self):
        """
        disconnects from the server
        :return: None
        """
        self.client.close()

    def send(self, data, pick=False):
        """
        sends information to the server

        :param data: str
        :param pick: boolean if should pickle or not
        :return: str
        """
        try:
            # if pick:
            #     self.client.send(pickle.dumps(data))
            # else:
            while (len(data) < 19):
                data += ' '
            self.client.send(str.encode(data))

            # reply = self.client.recv(2048*4)
            # try:
            #     reply = pickle.loads(reply)
            # except Exception as e:
            #     print(e)

            # return reply
        except socket.error as e:
            # print(e)
            pass
    
    def receive(self):
        try:
            reply = self.client.recv(19)
            print("reply", reply)
            # reply = pickle.loads(reply)
            reply = reply.decode()
        except Exception as e:
            print(e)
        
        return reply

