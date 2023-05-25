def parse_username_and_password(data):
        try:
            d = data.split(":")
            return d[0], d[1]
        except:
            pass

def get_session_by_code(code, sessions):
    for session in sessions:
        if session.session_code == code:
            return session
    return None

def broadcast(message, clients):
    for client in clients:
        client['client'].send(str.encode(message))

def get_client_idx_by_socket(client, clients):
    for client_idx, client_itr in enumerate(clients):
        if client_itr['client'] == client:
            return client_idx  
    return -1

def get_player_idx_by_id(id, players):
    for player_idx, player in enumerate(players):
        if player['id'] == id:
            return player_idx
    return -1