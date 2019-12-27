from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import pygame
import random


def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            # msg_list.insert(tkinter.END, msg)
            print(msg)
            # if msg.startswith("Greetings") \
            #         or msg.startswith("Welcome") \
            #         or "has joined" in msg:
            #     continue
            try:
                id, x, y = [int(i) for i in msg.split(": ")]
                if id == player_id:
                    continue
                else:
                    if id not in enemies:
                        Enemy(all_sprites, id)
                    enemies[id] = (x, y)
                    # print(enemies)
            except ValueError:
                continue
        except OSError:  # Possibly client has left the chat.
            break


def send(msg, event=None):  # event is passed by binders.
    """Handles sending of messages."""
    # msg = my_msg.get()
    # my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        # top.quit()


class Enemy(pygame.sprite.Sprite):
    image = pygame.image.load("data/creature.png")

    def __init__(self, group, id):
        super().__init__(group)
        self.image = Enemy.image
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.id = id

    def update(self, *args):
        # print('up')
        self.rect.topleft = enemies[self.id]


pygame.init()
screen = pygame.display.set_mode((600, 600))

running = True
clock = pygame.time.Clock()
image = pygame.image.load('data/creature.png')
imgRect = image.get_rect()
all_sprites = pygame.sprite.Group()

v = 10
shift = {pygame.K_LEFT: (-v, 0), pygame.K_RIGHT: (v, 0),
         pygame.K_UP: (0, -v), pygame.K_DOWN: (0, v)}

# ----Now comes the sockets part----
HOST = "127.0.0.1"  # input('Enter host: ')
PORT = 33000  # input('Enter port: ')
# if not PORT:
#     PORT = 33000
# else:
#     PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()

player_id = random.randint(1, 1000000)
send(f"{player_id}")
enemies = {}

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    for s in shift:
        if pygame.key.get_pressed()[s]:
            imgRect.move_ip(shift[s])
            send(f"{imgRect.x}: {imgRect.y}")
    screen.fill(pygame.Color("white"))
    screen.blit(image, imgRect)
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(100)
