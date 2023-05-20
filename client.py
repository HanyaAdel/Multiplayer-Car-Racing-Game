import socket
import threading

# Choosing Nickname



# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

# Listening to Server and Sending Nickname
def receive():
    while True:
        try:

            message = client.recv(1024).decode('ascii')

            print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            client.close()
            break

# Sending Messages To Server
def write():
    while True:
        message = input('')
        client.send(message.encode('ascii'))



def setup_connection():
        try:
            # Receive Message From Server


            message = client.recv(1024).decode('ascii')
            new_session = input("Do you want to start a new session? yes, no ")
            client.send(new_session.encode('ascii'))

            if new_session == 'no':
                message = client.recv(1024).decode('ascii')
                session_num = input("Enter session number: ")
                client.send(session_num.encode('ascii'))

            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            nickname = input("Choose your nickname: ")
            client.send(nickname.encode('ascii'))

            
            # Starting Threads For Listening And Writing
            receive_thread = threading.Thread(target=receive)
            receive_thread.start()

            write_thread = threading.Thread(target=write)
            write_thread.start()

        except:
            # Close Connection When Error
            print("An error occured!")
            client.close()


setup_connection()