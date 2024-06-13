import socket
import threading
import os

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 3490
BUFFER_SIZE = 4096

class TerminalServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = {}
        self.nicknames = {}

    def start(self):
        self.server_socket.bind((SERVER_HOST, SERVER_PORT))
        self.server_socket.listen()
        print(f"Server is running on {SERVER_HOST}:{SERVER_PORT}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Established connection to {client_address}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def broadcast_message(self, message, sender_socket):
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.sendall(message.encode())
                except Exception as e:
                    print(f"Error sending message to {client_socket}: {e}")

    def handle_client(self, client_socket):
        try:
            nickname = client_socket.recv(BUFFER_SIZE).decode().strip()
            self.nicknames[client_socket] = nickname
            self.clients[client_socket] = True
            self.broadcast_message(f"{nickname} joined the chat.\n", client_socket)

            while True:
                message = client_socket.recv(BUFFER_SIZE).decode()
                if message:
                    if message.startswith('/sendimage'):
                        self.receive_image(client_socket)
                    elif message.startswith('/sendfile'):
                        self.receive_file(client_socket)
                    else:
                        self.broadcast_message(f"{nickname}: {message}", client_socket)
                else:
                    raise Exception("Client disconnected")
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.disconnect_client(client_socket)

    def receive_image(self, client_socket):
        try:
            client_socket.sendall("Please select an image file to send.\n".encode())

            image_data = b""
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                image_data += data

            # Process received image_data as needed (e.g., save to disk, broadcast to other clients)
            print(f"Received image data from {self.nicknames[client_socket]}")

        except Exception as e:
            print(f"Error receiving image: {e}")

    def receive_file(self, client_socket):
        try:
            client_socket.sendall("Please select a file to send.\n".encode())

            file_data = b""
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                file_data += data

            # Process received file_data as needed (e.g., save to disk, broadcast to other clients)
            print(f"Received file data from {self.nicknames[client_socket]}")

        except Exception as e:
            print(f"Error receiving file: {e}")

    def disconnect_client(self, client_socket):
        if client_socket in self.clients:
            nickname = self.nicknames.get(client_socket, 'Unknown')
            del self.clients[client_socket]
            del self.nicknames[client_socket]
            client_socket.close()
            self.broadcast_message(f"{nickname} left the chat.\n", None)

if __name__ == "__main__":
    server = TerminalServer()
    server.start()
