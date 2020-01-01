from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import pygame
import pickle
import sys
import random


def receive():
    while True:
        try:
            msg = client_socket.recv(BUFSIZE)
            try:
                server_players = pickle.loads(msg)
                for pid in server_players:
                    if pid not in players:
                        Player(all_sprites, pid)
                    players[pid] = server_players[pid]
            except pickle.UnpicklingError:
                try:
                    t = msg.decode("utf8")
                    if t.startswith("{quit}"):
                        client_socket.close()
                        break
                    if t.startswith("del"):
                        del_id = t.split()[1]
                        del players[del_id]
                except UnicodeDecodeError:
                    continue
        except OSError:  # Possibly client has left the chat.
            break


class Player(pygame.sprite.Sprite):
    enemy_image = pygame.image.load("data/bomb.png")
    my_image = pygame.image.load("data/bomb2.png")

    def __init__(self, group, id):
        super().__init__(group)
        if id != player_id:
            self.image = Player.enemy_image
        else:
            self.image = Player.my_image
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.id = id

    def update(self, *args):
        if self.id not in players:
            self.kill()
        else:
            self.rect.center = players[self.id]


pygame.init()
screen = pygame.display.set_mode((600, 600))

running = True
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()

v = 10
shift = {pygame.K_LEFT: (-v, 0), pygame.K_RIGHT: (v, 0),
         pygame.K_UP: (0, -v), pygame.K_DOWN: (0, v)}
bot = False

HOST = "127.0.0.1"  # input('Enter host: ')
PORT = 33000  # input('Enter port: ')
if len(sys.argv) > 1:
    HOST = sys.argv[1]
if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
if len(sys.argv) > 3:
    bot = sys.argv[3] == "bot"
BUFSIZE = 1024
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((HOST, PORT))
receive_thread = Thread(target=receive)
receive_thread.start()

player_id = str(random.randint(1, 1000000))
player_name = "player" + player_id  # input('Введите ник игрока')
client_socket.send(bytes(f"{player_id} {player_name}", "utf8"))
players = {}

bot_event = 30
if bot:
    pygame.time.set_timer(bot_event, 100)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            client_socket.send(bytes("{quit}", "utf8"))
            running = False
        if event.type == bot_event:
            client_socket.send(pickle.dumps(random.choice(list(shift.values()))))
    for s in shift:
        if pygame.key.get_pressed()[s]:
            client_socket.send(pickle.dumps(shift[s]))
    screen.fill(pygame.Color("white"))
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(100)
