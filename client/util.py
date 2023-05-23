MAX_SIZE = 19

def fill_data(data):
    while len(data) < MAX_SIZE:
        data += ' '
    return data