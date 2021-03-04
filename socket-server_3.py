import threading
import socket
from os import system
## os.system-moduulilla tyhjennetään konsoli kun ohjelma
## käynnistetään

## Socketin konfiguraatio:
PORT = 23456
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

## Globaaleja muuttujia:
DISCONNECT_MESSAGE = ">X<"   ## Tällä viestillä katkaistaan yhteys
FORMAT = 'iso8859_10'               ## utf_8 aiheutti virheitä öökkösten kanssa

## Header on selitetty client-tiedostossa tarkemmin
H_LEN = 8
H_USER = 16

## lista yhdistetyistä clienteista viestien edelleenlähetystä varten
clients = []


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

## Olio yhteyden tietoja varten
class Client:
    def __init__(self, conn, addr):
        self.connection = conn
        self.address, self.port = addr

## Olio viestin tietoja varten
class Message:
    def __init__(self, user, length, message):
        self.user = user
        self.length = length
        self.message = message


## Luetaan viesti ja tehdään siitä objekti
def read_message(conn):
    try:
        user = conn.recv(H_USER).decode(FORMAT).strip()
        msg_len = int(conn.recv(H_LEN).decode(FORMAT).strip())
        msg = conn.recv(msg_len).decode(FORMAT)
        message = Message(user, msg_len, msg)
        return message

    ## ValueError tulee, jos luetaan tyhjää viestiä, ConnectionReset jos
    ## client on katkaissut yhteyden
    except ValueError or ConnectionResetError:
        return Message(user, len(DISCONNECT_MESSAGE), DISCONNECT_MESSAGE)


## Saapuvien viestien edelleenlähetys
## parametrina viesti-objekti ja yhteys, josta viesti tuli
## jotta ei lähetetä samaa viestiä takaisin
def forward_message(msg, client):
    for c in clients:
        if c != client:
            header_user = f"{msg.user:<{H_USER}}".encode(FORMAT)
            header_len = f"{msg.length:<{H_LEN}}".encode(FORMAT)
            message = header_user + header_len + msg.message.encode(FORMAT)
            c.connection.sendall(message)


## Pääthread 
def client_thread(client):
    conn = client.connection
    addr = client.address

    ## Tulostetaan tietoja
    print(f"[+] {addr} connected")
    print(f"[i] {len(clients)} client(s) active")

    while True:
        ## Luetaan viesti
        message = read_message(conn)

        ## Lähetetään viesti edelleen, parametrina vastaanottanut yhteys
        forward_message(message, client)

        ## Yhteyden katkaisu
        if message.message == DISCONNECT_MESSAGE:
            print(f"[-] {addr} disconnected")
            clients.remove(client)
            print(f"[i] {len(clients)} client(s) active")
            return

        print(f"{message.user} @ [{addr}] : {message.message} ")


    


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
        system('clear -x')  ## Näyttö tyhjäksi
        start()
except KeyboardInterrupt:
    print("\nServer closed.")

