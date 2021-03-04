## Jarno Rankinen TVT19KMO
## Sockets programming exercise 3
## ASSD Spring 2021

import socket
import threading
from os import system   
## os.system-moduulilla tyhjennetään konsoli kun ohjelma
## käynnistetään

## Yhteyden tiedot, vastaa serverin PORT ja SERVER muuttujia
HOST = '192.168.1.101'
PORT = 23456
SERVER = (HOST, PORT)

## Globaaleja muuttujia:
DISCONNECT_MESSAGE = ">X<"   ## Tällä viestillä katkaistaan yhteys
FORMAT = 'iso8859_10'        ## utf_8 aiheutti virheitä öökkösten kanssa

## Header on 16 byteä + 8 byteä, siinä kulkee käyttäjänimi ja viestin pituus
## koko viesti esim:
## b'jarno           5       terve'
H_LEN = 8
H_USER = 16

## listen_messages() pyörii omassa threadissa ja kuuntelee saapuvia viestejä
def listen_messages(sock):
    while True:
        try:
            user = sock.recv(H_USER).decode(FORMAT).strip()
            if user:
                msg_len = int(sock.recv(H_LEN).decode(FORMAT).strip())
                msg = sock.recv(msg_len).decode(FORMAT)
                print(f"{user}: {msg}")
        except ValueError:
            pass


## connect() yhdistää palvelimeen ja hoitaa viestien lähettämisen
def connect():

    ## Viestin lähetys
    def send(msg):
        try:
            sock.sendall(msg)
        ## Jos palvelin on suljettu (=kaatunut...), lopetetaan
        except ConnectionResetError:
            print("Server closed the connection, exiting.")
            exit()


    try:
        ## Luodaan socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(SERVER)

        ## Käynnistetään saapuvien viestien thread
        listen_thread = threading.Thread(target=listen_messages, args=(sock,))
        listen_thread.daemon = True     ## daemon, jotta voidaan lopettaa ohjelma
        listen_thread.start()
        print(f"Connected to {HOST}:{PORT}")

    ## Jos palvelin ei ole käynnissä
    except ConnectionRefusedError:
        print(f"Could not connect to {HOST}:{PORT}")
        return
    username = input("Enter username: ")

    while True:

        try:
            ## Luetaan viesti ja muodostetaan header
            message = input()
            header_user = f"{username:<{H_USER}}".encode(FORMAT)
            header_len = f"{len(message):<{H_LEN}}".encode(FORMAT)

        ## Lopettaminen tapahtuu Ctrl+D (EOFError) tai Ctrl+C (KeyboardInterrupt)
        ## painamalla
        except EOFError or KeyboardInterrupt:
            message = DISCONNECT_MESSAGE
            header_user = f"{username:<{H_USER}}".encode(FORMAT)
            header_len = f"{len(message):<{H_LEN}}".encode(FORMAT)
            print("Disconnected.")
            exit()

        ## kasataan ja lähetetään viesti
        message = header_user + header_len + message.encode(FORMAT)
        send(message)
        




if __name__ == "__main__":
    system('clear -x')
    client_thread = threading.Thread(target=connect, args=())
    client_thread.start()


