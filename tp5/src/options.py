import pygame
import random

WIDTH = 1200
HEIGHT = 800
TILE = 50

SPEED = 2
TURN_SPEED = 0.04
MAX_FPS = 120
COLORS = {
    'white':  (200, 200, 200),
    'black':  (50, 50, 50),
    'orange': (150, 80, 40),
    'green':  (0, 200, 0),
    'blue':   (0, 0, 200),
    'gray':   (150, 150, 150),
    'purple': (120, 0, 120),
    'red':    (200, 0, 0),
    'yellow': (255, 255, 0)
}

FONT = lambda size: pygame.font.SysFont('verdana', size, True)
PLAYER_COLOR = [COLORS["green"], COLORS["red"], COLORS["blue"], COLORS["orange"], COLORS["yellow"]]


spawn_list = [(550, 550), (100, 100), (425, 80), (200, 680), (650, 680), (1100, 700), (1100, 275)]
def get_random_spawn():
    return random.choice(spawn_list)


def handle_client_args(args):
    """
    Code is not looking good, I saw last minute that we need to handle command line arguments :)
    """
    if "--help" in args or "-h" in args:
        print("This is the client of the game, in order to run it, you need to respect this format:")
        print(f"     {args[0]} [-i|--ip] <ip_addr> [-p|--port] <port_number>")
        print(f"\nExample : {args[0]} -i 127.0.0.1 -p 8008")
        return None, None

    show_usage = False
    if len(args) != 5:
        print(f"Usage : {args[0]} [-i|--ip] <ip_addr> [-p|--port] <port_number>")
        print(f"Example : {args[0]} -i 127.0.0.1 -p 8008")
        return None, None

    if args[1] not in ('-i', '--ip'):
        show_usage = True

    if args[3] not in ('-p', '--port'):
        show_usage = True

    IP = args[2]
    PORT = 0
    try:
        PORT = int(args[4])
    except ValueError:
        show_usage = True

    if show_usage:
        print(f"Usage : {args[0]} [-i|--ip] <ip_addr> [-p|--port] <port_number>")
        print(f"Example : {args[0]} -i 127.0.0.1 -p 8008")
        return None, None

    return IP, PORT

def handle_server_args(args):
    if "--help" in args or "-h" in args:
        print("This is the server of the game, in order to run it, you need to respect this format:")
        print(f"     {args[0]} [-p|--port] <port_number>")
        print(f"\nExample : {args[0]} -p 8008")
        return None

    show_usage = False
    if len(args) != 3:
        print(f"Usage : {args[0]} [-p|--port] <port_number>")
        print(f"Example : {args[0]} -p 8008")
        return None

    if args[1] not in ('-p', '--port'):
        show_usage = True

    PORT = 0
    try:
        PORT = int(args[2])
    except ValueError:
        show_usage = True

    if show_usage:
        print(f"Usage : {args[0]} [-i|--ip] <ip_addr> [-p|--port] <port_number>")
        print(f"Example : {args[0]} -i 127.0.0.1 -p 8008")
        return None

    return PORT
