#!/bin/env python3

import threading
import socket
import pygame
import sys

from classes import Player, World
from struct import unpack
import protocol
import options



HOST, PORT = options.handle_client_args(sys.argv)
if HOST is None:
	quit()


def handle_server(server_conn, player):
	"""
	Network main loop
	Here we are processing everything that the server sends, such as:
		- other players location & angle
		- other player / us leaving the game 
		- "freeze" gestion
	(and handling network error too)
	"""
	weird_streak = 0   # if we receive 5 packets in a row, we assume that
					   # that there is a problem and we close the connexion
	while player.world.alive:
		packet = server_conn.recv(protocol.PACKET_SIZE)
		data = protocol.read_packet(packet, err_log=True)
		if data is None:
			print(f"Server sent weird packet. {packet}")
			weird_streak += 1
			if weird_streak >= 5:
				print("Server is too weird for me. Exiting !")
				server_conn.send(protocol.type["CLIENT_GOODBYE"])
				player.world.alive = False
				server_conn.close()
			continue

		weird_streak = 0
		client_id = data["id"]
		packet_type = data["type"]

		if packet_type == protocol.types["SERVER_GOODBYE"]:
			if client_id == player.id:
				print("Server told us to left")
				player.world.alive = False
				server_conn.close()
				return
			else:
				world.remove_player_from_id(client_id)
				print(f"Player {client_id} left")

		if packet_type == protocol.types["SERVER_UPDATE"]:
			player.handle_update(client_id, data["x"], data["y"], data["angle"])

		if packet_type == protocol.types["SERVER_FREEZE"]:
			player.handle_update(client_id, data["x"], data["y"], data["angle"])
			target = player.world.get_player_from_id(client_id)
			target.player_freeze()


def render_fps(surface, clock):
	"""
	Draw fps count on screen
	Using the clock object to extract fps data
	"""
	current_fps = int(clock.get_fps())  # removing float precision
	color = options.COLORS["red"] if current_fps < 15 else options.COLORS["green"]
	fps_text = options.FONT(15).render(str(current_fps), 0, color)
	surface.blit(fps_text, (10, 10))


# Starting init network operation
server = socket.socket()
server.connect((HOST, PORT))

server.send(protocol.CLIENT_HELLO())
packet = server.recv(protocol.PACKET_SIZE)
data = protocol.read_packet(packet)
if data is None:
	# Exception should be handled in protocol.read_packet()
	server.close()
	print("Exiting the program, please contact the server for more information.")
	quit()

new_id = data["id"]
packet_type = data["type"]


if packet_type == protocol.types["SERVER_FULL"]:
	print("Server is full !")
	server.close()
	quit()

if packet_type == protocol.types["SERVER_HELLO"]:
	print("Accepted in the server with ID: ", new_id)
else:
	# If the server doesnt respond with a SEVER_HELLO, we abort the connection.
	print("Server response incorrect, aborting !!")
	server.close()
	quit()
# End of init network operation, we now have an ID

world = World()
world.init_walls()

curr_player = Player(data["x"], data["y"], world, new_id, server)
print("My id: ", new_id)

world.players.append(curr_player)

pygame.init()
window = pygame.display.set_mode((1200, 800))
clock = pygame.time.Clock()

threading.Thread(target=handle_server, args=(server, curr_player)).start()

while world.alive:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			server.send(protocol.CLIENT_GOODBYE(curr_player.id))
			world.alive = False
			continue
	
	window.fill((150, 150, 150))

	curr_player.handle_movement()

	for wall in world.walls:
		wall.draw(window)

	for player in world.players:
		player.draw(window)

	render_fps(window, clock)
	pygame.display.flip()
	clock.tick(options.MAX_FPS)

	# in order to avoid spamming the network, we are sending a packet only if our coordinates have changed
	# (this includes angle)
	if (curr_player.x, curr_player.y, curr_player.angle) != curr_player.last_pos:
		curr_player.last_pos = (curr_player.x, curr_player.y, curr_player.angle)
		server.send(protocol.CLIENT_UPDATE(curr_player.id, curr_player.x, curr_player.y, curr_player.angle))