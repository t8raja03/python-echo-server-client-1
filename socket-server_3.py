import threading
import socket
from os import system

## Socketin konfiguraatio:
PORT = 23456
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

## Globaaleja muuttujia:
DISCONNECT_MESSAGE = ">X<"   ## Tällä viestillä katkaistaan yhteys
FORMAT = 'iso8859_10'               ## utf_8 aiheutti virheitä öökkösten kanssa
H_LEN = 8
H_USER = 16

clients = []


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

class Client:
    def __init__(self, conn, addr):
        self.connection = conn
        self.address, self.port = addr

class Message:
    def __init__(self, user, length, message):
        self.user = user
        self.length = length
        self.message = message

def read_message(conn):
    try:
        user = conn.recv(H_USER).decode(FORMAT).strip()
        msg_len = int(conn.recv(H_LEN).decode(FORMAT).strip())
        msg = conn.recv(msg_len).decode(FORMAT)
        message = Message(user, msg_len, msg)
        return message

    except ValueError or ConnectionResetError:
        return Message(user, len(DISCONNECT_MESSAGE), DISCONNECT_MESSAGE)




def client_thread(client):
    conn = client.connection
    addr = client.address

    print(f"[+] {addr} connected")
    print(f"[i] {len(clients)} client(s) active")

    while True:
        message = read_message(conn)
        forward_message(message, client)
        if message.message == DISCONNECT_MESSAGE:
            print(f"[-] {addr} disconnected")
            clients.remove(client)
            print(f"[i] {len(clients)} client(s) active")
            return
        print(f"{message.user} @ [{addr}] : {message.message} ")


def forward_message(msg, client):
    for c in clients:
        if c != client:
            header_user = f"{msg.user:<{H_USER}}".encode(FORMAT)
            header_len = f"{msg.length:<{H_LEN}}".encode(FORMAT)
            message = header_user + header_len + msg.message.encode(FORMAT)
            c.connection.sendall(message)
    


def start():
    server.listen()
    print(f"Listening at {SERVER}:{PORT}")

    while True:
        conn, addr = server.accept()
        client = Client(conn, addr)
        clients.append(client)
        thread = threading.Thread(target=client_thread, args=(client,))
        thread.daemon = True
        thread.start()

try:
    if __name__ == "__main__":
        system('clear -x')
        start()
except KeyboardInterrupt:
    print("\nServer closed.")

