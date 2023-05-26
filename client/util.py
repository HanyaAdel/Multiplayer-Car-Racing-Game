MAX_SIZE = 19

def fill_data(data):
    while len(data) < MAX_SIZE:
        data += ' '
    return data

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

    
def parse_location(data):
        try:
            d = data.split(":")
            return int(d[1]), int(d[2]), int(d[3]), int(d[4])
        except:
            pass
def parse_leaving_player(data):
    try:
        d = data.split(":")
        return int(d[1])
    except:
        pass    

def parse_obstacle_location(data):
    try:
        d = data.split(":")
        return int(d[1])
    except:
        pass        

def getHeader(data):
        try:
            d = data.split(":")
            return d[0]
        except:
            pass

def get_player_idx_by_id(id, players):
    for player_idx, player in enumerate(players):
        if player['id'] == id:
            return player_idx
    
    return -1