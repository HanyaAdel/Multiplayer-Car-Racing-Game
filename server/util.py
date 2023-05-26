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
        message_length = len(message.encode('utf-8'))

        header = message_length.to_bytes(4, byteorder='big')
        client['client'].sendall(header + message.encode('utf-8'))  

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

def receive_data(client):
    header = client.recv(4)
    if not header:
        return

    # Parse the header
    msg_len = int.from_bytes(header[0:4], byteorder="big")

    # Receive the message data
    chunks = []
    bytes_recd = 0
    while bytes_recd < msg_len:
        chunk = client.recv(min(msg_len - bytes_recd,
                            1024))
        if not chunk:
            raise RuntimeError("ERROR")
        chunks.append(chunk)
        bytes_recd += len(chunk)

    data = b"".join(chunks)

    # Print the message
    message = data.decode("utf-8").strip()
    return message


def send_data(data, client):
    message_length = len(data.encode('utf-8'))

    #msg_len = len(message.encode('utf-8'))

    header = message_length.to_bytes(4, byteorder='big')
    client.sendall(header + data.encode('utf-8'))
