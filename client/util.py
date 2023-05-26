MAX_SIZE = 19

def fill_data(data):
    while len(data) < MAX_SIZE:
        data += ' '
    return data


def parse_location(data):
        try:
            d = data.split(":")
            return int(d[1]), int(d[2]), int(d[3])
        except:
            pass
def parse_leaving_player(data):
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