import socket
import threading
import os
import sys

SERVER_HOST = 'localhost'
SERVER_PORT = 3490
BUFFER_SIZE = 4096

class TerminalClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = None

    def connect_to_server(self):
        self.client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("Connected to server.")

    def send_message(self, message):
        try:
            self.client_socket.sendall(message.encode())
        except Exception as e:
            print(f"Error sending message: {e}")
            self.client_socket.close()
            sys.exit()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(BUFFER_SIZE).decode()
                if message:
                    print(message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.client_socket.close()
                sys.exit()

    def send_image(self, image_path):
        try:
            with open(image_path, 'rb') as file:
                image_data = file.read()
                self.client_socket.sendall(b"/sendimage\n")
                self.client_socket.sendall(image_data)
                print(f"Sent image: {image_path}")
        except Exception as e:
            print(f"Error sending image: {e}")

    def send_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
                file_name = os.path.basename(file_path)
                self.client_socket.sendall(f"/sendfile {file_name}\n".encode())
                self.client_socket.sendall(file_data)
                print(f"Sent file: {file_name}")
        except Exception as e:
            print(f"Error sending file: {e}")

    def start_chatting(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()

        self.nickname = input("Enter your nickname: ").strip()
        if not self.nickname:
            print("Nickname cannot be empty.")
            return

        self.send_message(self.nickname)

        while True:
            message = input()

            if message.lower() == 'exit':
                break
            elif message.startswith('/sendimage'):
                _, image_path = message.split(maxsplit=1)
                self.send_image(image_path.strip())
            elif message.startswith('/sendfile'):
                _, file_path = message.split(maxsplit=1)
                self.send_file(file_path.strip())
            else:
                self.send_message(message)

        self.client_socket.close()

if __name__ == "__main__":
    client = TerminalClient()
    client.connect_to_server()
    client.start_chatting()
