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

## Topicit ja ne tilanneet clientit tallennetaan 2-ulotteiseen listaan,
## topics = [['all', Client1, Client2, Client3, Client4, Client5],
##            'topic1', Client3, Client4], ['topic2', Client3, Client4],
##            'topic2', Client2, Client5, Client4], ['topic3', Client1, Client2]]
## esim:
## all      Client1 Client2 Client3 Client4 Client5
## topic1   Client3 Client4  
## topic2   Client2 Client5 Client4
## topic3   Client1 Client2
##
## Aiempi clients-lista on nyt topics[0] eli 'all'-lista
## aktiivisten clientien määrä on siis len(topics[0]) - 1, koska topics-listan
## jokaisella rivillä on otsikkona topicin nimi

## Tyhjä topics-lista sisältää vain yhden rivin ja sen otsikon 'all',
## tämä sisältää kaikki yhdistetyt clientit:
topics = [['all']]


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


## find_topic etsii halutun topicin indeksin topics-taulukosta ja jos topicia
## ei ole, palauttaa False
def find_topic(topic):
    t = f"'{topic}'"
    for i in range(len(topics)):
        if topics[i][0] == t:
            return i
    return False


## Tulostaa topics-taulukon
def print_topics():
    for row in topics:
        for col in row:
            if type(col) == str:
                print(col, end="\t")
            else:
                print(id(col), end="\t")
        print()
    return


## Clientin yhteyden katkaisu, käy kaikki topicit läpi
def remove_client(client):
        for topic in topics:
            try:
                topic.remove(client)
            except ValueError:
                pass
            if len(topic) == 1 and topic[0] != 'all':
                topics.remove(topic)




## Jos saapunut viesti alkaa '#'-merkillä, se liittyy topiceihin ja käsitellään
## tässä funktiossa
def topic_handler(msg, client):
    ## '#'-merkki toimii erottimena, ensimmäinen pätkä on käsky (action),
    ## toinen pätkä on topic (req_topic),
    ## kolmas pätkä viesti (topic_message myöhempänä)
    action = msg.message.split('#')[1]
    try:
        req_topic = msg.message.split('#')[2]

        ## Tarkistetaan onko topic olemassa, jos on haetaan sen indeksi
        index = find_topic(req_topic)
    except IndexError:
        print_topics()

    ## SUBSCRIBE:
    if action == 'SUBSCRIBE':
        print(f'{action} {req_topic}')

        ## Jos topicia ei ole vielä olemassa, luodaan uusi ja tilataan se
        if not index:
            ## - Luodaan uusi "rivi" topics-taulukkoon
            ## - Rivin ensimmäinen sarake on topicin nimi
            ## - Lisätään pyynnön lähettänyt client topicin tilanneisiin
            ## - Rivi topics-taulukkoon
            ## - Vahvistusviesti
            ## - tulostetaan taulukko serverin konsolille
            new_topic = []
            new_topic.append(f"'{req_topic}'")
            new_topic.append(client)
            topics.append(new_topic)            
            return_message(f'Created new topic "{req_topic}"', client)
            print_topics()


        ## Jos topic on olemassa, tilataan se
        else:
            ## - Lisätään pyynnön lähettänyt client riville
            ## - Vahvistusviesti
            ## - Taulukko serverin konsolille
            topics[index].append(client)
            return_message(f'Subscribed to topic "{req_topic}"', client)
            print_topics()


    ## PUBLISH, viestin julkaisu topiciin
    elif action == 'PUBLISH':
        print(f'{action} {req_topic}')

        ## Jos topicia ei ole olemassa
        if not index:
            return_message(f'No topic named {req_topic}', client)


        ## Topic olemassa, julkaistaan viesti
        else:

            ## Erotetaan viesti pyynnöstä
            topic_message = msg.message.split('#')[3]
            topic = topics[index]

            ## Välitetään viesti kaikille tilanneille,
            ## ei kuitenkaan viestin lähettäjälle
            for c in topic:
            ## topicin ensimmäinen jäsen on listan nimi, hypätään se yli
                if c != client and c != topic[0]:
                    user = f'#{req_topic} {msg.user}'
                    header_user = f"{user:<{H_USER}}".encode(FORMAT)
                    header_len = f"{len(topic_message):<{H_LEN}}".encode(FORMAT)
                    message = header_user + header_len + topic_message.encode(FORMAT)
                    c.connection.sendall(message)


    ## Kirotusvireet ja muut
    else:
        return_message('Invalid topic action', client)


## Viestin lähetys vain yhdelle clientille
def return_message(msg, client):
    header_user = f"{'root':<{H_USER}}".encode(FORMAT)
    header_len = f"{len(msg):<{H_LEN}}".encode(FORMAT)
    message = header_user + header_len + msg.encode(FORMAT)
    client.connection.sendall(message)



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
    except (ValueError, ConnectionResetError):
        return Message(user, len(DISCONNECT_MESSAGE), DISCONNECT_MESSAGE)


## Saapuvien viestien edelleenlähetys
## parametrina viesti-objekti ja yhteys, josta viesti tuli
## jotta ei lähetetä samaa viestiä takaisin
def forward_message(msg, client):
    for c in topics[0]:
        ## topics[0] ensimmäinen jäsen on listan nimi, hypätään se yli
        if c != client and c != topics[0][0]:
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
    print(f"[i] {len(topics[0])-1} client(s) active")

    join_message = f"[+] {addr} connected"
    forward_message(Message('root', len(join_message), join_message), client)

    print_topics()

    while True:
        ## Luetaan viesti
        try:
            message = read_message(conn)
        except Exception:
            ## Jos ei yhteyttä clientiin
            print(f"Connection lost to {addr}")
            remove_client(client)
            break


        ## Yhteyden katkaisu
        if message.message == DISCONNECT_MESSAGE:
            disconnect_message = f"[-] {addr} disconnected"
            forward_message(Message('root', len(disconnect_message), disconnect_message), client)
            print(f"[-] {addr} disconnected")
            remove_client(client)
            print(f"[i] {len(topics[0])-1} client(s) active")
            return
        else:
            ## Jos viestin ensimmäinen merkki on '#' ja viesti ei ole tyhjä:
            if message.message[0] == '#' and message.message:
                topic_handler(message, client)
            else:
                ## Jos ensimmäinen merkki ei ole '#',
                ## lähetetään viesti edelleen kaikille, 
                ## parametrina vastaanottanut yhteys
                forward_message(message, client)

        print(f"{message.user} @ [{addr}] : {message.message} ")


    


def start():
    server.listen()
    print(f"Listening at {SERVER}:{PORT}")
    print_topics()

    while True:
        conn, addr = server.accept()
        client = Client(conn, addr)
        topics[0].append(client)
        thread = threading.Thread(target=client_thread, args=(client,))
        thread.daemon = True
        thread.start()

try:
    if __name__ == "__main__":
        system('clear -x')  ## Näyttö tyhjäksi
        start()
except KeyboardInterrupt:
    print("\nServer closed.")

