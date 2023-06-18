# Multiplayer-Car-Racing-Game

An online multiplayer car racing game with chat and failure recovery

## Demo

https://youtu.be/H486yh9tAXY

## Setting up dependencies

Install python if you don't have it already.

To setup the dependencies for each of the client and server, open a terminal in the component's directory and then run the following command:

``` 
pip install -r requirements.txt
```

## Before running the server

Open [.env_sample](./server/.env_sample) and update the fields' values to match your two databases credentials, and port numbers that you want your server to listen on (make sure that your network interface allows traffic on those ports). Values should be written without quotes.

Rename [.env_sample](./server/.env_sample) to .env

Note that both of the databases should have the same schema as the one in this [link](https://drawsql.app/teams/team-770/diagrams/multiplayer-car-racing-game).

## Before running the game
Open [.env_sample](./client/.env_sample) and update the fields' values to match ther server's IP address, use localhost if the game is running on the same machine as the server, or the local ip address of the server if the server is on the same local network or the public ip address of the server if the server is deployed online (you may need to setup port forwarding on the server for this to work). Update the value of the ports to match those of the server. Values should be written without quotes.

Rename [.env_sample](./client/.env_sample) to .env


## Running the server

Open a new terminal in the [server directory](./server/) and then run the following command:
``` 
python server.py
```

## Running the client

Open a new terminal in the [client directory](./client/) and then run the following command:

``` 
python game.py
```
