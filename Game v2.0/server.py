from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import pickle


def accept_incoming_connections():  # новое подключение
    while True:
        client, client_address = SERVER.accept()
        print(f"Новый игрок {client_address}")
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    player_id, player_name = client.recv(BUFSIZE).decode("utf8").split()
    clients[client] = (player_id, player_name)
    positions[player_id] = (300, 300)
    broadcast(pickle.dumps(positions))

    while True:
        try:
            msg = client.recv(BUFSIZE)
            if msg != bytes("{quit}", "utf8"):
                s = pickle.loads(msg)
                old = positions[player_id]
                positions[player_id] = ((old[0] + s[0]) % 600, (old[1] + s[1]) % 600)
                print(positions)
                broadcast(pickle.dumps(positions))
            else:
                print(f"{player_name} вышел из игры")
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del clients[client]
                del positions[player_id]
                broadcast(bytes(f"del {player_id}", "utf8"))
                break
        except ConnectionResetError:
            break


def broadcast(msg):  # разослать сообщение всем клиентам
    for sock in clients:
        sock.send(msg)


clients = {}
positions = {}

HOST = ''
PORT = 33000
BUFSIZE = 1024

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind((HOST, PORT))

if __name__ == "__main__":
    SERVER.listen(5)
    print("Ждем подключения...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
