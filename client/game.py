# small network game that has differnt blobs
# moving around the screen

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from network import Network
import random
import threading
import os
pygame.font.init()

# Constants
PLAYER_RADIUS = 10
START_VEL = 9
BALL_RADIUS = 5

W, H = 500, 500

NAME_FONT = pygame.font.SysFont("comicsans", 20)
TIME_FONT = pygame.font.SysFont("comicsans", 30)
SCORE_FONT = pygame.font.SysFont("comicsans", 26)

COLORS = [(255,0,0), (255, 128, 0), (255,255,0), (128,255,0),(0,255,0),(0,255,128),(0,255,255),(0, 128, 255), (0,0,255), (0,0,255), (128,0,255),(255,0,255), (255,0,128),(128,128,128), (0,0,0)]

# Dynamic Variables
current_id = 0
server = None
game_conn = None
chat_conn = None
players = []

# FUNCTIONS
def convert_time(t):
    """
    converts a time given in seconds to a time in
    minutes

    :param t: int
    :return: string
    """
    if type(t) == str:
        return t

    if int(t) < 60:
        return str(t) + "s"
    else:
        minutes = str(t // 60)
        seconds = str(t % 60)

        if int(seconds) < 10:
            seconds = "0" + seconds

        return minutes + ":" + seconds


def redraw_window(players):
    """
    draws each frame
    :return: None
    """
    WIN.fill((255,255,255)) # fill screen white, to clear old frames
    
        # draw all the orbs/balls
    # for ball in balls:
    #     pygame.draw.circle(WIN, ball[2], (ball[0], ball[1]), BALL_RADIUS)


    # draw each player in the list
    for player in players:
        pygame.draw.circle(WIN, (255, 0, 0), (player["x"], player["y"]), PLAYER_RADIUS )
        # render and draw name for each player
        # text = NAME_FONT.render(p["name"], 1, (0,0,0))
        # WIN.blit( (p["x"] - text.get_width()/2, p["y"] - text.get_height()/2))

    # draw scoreboard
    # sort_players = list(reversed(sorted(players, key=lambda x: players[x]["score"])))
    # title = TIME_FONT.render("Scoreboard", 1, (0,0,0))
    # start_y = 25
    # x = W - title.get_width() - 10
    # WIN.blit(title, (x, 5))

    # ran = min(len(players), 3)
    # for count, i in enumerate(sort_players[:ran]):
    #     text = SCORE_FONT.render(str(count+1) + ". " + str(players[i]["name"]), 1, (0,0,0))
    #     WIN.blit(text, (x, start_y + count * 20))

    # # draw time
    # #text = TIME_FONT.render("Time: " + convert_time(game_time), 1, (0,0,0))
    # WIN.blit(text,(10,10))
    # # draw score
    # text = TIME_FONT.render("Score: " + str(round(score)),1,(0,0,0))
    # WIN.blit(text,(10,15 + text.get_height()))


def main(game_conn, chat_conn):
    """
    function for running the game,
    includes the main loop of the game

    :param players: a list of dicts represting a player
    :return: None
    """
    global players, current_id, server

    # # start by connecting to the network
    # server = Network()
    # # current_id, num_players = server.connect(username)
    # game_conn, chat_conn = server.connect(username, password)
    current_id, num_players = game_conn.getInitialGameData()
    players.append({'id':current_id, 'x':0, 'y':0})
    # for i in range(current_id+1):
    #     players.append({'id':i, 'x':0, 'y':0})

    # players = server.send("get")


    sendThread = threading.Thread(target=sender_thread)
    receiveThread = threading.Thread(target=receiver_thread)
    chatSendThread = threading.Thread(target=write)
    chatReceiveThread = threading.Thread(target=receive)
    sendThread.start()
    receiveThread.start()
    chatSendThread.start()
    chatReceiveThread.start()

    while num_players<len(players):
        continue
    # setup the clock, limit to 30fps
    clock = pygame.time.Clock()

    run = True

    while run:
        clock.tick(60) # 30 fps max
        player_idx = get_player_idx_by_id(id=current_id)
        player = players[player_idx]
        # print(player)
        # print(players)

        vel = START_VEL
        if vel <= 1:
            vel = 1

        # get key presses
        keys = pygame.key.get_pressed()

        data = ""
        # movement based on key presses
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if player["x"] - vel - PLAYER_RADIUS >= 0:
                player["x"] = player["x"] - vel

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if player["x"] + vel + PLAYER_RADIUS  <= W:
                player["x"] = player["x"] + vel

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if player["y"] - vel - PLAYER_RADIUS  >= 0:
                player["y"] = player["y"] - vel

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if player["y"] + vel + PLAYER_RADIUS <= H:
                player["y"] = player["y"] + vel


        for event in pygame.event.get():
            # if user hits red x button close window
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # if user hits a escape key close program
                if event.key == pygame.K_ESCAPE:
                    run = False


        # redraw window then update the frame
        redraw_window(players)
        pygame.display.update()


    server.disconnect()
    game_conn.disconnect()
    chat_conn.disconnect()
    pygame.quit()
    quit()

def sender_thread():
    global current_id, game_conn
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        try:
            player_idx = get_player_idx_by_id(id=current_id)
            player = players[player_idx]
            reply = f"LOCATION: {player['id']}:{player['x']}:{player['y']}"
            game_conn.send_game(reply)
        except:
            print("error")
            break

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

def get_player_idx_by_id(id):
    global players
    for player_idx, player in enumerate(players):
        if player['id'] == id:
            return player_idx
    
    return -1
def receiver_thread():
    global current_id, game_conn
    # clock = pygame.time.Clock()
    while True:
        try:
            data = game_conn.receive_game()
            if not data:
                # print("empty reply")
                #server.send("Goodbye")
                continue
            else:
                reply = data
                header = getHeader(reply)
                if (header == "LOCATION"):
                    id, x, y = parse_location(reply)
                    player_idx = get_player_idx_by_id(id=id)
                    if id == current_id:
                        continue
                    elif player_idx == -1:
                        players.append({'id':id, 'x':x, 'y':y})
                    else:
                        players[player_idx]['x'] = x
                        players[player_idx]['y'] = y
                    

                if header == "LEFT":
                    id = parse_leaving_player(reply)
                    print("player ", id, " left the game")
                    print(players)
                    deleted_player_idx = get_player_idx_by_id(id)
                    if (deleted_player_idx != -1):
                        del players[deleted_player_idx]
                    elif(deleted_player_idx == -1):
                            print("got -1 in getplayeridxbyid")
                            pass
        except:
            break
    print("game receive closed")

def receive():
    global chat_conn
    while True:
        try:
            message = chat_conn.client.recv(1024).decode()
            print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            chat_conn.client.close()
            break

# Sending Messages To Server
def write():
    global chat_conn
    while True:
        message = input('')
        chat_conn.client.send(message.encode('ascii'))


# get users name
username, password = "", ""
while True:
    username = input ("Please enter your username")
    password = input ("Please enter your password")
    if len(password) == 0 or len(username) == 0:
        print("Error, password cannot be empty")
    else: 
        server = Network()
        game_conn, chat_conn = server.connect(username, password)

        if (not game_conn or not chat_conn):
            print("Error, incorrect username or password")
        else:            
            break

    # name = input("Please enter your name: ")
    # if  len(email) == 0:
    #     break
    # else:
    #     print("Error, this username is not allowed (must be between 1 and 19 characters [inclusive])")

# make window start in top left hand corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,30)

# setup pygame window
WIN = pygame.display.set_mode((W,H))
pygame.display.set_caption("Blobs")

# start game
main(game_conn, chat_conn)