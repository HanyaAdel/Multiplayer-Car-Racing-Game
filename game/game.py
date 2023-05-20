# small network game that has differnt blobs
# moving around the screen

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from client import Network
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
players = []
# balls = []

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


def main(name):
    """
    function for running the game,
    includes the main loop of the game

    :param players: a list of dicts represting a player
    :return: None
    """
    global players, current_id, server

    # start by connecting to the network
    server = Network()
    current_id = server.connect(name)
    for i in range(current_id+1):
        players.append({'id':i, 'x':0, 'y':0})

    # players = server.send("get")


    sendThread = threading.Thread(target=sender_thread)
    receiveThread = threading.Thread(target=receiver_thread)
    sendThread.start()
    receiveThread.start()


    # setup the clock, limit to 30fps
    clock = pygame.time.Clock()

    run = True

    while run:
        clock.tick(60) # 30 fps max
        player = players[current_id]
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

        # data = str(current_id) + " " +str(player["x"]) + " " + str(player["y"])
        data = player

        # send data to server and recieve back all players information
        # players = server.send(data, True)

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
    pygame.quit()
    quit()

def sender_thread():
    global current_id, server
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        player = players[current_id]
        reply = f"LOCATION: {player['id']}:{player['x']}:{player['y']}"
        server.send(reply)

def parse_location(data):
        try:
            d = data.split(":")
            return int(d[1]), int(d[2]), int(d[3])
        except:
            pass
def parse_left(data):
    try:
        d = data.split(":")
        return d[1]
    except:
        pass    

def getHeader(data):
        try:
            d = data.split(":")
            return d[0]
        except:
            pass

def get_player_idx_by_id(players, id):
    for player_idx, player in enumerate(players):
        if player['id'] == id:
            return player_idx
    
    return -1
def receiver_thread():
    global current_id, server
    # clock = pygame.time.Clock()
    while True:
        try:
            data = server.receive()
            if not data:
                print("empty reply")
                #server.send("Goodbye")
                continue
            else:
                reply = data
                header = getHeader(reply)
                if (header == "LOCATION"):
                    id, x, y = parse_location(reply)
                    player_idx = get_player_idx_by_id(players=players,id=id)
                    if player_idx == -1:
                        players.append({'id':id, 'x':x, 'y':y})
                    else:
                        players[player_idx]['x'] = x
                        players[player_idx]['y'] = y
                    

                if header == "LEFT":
                    id = parse_left(reply)
                    print("player ", id, " left the game")

                    deleted_player_idx = get_player_idx_by_id(players, id)
                    del players[deleted_player_idx]
        except:
            break


# get users name
while True:
     name = input("Please enter your name: ")
     if  0 < len(name) < 20:
         break
     else:
         print("Error, this name is not allowed (must be between 1 and 19 characters [inclusive])")

# make window start in top left hand corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,30)

# setup pygame window
WIN = pygame.display.set_mode((W,H))
pygame.display.set_caption("Blobs")

# start game
main(name)