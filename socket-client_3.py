import socket
import threading
from os import system

## Yhteyden tiedot, vastaa serverlin PORT ja SERVER muuttujia
HOST = '192.168.1.101'
PORT = 23456
SERVER = (HOST, PORT)

## Globaaleja muuttujia:
DISCONNECT_MESSAGE = ">X<"   ## Tällä viestillä katkaistaan yhteys
FORMAT = 'iso8859_10'               ## utf_8 aiheutti virheitä öökkösten kanssa
H_LEN = 8
H_USER = 16


def listen_messages(sock):
    while True:
        user = sock.recv(H_USER).decode(FORMAT).strip()
        if user:
            msg_len = int(sock.recv(H_LEN).decode(FORMAT).strip())
            msg = sock.recv(msg_len).decode(FORMAT)
            print(f"{user}: {msg}")



def connect():

    def send(msg):
        try:
            sock.sendall(msg)
        except ConnectionResetError:
            print("Server closed the connection, exiting.")
            exit()


    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(SERVER)
        listen_thread = threading.Thread(target=listen_messages, args=(sock,))
        listen_thread.daemon = True
        listen_thread.start()
        print(f"Connected to {HOST}:{PORT}")
    except ConnectionRefusedError:
        print(f"Could not connect to {HOST}:{PORT}")
        return
    username = input("Enter username: ")

    while True:

        try:
            message = input()
            header_user = f"{username:<{H_USER}}".encode(FORMAT)
            header_len = f"{len(message):<{H_LEN}}".encode(FORMAT)
        except EOFError or KeyboardInterrupt:
            message = DISCONNECT_MESSAGE
            header_user = f"{username:<{H_USER}}".encode(FORMAT)
            header_len = f"{len(message):<{H_LEN}}".encode(FORMAT)
            print("Disconnected.")
            exit()

        message = header_user + header_len + message.encode(FORMAT)
        send(message)
        




if __name__ == "__main__":
    system('clear -x')
    client_thread = threading.Thread(target=connect, args=())
    client_thread.start()


