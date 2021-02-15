import socket
import threading

## Socketin konfiguraatio:
PORT = 23456
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

## Globaaleja muuttujia:
DISCONNECT_MESSAGE = "DISCONNECT"   ## Tällä viestillä katkaistaan yhteys
FORMAT = 'iso8859_10'               ## utf_8 aiheutti virheitä öökkösten kanssa
HEADER = 8                          ## Headerin pituus

print("Server details: " + str(ADDR))  

## Socketin asetukset:
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
## SO_REUSEADDR estää "Address already in use" -virheet
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"NEW CONNECTION: {addr} connected.")

    connected = True    
    while connected:    ## Tässä olisi voinut olla myös 'with conn:'
        ## Tässä silmukassa haetaan koko ajan saapunutta dataa
        ## socketilta.
        try:
            ## Haetaan ensin HEADERin mittainen pätkä lähetyksestä,
            ## siitä luetaan viestin pituus
            msg_length = conn.recv(HEADER).decode(FORMAT).strip()
            msg_length = int(msg_length)

            ## Sitten haetaan äsken saadun viestin pituuden verran merkkejä
            msg = conn.recv(msg_length).decode(FORMAT).strip()
        except Exception:
            ## Jotkut kirjaimet aiheuttavat virheen, tässä käsitellään ne.
            print("Some characters are not supported.")
        finally:
            ## Lähetetään sama viesti takaisin samaa yhteyttä pitkin
            conn.sendall(msg.encode(FORMAT))

            if msg == DISCONNECT_MESSAGE:
                ## Jos viesti on 'DISCONNECT', katkaistaan silmukka jolloin
                ## thread lopettaa automaattisesti
                print("Received disconnect from client " + str(addr))
                connected = False
                break

            if msg_length>0:
                ## Tulostetaan saatu viesti serverin konsolille
                print(f"[{addr}] {msg}")
        


def start():
    server.listen()     ## Käynnistetään socket kuuntelemaan yhteyksiä
    print(f"LISTENING: Server listening on {SERVER}:{PORT}")
    while True:
        ## Tässä silmukassa hyväksytään aina uudet yhteydet ja aloitetaan uusi
        ## threadi jokaiselle yhteydelle. Threadille viedään argumentteina
        ## yhteyden tiedot
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"ACTIVE CONNECTIONS: {threading.activeCount() - 1}")

print("Server is starting...")

## Käynnistetään serveri, try-exceptillä käsitellään KeyboardInterrupt (ctrl+C)
## Näin ei tule virheilmoitusta
try:
    start()
except KeyboardInterrupt:
    print("\nServer interrupted by user.")