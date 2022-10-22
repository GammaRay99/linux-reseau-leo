#!/bin/env python3

from struct import unpack
import threading
import socket
import sys

from classes import Player, World
import protocol
import options

HOST = "0.0.0.0"
PORT = options.handle_server_args(sys.argv)
if PORT is None:
	quit()

def handle_player(world, id_player):
	"""
	Network main loop
	Here we are processing everything that the server receives for a certain player, such as:
		- player location & angle update
		- player leaving the game 
		- "freeze" gestion
	(and handling network error too)
	"""
	player_target = world.get_player_from_id(id_player)
	weird_streak = 0   # if we receive 5 packets in a row, we assume that
					   # that there is a problem and we close the connexion
	while world.alive:
		print(f"{id_player} : {player_target.x}, {player_target.y}, {player_target.angle}")
		try:
			packet = player_target.recv(protocol.PACKET_SIZE)
		except ConnectionResetError as e:
			if not world.alive:
				# Security feature, some sort of race condition kept happening and the threads
				# were desync. Using world.alive coupled with a check for network err fixes it.
				continue
			else:
				print("Lost connexion with client")
				world.remove_player_from_id(id_player)
				print(f"Player {id_player} left")
				return

		data = protocol.read_packet(packet, err_log=False)
		if data is None:
			# Handling invalid packet
			print(f"Client {id_player} sent weird packet: {packet}")
			weird_streak += 1
			if weird_streak > 5:
				print(f"Client {id_player} is too weird for me, kicking him.")
				for player in world.players:
					player.send(protocol.SERVER_GOODBYE(id_player), no_out=True)

				world.remove_player_from_id(id_player)
				print(f"Player {id_player} left")
				return
			continue

		weird_streak = 0
		client_id = data["id"]
		packet_type = data["type"]

		if packet_type == protocol.types["CLIENT_GOODBYE"]:
			for player in world.players:
				player.send(protocol.SERVER_GOODBYE(id_player))
			world.remove_player_from_id(id_player)
			print(f"Player {id_player} left")
			return

		if packet_type == protocol.types["CLIENT_UPDATE"]:
			player_target.handle_update(client_id, data["x"], data["y"], data["angle"])
			for player in world.players:
				if player.id != id_player:
					player.send(protocol.SERVER_UPDATE(id_player, data["x"], data["y"], data["angle"]))
			continue

		if packet_type == protocol.types["CLIENT_FREEZE"]:
			player.player_freeze()  # Useless but for consistency
			for player in world.players:
				player.send(protocol.SERVER_FREEZE(id_player, data["x"], data["y"], data["angle"]))


world = World()

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(world.limit)

while world.alive:
	# This loop creates new players from new connection if the server is not already full
	try:
		client, addr = sock.accept()
	except KeyboardInterrupt:
		print("Telling everyong to GTFO...")
		for player in world.players:
			player.send(protocol.SERVER_GOODBYE(player.id))
			player.conn.close()
		print("Exiting")
		world.alive = False
		sock.close()
		continue

	packet = client.recv(protocol.PACKET_SIZE)
	data = protocol.read_packet(packet)
	if data is None:
		# Exception should be handled in protocol.read_packet()
		client.close()
		continue

	client_id = data["id"]
	packet_type = data["type"]
	
	if world.is_full():
		print("Rejecting connection, server is full")
		client.send(protocol.SERVER_FULL())
		continue

	if packet_type == protocol.types["CLIENT_HELLO"]:
		spawn_x, spawn_y = options.get_random_spawn()
		success = client.send(protocol.SERVER_HELLO(world.next_id, spawn_x, spawn_y))
		if not success:
			print(f"An error occured while responding SERVER_HELLO to client {addr}: {e}")
			client.close()
			continue

		print(f"Player {world.next_id} connected")
		new_player = Player(spawn_x, spawn_y, world, world.next_id, client)
		world.players.append(new_player)

		for player in world.players:
			client.send(protocol.SERVER_UPDATE(player.id, player.x, player.y, player.angle))
			player.send(protocol.SERVER_UPDATE(new_player.id, new_player.x, new_player.y, new_player.angle))
			if player.freeze:
				client.send(protocol.SERVER_FREEZE(player.id, player.x, player.y, player.angle))

		threading.Thread(target=handle_player, args=(world, world.next_id)).start()
		world.next_id += 1
	else:
		# For a new connection, only the packet type "CLIENT_HELLO" is accepted, everything else is considered
		# as incorrect
		print(f"Uknown client sent packet type: {hex(packet_type)}")

sock.close()

