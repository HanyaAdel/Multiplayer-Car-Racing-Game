import socket
import threading
from time import sleep
from session import Session
from model import Model

# Connection Data
host = ''

port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
server.bind((host, port))
server.listen()

sessions = []

def parse_username_and_password(data):
        try:
            d = data.split(":")
            return d[0], d[1]
        except:
            pass

def get_session_by_code(code):
    for session in sessions:
        if session.session_code == code:
            return session
    return None
    

def handle_incoming_connection(client, address):
    print("Connected with {}".format(str(address)))
    chat_client, chat_address = server.accept()
    game_client, game_address = server.accept()

    print("created game and chat clients")
    username, password = parse_username_and_password(client.recv(1024).decode('ascii'))
    print("received username", username)
    # password = client.recv(1024).decode('ascii')
    print("received password", password)

    client_id = model.login(username, password)
    if client_id == None:
        client.send("FAILED".encode('ascii'))
        client.close()
        game_client.close()
        chat_client.close()
        print("closing incoming connection handler")
        print("in fail")
        return
    else:
        client.send("SUCCESS".encode('ascii'))
        print("in success")

    # chat_client, chat_address = server.accept()
    # game_client, game_address = server.accept()


    # Request And Store Nickname
    # client.send('NEW_SESSION'.encode('ascii'))
    newSession = client.recv(1024).decode('ascii')
    # newSession.add_client(client=client)
    print(newSession)

    if newSession == 'yes':
        # start new session
        newSession = Session(model=model)
        sessions.append(newSession)
        newSession.add_client(game_client=game_client, chat_client=chat_client, username=username, client_id=client_id)

    if newSession == 'no':
        # client.send('SESSION_NUM'.encode('ascii'))
        sessionCode = client.recv(1024).decode('ascii')
        session = get_session_by_code(code=sessionCode)
        if session == None:
            #TODO
            pass
        else:
            session.add_client(game_client, chat_client, username = username, client_id=client_id)
    
    client.close()
    print("closing incoming connection handler")


# Receiving / Listening Function
def listen():
    while True:
        # Accept Connection
        client, address = server.accept()
        handler_thread = threading.Thread(target=handle_incoming_connection, args=(client, address))
        handler_thread.start()
        sleep(1)
            
model = Model()
listen()