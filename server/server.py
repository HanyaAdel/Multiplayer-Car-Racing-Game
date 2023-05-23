import socket
import threading
from session import Session

# Connection Data
host = ''

port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
server.bind((host, port))
server.listen()

sessions = []

def handle_incoming_connection(client, chat_client, game_client, address):
    print("Connected with {}".format(str(address)))

    # Request And Store Nickname
    # client.send('NEW_SESSION'.encode('ascii'))
    newSession = client.recv(1024).decode('ascii')
    # newSession.add_client(client=client)
    print(newSession)

    if newSession == 'yes':
        # start new session
        newSession = Session(id=len(sessions))
        sessions.append(newSession)
        newSession.add_client(game_client=game_client, chat_client=chat_client)

    if newSession == 'no':
        # client.send('SESSION_NUM'.encode('ascii'))
        sessionNum = client.recv(1024).decode('ascii')
        session = sessions[int(sessionNum)]
        session.add_client(game_client, chat_client)
    
    client.close()
    print("closing incoming connection handler")

# Receiving / Listening Function
def listen():
    while True:
        # Accept Connection
        client, address = server.accept()
        chat_client, chat_address = server.accept()
        game_client, game_address = server.accept()
        handler_thread = threading.Thread(target=handle_incoming_connection, args=(client, chat_client, game_client, address))
        handler_thread.start()
            
listen()