import socket
import threading

# Choose a nickname
nickname = input("Choose your nickname: ")

# Client setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 12345))

# Listening to server and sending nickname
def receive():
    while True:
        try:
            # Receive message from server
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                print(message)
        except:
            # Close connection when error occurs
            print("An error occurred!")
            client.close()
            break

# Sending messages to server
def write():
    while True:
        message = f'{nickname}: {input("")}'
        client.send(message.encode('utf-8'))

# Starting threads for receiving and writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
