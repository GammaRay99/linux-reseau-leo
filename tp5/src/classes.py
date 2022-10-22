from struct import unpack
import pygame
import math

from map_array import map_array
import protocol
import options


class Player:
	def __init__(self, x, y, world, player_id, connexion=None):
		self.conn = connexion
		self.x = x
		self.y = y
		self.angle = 0
		self.world = world
		self.id = player_id
		self.color = options.PLAYER_COLOR[player_id]
		self.freeze = False
		self.last_pos = None
		self.speed = options.SPEED
		self.turn_speed = options.TURN_SPEED
		self.rayon = 12

	def send(self, data, no_out=False):
		"""
		use the connexion object of the player to send packets
		Only the server uses this method
		"""
		try:
			self.conn.send(data)
			return True
		except Exception as e:
			if not no_out:
				print(f"A network occured: {e}")
			return False
	
	def recv(self, size=protocol.PACKET_SIZE):
		"""
		use the connexion object of the player to receive incoming packets
		Only the server uses this method
		"""
		if self.conn is not None:
			return self.conn.recv(size)
		else:
			raise Exception("Player connection is None")

	def move(self, x, y, angle):
		"""
		just move
		"""
		self.x = x
		self.y = y
		self.angle = angle

	def player_freeze(self):
		"""
		idk what's the point of that but yeah you can't move and your purple
		"""
		self.freeze = True
		self.color = options.COLORS["purple"]


	def handle_movement(self):
		"""
		This is client sided, we are using the keys of the keyboard to move
		"""
		if self.freeze:
			return
	
		keys = pygame.key.get_pressed()

		if keys[pygame.K_d]:
			next_angle = round(self.angle + self.turn_speed, 2)
			if self.angle <= round(math.pi*2, 2) <= next_angle:
				next_angle = next_angle - round(math.pi*2, 2)
			self.angle = next_angle

		if keys[pygame.K_q]:
			next_angle = round(self.angle - self.turn_speed, 2)
			if self.angle >= -round(math.pi*2, 2) >= next_angle:
				next_angle = next_angle + round(math.pi*2, 2)
			self.angle = next_angle

		if keys[pygame.K_z]:
			next_x = self.x + round(self.speed * math.cos(self.angle))  # thanks for the maths internet
			next_y = self.y + round(self.speed * math.sin(self.angle))  # note: don't invert sin and cos
			if map_array[int(next_y / options.TILE)][int(next_x / options.TILE)]:
				# if we're going into a wall,
				# we dont go into the wall.
				if not map_array[int(self.y / options.TILE)][int(next_x / options.TILE)]:
					self.x = next_x
				elif not map_array[int(next_y / options.TILE)][int(self.y / options.TILE)]:
					self.y = next_y
				else:
					pass
			else:
				self.x = next_x
				self.y = next_y

		if keys[pygame.K_s]:
			next_x = self.x - round(self.speed * math.cos(self.angle))
			next_y = self.y - round(self.speed * math.sin(self.angle))
			if map_array[int(next_y / options.TILE)][int(next_x / options.TILE)]:
				# if we're going into a wall,
				# we dont go into the wall.
				if not map_array[int(self.y / options.TILE)][int(next_x / options.TILE)]:
					self.x = next_x
				elif not map_array[int(next_y / options.TILE)][int(self.y / options.TILE)]:
					self.y = next_y
				else:
					pass
			else:
				self.x = next_x
				self.y = next_y

		if keys[pygame.K_SPACE]:
			self.send(protocol.CLIENT_FREEZE(self.id, self.x, self.y, self.angle))


	def draw(self, win):
		"""
		Draw the player on screen
		Only the client uses that
		"""
		pygame.draw.circle(win, self.color, [self.x, self.y], self.rayon)
		pygame.draw.line(win, self.color, [self.x, self.y], (self.x + 20 * math.cos(self.angle), self.y + 20 * math.sin(self.angle)), 8)
		# ^ draw the line of direction with some fancy math calc

	def handle_update(self, player_id, new_x, new_y, new_angle):
		"""
		handle a CLIENT_UPDATE or a SERVER_UPDATE
		both client and server uses this method
		"""
		if player_id == self.id:
			self.move(new_x, new_y, new_angle)
		else:
			opponent = self.world.get_player_from_id(player_id)
			if opponent is None:
				self.world.players.append(Player(new_x, new_y, self.world, player_id))
				self.world.players[len(self.world.players) - 1].last_pos = [new_x, new_y, new_angle]
			else:
				if abs(new_y - opponent.last_pos[1]) > 100:
					new_y = new_y // 10
				opponent.last_pos = (opponent.x, opponent.y, opponent.angle)
				opponent.move(new_x, new_y, new_angle)
				print("Ennemy moved, ", new_x, new_y, new_angle)


class World:
	def __init__(self, limit=5):
		# flemme de faire des commentaires pour le reste du fichier
		# c'est pas très intéressant c'est un monde et des murs en gros
		if limit > len(options.PLAYER_COLOR):
			raise Exception("World limit should not be greater than options.PLAYER_COLOR")
		self.limit = limit
		self.players = []
		self.next_id = 0
		self.alive = True
		self.walls = []
		self.walls_cord = []

	def init_walls(self):
		for y, row in enumerate(map_array):
			for x, tile in enumerate(row):
				if tile:
					self.walls_cord.append((x, y))
					self.walls.append(Wall((x * options.TILE, y * options.TILE)))

	def get_player_from_id(self, player_id):
		for player in self.players:
			if player.id == player_id:
				return player
		return None

	def remove_player_from_id(self, player_id):
		self.next_id = player_id
		player = self.get_player_from_id(player_id)
		if player.conn is not None:
			player.conn.close()
		self.players.remove(player)
		if len(self.players) == 0 and self.next_id != 0:
			self.next_id = 0

	def is_full(self):
		return len(self.players) == self.limit


class Wall:
	def __init__(self, cord: tuple):
		self.x = cord[0]
		self.y = cord[1]
		self.color = options.COLORS['black']
		self.size = options.TILE

	def draw(self, win):
		win.fill(self.color, pygame.Rect(self.x, self.y, self.size, self.size))