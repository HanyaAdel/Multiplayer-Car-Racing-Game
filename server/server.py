import socket
import threading
from time import sleep
from session import Session
from model import Model
import util
import os
from dotenv import load_dotenv
load_dotenv()

# Connection Data
host = ''

connection_port = int(os.getenv('CONNECTION_PORT'))
game_port = int(os.getenv('GAME_PORT'))

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
server.bind((host, connection_port))
server.listen()

game_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
game_server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
game_server.bind((host, game_port))
game_server.listen()    
# sessions = []


def logged_in(id):
    # global sessions
    for session in Session.sessions:
        for player in session.players:
            if player['id'] == id:
                return True
            
    return False



def handle_incoming_connection(client, address):
    print("Connected with {}".format(str(address)))

    chat_client, chat_address = game_server.accept()
    game_client, game_address = game_server.accept()

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
        Session.sessions.append(newSession)
        newSession.add_client(game_client=game_client, chat_client=chat_client, username=username, client_id=client_id)
        newSession.game_server.start_sender()

    if newSession == 'no':
        # receive the session code from the client and add the player to that session.
        valid_session = False
        session = None
        while not valid_session:

            sessionCode = util.receive_data(client)
            print("sessions: ", Session.sessions)
            session = util.get_session_by_code(code=sessionCode, sessions = Session.sessions)
            if session == None :
                util.send_data("FAIL", client)
                pass
            elif len(session.players) >= session.expected or (session.started and model.getPlayerScore(client_id,sessionCode) == None):
                util.send_data("FULL", client)
            
            else:
                util.send_data("SUCCESS", client)
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
        sleep(3)
            
model = Model()
listen()