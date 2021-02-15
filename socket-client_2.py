import socket

## Yhteyden tiedot, vastaa serverlin PORT ja SERVER muuttujia
HOST = '192.168.1.101'
PORT = 23456
SERVER_ADDRESS = (HOST, PORT)

## Globaaleja muuttujia:
FORMAT = 'iso8859_10'
HEADER = 8
DISCONNECT_MESSAGE = "DISCONNECT"

def echo_client():
    ## Yhdistetään serveriin uudella socketilla
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.connect(SERVER_ADDRESS)
    ## message ja return_message tyhjiksi stringeiksi
    message = ''    
    return_msg = ''

    while return_msg != DISCONNECT_MESSAGE:
        ## Tätä loopataan niin kauan kuin saadaan paluuviestinä 'DISCONNECT'
        try:
            ## Luetaan haluttu viesti STDINistä:
            message = input(">> ")
            ## luodaan viestille header, 8 byteä pitkä ja siinä on vain viestin
            ## pituus:
            header = f"{len(message):<{HEADER}}".encode(FORMAT)
            ## Luodaan ja enkoodataan viesti oikeaan muotoon:
            message = message.encode(FORMAT)
            ## Lähetetään viesti headereineen:
            sock.send(header + message)
            amount_expected = len(message)  ## paluuviestin pitäisi olla yhtä pitkä
            ## Luetaan paluuviesti:
            return_msg = sock.recv(amount_expected).decode(FORMAT).strip()
        except Exception as e:
            print("ERROR: " + str(e))
        finally:
            if return_msg == DISCONNECT_MESSAGE:
                ## Jos saadaan 'DISCONNECT' serveriltä paluuviestinä,
                ## suljetaan yhteys
                print("Closing connection.")
                sock.close()
            else:
                ## Tulostetaan paluuviesti konsolille
                print("Server echoed back: " + return_msg)

echo_client()
