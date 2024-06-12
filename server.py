import socket
import threading

# Server setup
host = '127.0.0.1'  # Localhost
port = 12345        # Arbitrary non-privileged port

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_socket.bind((host, port))

# Listen for incoming connections (5 is the max number of queued connections)
server_socket.listen(5)

clients = []
nicknames = []

# Broadcast function to send messages to all clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Function to handle each client
def handle_client(client):
    while True:
        try:
            # Receive message from client
            message = client.recv(1024)
            broadcast(message)
        except:
            # Remove and close the client connection
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} has left the chat.'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# Main function to receive clients
def receive_clients():
    while True:
        # Accept a new connection
        client, address = server_socket.accept()
        print(f'Connected with {str(address)}')

        # Request and store nickname
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname of the client is {nickname}')
        broadcast(f'{nickname} has joined the chat!'.encode('utf-8'))
        client.send('Connected to the server!'.encode('utf-8'))

        # Start a new thread to handle the client
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

print('Server is listening...')
receive_clients()
