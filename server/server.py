import socket
import threading
from time import sleep
from session import Session
from model import Model
import util

# Connection Data
host = 'localhost'

port = 5555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
server.bind((host, port))
server.listen()

sessions = []


def logged_in(id):
    global sessions
    for session in sessions:
        for player in session.players:
            if player['id'] == id:
                return True
            
    return False



def handle_incoming_connection(client, address):
    print("Connected with {}".format(str(address)))
    chat_client, chat_address = server.accept()
    game_client, game_address = server.accept()

    print("created game and chat clients")
    username, password = util.parse_username_and_password(util.receive_data(client))
    print("received username", username)

    print("received password", password)

    client_id = model.login(username, password)
    
    if client_id == None or logged_in(client_id) == True:
        util.send_data("FAILED", client)
        client.close()
        game_client.close()
        chat_client.close()
        print("closing incoming connection handler")
        print("in fail")
        return
    else:
        util.send_data("SUCCESS", client)
        print("in success")

    newSession = util.receive_data(client)

    print(newSession)

    if newSession == 'yes':
        # start new session
        expected_num_players = int(util.receive_data(client))
        newSession = Session(model=model, expected=expected_num_players)
        code = newSession.session_code
        util.send_data(f"CODE: {code}", client)
        sessions.append(newSession)
        newSession.add_client(game_client=game_client, chat_client=chat_client, username=username, client_id=client_id)
        newSession.game_server.start_sender()

    if newSession == 'no':
        # receive the session code from the client and add the player to that session.
        valid_session = False
        session = None
        while not valid_session:

            sessionCode = util.receive_data(client)
            session = util.get_session_by_code(code=sessionCode, sessions = sessions)
            if session == None :
                util.send_data("FAIL", client)
                #client.send("FAIL".encode('ascii'))
                pass
            elif len(session.players) == 4:
                util.send_data("FULL", client)
            
            elif session and len(session.players) < 4:
                valid_session = True
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