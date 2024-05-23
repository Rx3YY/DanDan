import socket
import time

def send_command(command):
    server_address = ('10.122.227.179', 6000)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)
        sock.sendall(command.encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        print(f"Received response: {response}")

if __name__ == "__main__":
    while True:
        send_command("ONLINE")
        time.sleep(5)
