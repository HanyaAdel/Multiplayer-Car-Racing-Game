# small network game that has differnt blobs
# moving around the screen
from time import sleep
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from network import Network
import random
import threading
import os
import util
import operator

pygame.font.init()

# Constants
PLAYER_RADIUS = 10
START_VEL = 9
BALL_RADIUS = 5
BUFFER_SIZE = 1024
W, H = 1300, 600
display_width, display_height = 1500, 600
chat_width, chat_height = 200, 100
max_chat_length = 18

lane_width = W/3
lane_margin = 80
#Background
bgImg = pygame.image.load("background.jpg")
bg_x1 = 0
bg_x2 = 0
bg_y1 = 0
bg_y2 = -600
bg_speed = 3
render_bg = False


#clock 
clock = pygame.time.Clock()

NAME_FONT = pygame.font.SysFont("comicsans", 20)
TIME_FONT = pygame.font.SysFont("comicsans", 30)
SCORE_FONT = pygame.font.SysFont("comicsans", 26)

COLORS = [(255,0,0), (255, 128, 0), (255,255,0), (128,255,0),(0,255,0),(0,255,128),(0,255,255),(0, 128, 255), (0,0,255), (0,0,255), (128,0,255),(255,0,255), (255,0,128),(128,128,128), (0,0,0)]
white = (255, 255, 255)

# Dynamic Variables
current_id = 0
server = None
game_conn = None
chat_conn = None
players = []
messages = []
message = ""
message_ready = False

car1Img = pygame.image.load('car1.png')
car2Img = pygame.image.load('car2.png')
car3Img = pygame.image.load('car3.png')
car_width = 49
car_height = 100

enemy_car = pygame.image.load('enemy_car.png')
enemy_car_startx = 0
enemy_car_starty = 0
enemy_car_speed = 5
enemy_car_width = 49
enemy_car_height = 100

game_running = False



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
    global bg_y1, bg_y2, bg_speed, bgImg, enemy_car_starty
    
    WIN.blit(bgImg, (bg_x1, bg_y1))
    WIN.blit(bgImg, (bg_x2, bg_y2))

    bg_y1 += bg_speed
    bg_y2 += bg_speed

    if bg_y1 >= H:
            bg_y1 = -600

    if bg_y2 >= H:
           bg_y2 = -600

    # draw each player in the list
    for player in players:
        #pygame.draw.circle(WIN, (255, 0, 0), (player["x"], player["y"]), PLAYER_RADIUS )
        
        #render care according to player
        lane_number = player["lane"]
        if lane_number == 1: 
            WIN.blit(car1Img, (player["x"], player["y"]))
        elif lane_number == 2: 
            WIN.blit(car2Img, (player["x"], player["y"]))
        else:
            WIN.blit(car3Img, (player["x"], player["y"]))
            
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Score : " + str(player["score"]), True, white)
        # text = font.render("Score : " + str(score), True, white)
        WIN.blit(text, ((lane_number - 1) * lane_width, 0))
        
        #render enemy car
        if enemy_car_startx != 0 and enemy_car_starty != None:
            WIN.blit(enemy_car, (enemy_car_startx + (lane_number - 1) * lane_width , enemy_car_starty))
    
    
    display_ranks(players)
    
    #update enemy car y location
    if(enemy_car_starty != None):
        enemy_car_starty+= enemy_car_speed
        if enemy_car_starty >= H:
            enemy_car_starty = None

        
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
    global players, current_id, server, enemy_car_speed, bg_speed
    
    #private score for each player to be sent to the server
    current_id, num_players,lane, score= game_conn.getInitialGameData()
    lane_number = lane
    print("lane no: ",lane_number)
    x = int((2*lane_number-1)*lane_width/2)
    # need to add 'score' and 'name' keys 
    players.append({'id':current_id, 'x':x, 'y':H - car_height, 'lane':lane_number, 'score': score})

    sendThread = threading.Thread(target=sender_thread)
    receiveThread = threading.Thread(target=receiver_thread)
    chatSendThread = threading.Thread(target=write_chat_messages)
    chatReceiveThread = threading.Thread(target=receive_chat_messages)
    sendThread.start()
    receiveThread.start()
    chatSendThread.start()
    chatReceiveThread.start()

    while num_players<len(players):
        continue
    
    # wait until server starts the game timer
    # while game_running == False:
    #     continue
    # # setup the clock, limit to 30fps
    clock = pygame.time.Clock()

    run = True
    WIN.fill((192, 192, 192)) # fill screen white, to clear old frames

    #modify to while game_running
    while run:
        clock.tick(60) # 30 fps max
        player_idx = util.get_player_idx_by_id(id=current_id, players=players)
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
        if not inputHasMouse() and (keys[pygame.K_LEFT] or keys[pygame.K_a]):
            if player["x"] - vel - PLAYER_RADIUS >= 0:
                player["x"] = player["x"] - vel
                
        if not inputHasMouse() and (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            if player["x"] + vel + PLAYER_RADIUS  <= W:
                player["x"] = player["x"] + vel

        if player["x"] < 80+(lane_number-1)*lane_width or player["x"] > 360+(lane_number-1)*lane_width:
            #if user hits the boundaries
            player["score"] -= 10
            display_message("Boundary hit !! score down!")
            
            
        enemy_car_shifted_startx = enemy_car_startx + (lane_number-1)*lane_width  
        if enemy_car_starty != None and player["y"] < enemy_car_starty + enemy_car_height:
            if player["x"] > enemy_car_shifted_startx and player["x"] < enemy_car_shifted_startx + enemy_car_width or player["x"] + car_width > enemy_car_shifted_startx and player["x"] + car_width < enemy_car_shifted_startx + enemy_car_width:
                    #run = False
                    # display_message("Game Over !!!")
                    player["score"] -= 10
                    display_message("Collision !! score down!")

        player["score"] += 1
        if (player["score"] % 100 == 0):
            if enemy_car_speed < 30:
                enemy_car_speed += 1
            if bg_speed < 30:
                bg_speed += 1

        for event in pygame.event.get():
            # if user hits red x button close window
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # if user hits a escape key close program
                if event.key == pygame.K_ESCAPE:
                    run = False
            if inputHasMouse() == True and event.type == pygame.KEYDOWN:
                print("has mouse and key down!!")
                read_chat_input(event)

        #if timer elapsed from the server, show ranking and exit the run
        # if keys[pygame.K_0] == True:
        #         display_ranks(players)
        #         run = False

        # redraw window then update the frame
        redraw_window(players)
        display_chat()
        pygame.display.update()
        clock.tick(60)
        
    print("exited the run")
    server.disconnect()
    game_conn.disconnect()
    chat_conn.disconnect()
    pygame.quit()
    quit()


def display_ranks(players):
    #sort
    sorted_players = sorted(players, key=operator.itemgetter('score'))
    for i in range(0, len(sorted_players)):
        player = sorted_players[i]
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Rank: " + str(i + 1), True, white)
        WIN.blit(text, (((player["lane"] - 1) * lane_width) + 250, 0))
        
 
            
def display_message(msg):
        font = pygame.font.SysFont("comicsansms", 72, True)
        text = font.render(msg, True, (255, 255, 255))
        WIN.blit(text, (700 - text.get_width() // 2, 240 - text.get_height() // 2))
        # self.display_credit()
        pygame.display.update()
        #self.clock.tick(60)
        sleep(1)

def inputHasMouse():
    (x,y) = pygame.mouse.get_pos()
    return x > W and x < W + chat_width and y < H and y > H - chat_height
    
    
def read_chat_input(event):

    global message, message_ready
     
    if event.key == pygame.K_RETURN:
            message_ready = True
            pygame.draw.rect(WIN, (192, 192, 192), (W - 10, 500, 210, 100))
            print("message ready: " + message + "\n")
    if event.key == pygame.K_BACKSPACE:
            message = message[:-1]
            dispaly_input_message(message)
    if event.key == pygame.K_SPACE:
            message += ' '
            dispaly_input_message(message)
    else:
        if str(pygame.key.name(event.key)).isalnum() and len(str(pygame.key.name(event.key))) == 1:
            message += pygame.key.name(event.key)
            dispaly_input_message(message)


def dispaly_input_message(message):
        x, y = W, H-chat_height+10
        pygame.draw.rect(WIN, (192, 192, 192), (W - 10, 500, 210, 100))
        
        for i in range(0, len(message), max_chat_length): 
                sub_msg = message[i:i+max_chat_length]
                font = pygame.font.SysFont("arial", 15, True)
                text = font.render(sub_msg, True, (0, 0, 0))
                WIN.blit(text, (x, y))
                y+=25   
                if y > H:
                    pygame.draw.rect(WIN, (192, 192, 192), (W - 10, 500, 210, 100))
                    y = H-chat_height+10
    
     
def display_chat():
        x, y = 1300, 0
        pygame.draw.rect(WIN, (255, 247, 174), (W - 10, 0, 210, 500))
        # pygame.draw.rect(WIN, (192, 192, 192), (W - 10, 500, 210, 100))
        
        msg = "Group Chat"
        font = pygame.font.SysFont("comicsansms", 20, True)
        text = font.render(msg, True, (0, 0, 0))
        WIN.blit(text, (x, y))
        y+=30

        # msg[i:i+max_len] for i in range(0, len(msg), max_len)
        for msg in messages:
            for i in range(0, len(msg), max_chat_length): 
                sub_msg = msg[i:i+max_chat_length]
                font = pygame.font.SysFont("arial", 15, True)
                text = font.render(sub_msg, True, (0, 0, 0))
                WIN.blit(text, (x, y))
                y+=25   
                if y > H -chat_height:
                    pygame.draw.rect(WIN, (255, 247, 174), (W - 10, 0, 210, 500))
                    y = 30
        # self.display_credit()
        # pygame.display.update()
        # # self.clock.tick(60)
        # sleep(1)

def sender_thread():
    global current_id, game_conn
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        try:
            player_idx = util.get_player_idx_by_id(id=current_id, players=players)
            player = players[player_idx]
            reply = f"LOCATION: {player['id']}:{player['x']}:{player['y']}:{player['score']}"
            game_conn.send_game(reply)
        except:
            print("error")
            break

def receiver_thread():
    global current_id, game_conn, enemy_car_startx, enemy_car_starty
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
                header = util.getHeader(reply)
                if (header == "LOCATION"):
                    id, x, y, lane, score = util.parse_location(reply)
                    player_idx = util.get_player_idx_by_id(id=id, players=players)
                    if id == current_id:
                        continue
                    elif player_idx == -1:
                        # need to add 'score' and 'name' keys 
                        players.append({'id':id, 'x':x, 'y':y, 'lane':lane, 'score': score})
                    else:
                        players[player_idx]['x'] = x
                        players[player_idx]['y'] = y
                        players[player_idx]['lane'] = lane
                        players[player_idx]['score'] = score
                    

                if header == "LEFT":
                    id = util.parse_leaving_player(reply)
                    print("player ", id, " left the game")
                    print(players)
                    deleted_player_idx = util.get_player_idx_by_id(id, players=players)
                    if (deleted_player_idx != -1):
                        del players[deleted_player_idx]
                    elif(deleted_player_idx == -1):
                            print("got -1 in getplayeridxbyid")
                            pass
                if header == "OBSTACLE":
                    enemy_car_startx = util.parse_obstacle_location(reply)
                    enemy_car_starty = 0
                    print("obstacle: ",enemy_car_startx)
                    
                # add message for game start (HEADER = GAME_STARTED)
                    # set game_running to True
                    
                # add message for game end (HEADER = GAME_ENDED)
                    # set game_running to False

        except:
            break
    print("game receive closed")

def receive_chat_messages():
    global chat_conn
    while True:
        try:
            header = chat_conn.client.recv(4)
            if not header:
                break

            # Parse the header
            msg_len = int.from_bytes(header[0:4], byteorder="big")

            # Receive the message data
            chunks = []
            bytes_recd = 0
            while bytes_recd < msg_len:
                chunk = chat_conn.client.recv(min(msg_len - bytes_recd,
                                    BUFFER_SIZE))
                if not chunk:
                    raise RuntimeError("ERROR")
                chunks.append(chunk)
                bytes_recd += len(chunk)

            data = b"".join(chunks)

            # Print the message
            message = data.decode("utf-8").strip()
            messages.append(message)
            print(message)            
        except:
            # Close Connection When Error
            print("An error occured!")
            chat_conn.client.close()
            break

# Sending Messages To Server
def write_chat_messages():
    global chat_conn, message, message_ready
    while True:
        #send message from gui not terminal
        #message = input('')
        if(message_ready):
            util.send_data(message, chat_conn.client)
            message_ready = False
            message = ""


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

# make window start in top left hand corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,30)

# setup pygame window
WIN = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Blobs")

# start game
main(game_conn, chat_conn)