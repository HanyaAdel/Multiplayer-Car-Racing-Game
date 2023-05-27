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
W, H = 1100, 600
display_width, display_height = 1350, 600
input_width, input_height = 250, 100
chat_height = 500
max_chat_length = 18
chat_padding = 9

lane_width = W/4
lane_margin = 80
#Background
bgImg = pygame.image.load("new_background.jpeg")
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
car4Img = pygame.image.load('car4.png')
car_width = 49
car_height = 100

enemy_car = pygame.image.load('enemy_car.png')
enemy_car_startx = 0
enemy_car_starty = 0
enemy_car_speed = 5
enemy_car_width = 49
enemy_car_height = 100

game_running = True


def redraw_window(players):
 
    global bg_y1, bg_y2, bg_speed, bgImg, enemy_car_starty
    
    #render the background and adjust its movement
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
        
        #render the car according to player lane
        lane_number = player["lane"]
        if lane_number == 1: 
            WIN.blit(car1Img, (player["x"], player["y"]))
        elif lane_number == 2: 
            WIN.blit(car2Img, (player["x"], player["y"]))
        elif lane_number == 3:
            WIN.blit(car3Img, (player["x"], player["y"]))
        else:
            WIN.blit(car4Img, (player["x"], player["y"]))

            
        #render the player score
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


def main(game_conn, chat_conn):
    
    global players, current_id, server, enemy_car_speed, bg_speed
    
    #get player data from the server
    current_id, num_players,lane, score= game_conn.getInitialGameData()
    lane_number = lane
    
    #calculate the car initial position on the screen according to the player's lane
    x = int((2*lane_number-1)*lane_width/2)
    
    #add the player's data to the players list
    players.append({'id':current_id, 'x':x, 'y':H - car_height, 'lane':lane_number, 'score': score})

    sendThread = threading.Thread(target=sender_thread)
    receiveThread = threading.Thread(target=receiver_thread)
    chatSendThread = threading.Thread(target=write_chat_messages)
    chatReceiveThread = threading.Thread(target=receive_chat_messages)
    sendThread.start()
    receiveThread.start()
    chatSendThread.start()
    chatReceiveThread.start()

    #wait until other players' data are received
    while num_players<len(players):
        continue
    
    # wait until server starts the game timer
    # while game_running == False:
    #     continue
    # # setup the clock, limit to 30fps
    clock = pygame.time.Clock()

    run = True
    
    # fill screen white, to clear old frames
    WIN.fill((192, 192, 192)) 

    #modify to while game_running
    while run:
        clock.tick(60) # 30 fps max
        
        #get the current player from the players list
        player_idx = util.get_player_idx_by_id(id=current_id, players=players)
        player = players[player_idx]

        vel = START_VEL
        if vel <= 1:
            vel = 1

        # get key presses
        keys = pygame.key.get_pressed()

        # movement based on key presses
        if not inputHasMouse() and (keys[pygame.K_LEFT] or keys[pygame.K_a]):
            if player["x"] - vel - PLAYER_RADIUS >= 0:
                player["x"] = player["x"] - vel
                
        if not inputHasMouse() and (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            if player["x"] + vel + PLAYER_RADIUS  <= W:
                player["x"] = player["x"] + vel

        if player["x"] < (lane_number-1)*lane_width or player["x"] > 224+(lane_number-1)*lane_width:
            #if user hits the boundaries
            player["score"] -= 10
            display_message("Boundary hit !! score down!")
            if lane_number == 4:            
                pygame.draw.rect(WIN, (192, 192, 192), (W, chat_height, input_width, input_height))

        #detect collision with enemy car
        enemy_car_shifted_startx = enemy_car_startx + (lane_number-1)*lane_width  
        if enemy_car_starty != None and player["y"] < enemy_car_starty + enemy_car_height:
            if player["x"] > enemy_car_shifted_startx and player["x"] < enemy_car_shifted_startx + enemy_car_width or player["x"] + car_width > enemy_car_shifted_startx and player["x"] + car_width < enemy_car_shifted_startx + enemy_car_width:
                    #run = False
                    # display_message("Game Over !!!")
                    player["score"] -= 10
                    display_message("Collision !! score down!")

        #adjust player score, bg speed, and enemy car speed
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
            
            #if user writes input to chat, receive it
            if inputHasMouse() == True and event.type == pygame.KEYDOWN:
                print("has mouse and key down!!")
                read_chat_input(event)

        #if timer elapsed from the server, show ranking and exit the run
        if game_running == False:
               display_final_ranks(players)
               

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
    #sort players list according to their scores then render the rankings
    sorted_players_asc = sorted(players, key=operator.itemgetter('score'))
    sorted_players = sorted_players_asc[::-1]  
    for i in range(0, len(sorted_players)):
        player = sorted_players[i]
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Rank: " + str(i + 1), True, white)
        WIN.blit(text, (((player["lane"] - 1) * lane_width)+5, 20))
        
def display_final_ranks(players):
    #sort players list according to their scores then render the rankings
    while True:
        sorted_players_asc = sorted(players, key=operator.itemgetter('score'))
        sorted_players = sorted_players_asc[::-1]  
        for i in range(0, len(sorted_players)):
            player = sorted_players[i]
            font = pygame.font.SysFont("comicsansms", 40)
            if player["lane"] == 1:
                text = font.render("Rank: " + str(i + 1), True, (255, 0, 0))
            elif player["lane"] == 2:
                text = font.render("Rank: " + str(i + 1), True, (255, 247, 174))
            elif player["lane"] == 3:
                text = font.render("Rank: " + str(i + 1), True, (255, 255, 255))
            else:
                text = font.render("Rank: " + str(i + 1), True, (148,0,211))
            
            WIN.blit(text, (((player["lane"] - 1) * lane_width)+ lane_width/2 - 50, display_height / 2))
            pygame.display.update()
            #sleep(5)
            
def display_message(msg):
        font = pygame.font.SysFont("comicsansms", 72, True)
        text = font.render(msg, True, (255, 255, 255))
        WIN.blit(text, (700 - text.get_width() // 2, 240 - text.get_height() // 2))
        # self.display_credit()
        pygame.display.update()
        #self.clock.tick(60)
        sleep(1)

def inputHasMouse():
    #check if the mouse is hovering over the chat input area
    (x,y) = pygame.mouse.get_pos()
    return x > W and x < W + input_width and y < H and y > H - input_height
    
    
def read_chat_input(event):

    global message, message_ready
    
    #if user press enter, set message as ready to be sent to the server
    if event.key == pygame.K_RETURN:
            message_ready = True
            pygame.draw.rect(WIN, (192, 192, 192), (W, chat_height, input_width, input_height))
            print("message ready: " + message + "\n")
            
    #if user press backspace, delete the last character and update the displayed input
    if event.key == pygame.K_BACKSPACE:
            message = message[:-1]
            dispaly_input_message(message)
            
    #if user press space, add space to the message
    if event.key == pygame.K_SPACE:
            message += ' '
            dispaly_input_message(message)
            
    #append the user input to the message
    else:
        if str(pygame.key.name(event.key)).isalnum() and len(str(pygame.key.name(event.key))) == 1:
            message += pygame.key.name(event.key)
            dispaly_input_message(message)


def dispaly_input_message(message):
        x, y = W+chat_padding, H-input_height+10
        pygame.draw.rect(WIN, (192, 192, 192), (W, chat_height, input_width, input_height))
        
        #divide the input message into submessages to be displayed in new lines in the 
        #input area if width limit reached
        for i in range(0, len(message), max_chat_length): 
                sub_msg = message[i:i+max_chat_length]
                font = pygame.font.SysFont("arial", 15, True)
                text = font.render(sub_msg, True, (0, 0, 0))
                WIN.blit(text, (x, y))
                y+=25   
                if y > H:
                    pygame.draw.rect(WIN, (192, 192, 192), (W, chat_height, input_width, input_height))
                    y = H-input_height+10
    
     
def display_chat():
        x, y = W+chat_padding, 0
        pygame.draw.rect(WIN, (255, 247, 174), (W, 0, input_width, chat_height))
        # pygame.draw.rect(WIN, (192, 192, 192), (W, 500, 210, 100))
        
        msg = "Group Chat"
        font = pygame.font.SysFont("comicsansms", 20, True)
        text = font.render(msg, True, (0, 0, 0))
        WIN.blit(text, (x, y))
        y+=30

        #for each chat message in list, divide the chat message into submessages to be displayed in new lines in the 
        #chat area if width limit reached
        for msg in messages:
            for i in range(0, len(msg), max_chat_length): 
                sub_msg = msg[i:i+max_chat_length]
                font = pygame.font.SysFont("arial", 15, True)
                text = font.render(sub_msg, True, (0, 0, 0))
                WIN.blit(text, (x, y))
                y+=25   
                if y > H -input_height:
                    pygame.draw.rect(WIN, (255, 247, 174), (W, 0, input_width, chat_height))
                    y = 30

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
    global current_id, game_conn, enemy_car_startx, enemy_car_starty, game_running
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

                if header == "END":
                    print("received end of session message")
                    game_running = False
                    
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