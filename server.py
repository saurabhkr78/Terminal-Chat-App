import socket
import select
import sys

# Constants
BACKLOG = 10
PORT = 3490

# Utility function to get IP address
def get_ip_address(sockaddr):
    return sockaddr[0]

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', PORT))
server_socket.listen(BACKLOG)

print("Server is running...")

# Variables
inputs = [server_socket]
clients = {}
nicked_users = {}
super_users = set()
password = "sherbetlemon"

# Helper functions
def broadcast_message(message, exclude_socket=None):
    for sock in inputs:
        if sock != server_socket and sock != exclude_socket:
            try:
                sock.send(message.encode())
            except Exception as e:
                print(f"Error sending message: {e}")
                sock.close()
                inputs.remove(sock)

def handle_new_connection(server_socket):
    client_socket, client_address = server_socket.accept()
    print(f"Established connection to {get_ip_address(client_address)}")
    client_socket.send("Welcome to the chat!\nEnter username: ".encode())
    inputs.append(client_socket)

def handle_client_message(sock):
    try:
        message = sock.recv(1024).decode().strip()
        if not message:
            raise ConnectionResetError
        
        if sock in nicked_users:
            username = nicked_users[sock]
            if username in super_users:
                if message.startswith("ban "):
                    user_to_ban = message.split(" ", 1)[1]
                    for client, nick in nicked_users.items():
                        if nick == user_to_ban:
                            client.send("You have been banned!\n".encode())
                            client.close()
                            inputs.remove(client)
                            del nicked_users[client]
                            broadcast_message(f"{user_to_ban} has been banned!\n")
                            return
            broadcast_message(f"{username}: {message}\n", sock)
        else:
            if message == password:
                sock.send("Welcome admin! Mention your codename: ".encode())
                super_users.add(sock)
            else:
                nicked_users[sock] = message
                broadcast_message(f"{message} has joined the chat!\n")

    except Exception as e:
        print(f"Error: {e}")
        if sock in nicked_users:
            username = nicked_users[sock]
            broadcast_message(f"{username} has left the chat.\n")
            del nicked_users[sock]
        sock.close()
        inputs.remove(sock)

# Main server loop
while True:
    read_sockets, _, _ = select.select(inputs, [], [])
    for sock in read_sockets:
        if sock == server_socket:
            handle_new_connection(server_socket)
        else:
            handle_client_message(sock)
