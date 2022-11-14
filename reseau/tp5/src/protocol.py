"""
Every valid packet should be as follow:

 00    00   00 00 00 00 00 00 00 00 
-ID-|-TYPE-|---------DATA----------|


The ID correspond to the client ID when the packet is upstream
and when it's downstream it can be the ID of another client.
Ex: if BOB moves, ALICE will receive a downstream packet with the ID of BOB to let
her know that he moved.

If user has no ID, it should be 0x00 and TYPE should be CLIENT_HELLO (11)
If the TYPE doesnt needs data, the DATA section should be empty

All packets must be 8 bytes long
"""
import struct
from struct import pack, unpack


PACKET_SIZE = 8

_EMPTY_DATA = b'\x00\x00\x00\x00\x00\x00'

types = {
	"SERVER_FULL": b'\xf0',
	"CLIENT_HELLO": b'\x01',
	"SERVER_HELLO": b'\xf1',
	"CLIENT_UPDATE": b'\x02',
	"SERVER_UPDATE": b'\xf2',
	"CLIENT_FREEZE": b'\x03',
	"SERVER_FREEZE": b'\xf3',
	"CLIENT_GOODBYE": b'\x0f',
	"SERVER_GOODBYE": b'\xff'
}

def is_valid(packet):
	# right now this function doesnt have a point since we could directly uses PACKET_SIZE instead of the func
	# but if later i use some other stuff to decide if a packet is valid or not, i would not
	# need to change every single file
	if len(packet) != PACKET_SIZE:
		return False
	return True


def read_packet(packet, err_log=True):
	try:
		packet_type = packet[1:2]
		client_id, _, x, y, angle = unpack("!BBHHh", packet)
		# We want packet_type to stay as bytes. 
		# when we unpack the packet, i choose to go with the oneliner
		# instead of slicing the packet into multiple parts to avoid calculing 
		# the packet_type (since we don't need to). I think it's: 
		# 1) cleaner code
		# 2) in terms of performance, i don't think it's really worse thank slicing the array multiple times 
	except struct.error as err:
		if err_log:
			print("Catched exception while reading packet: ", err)
		return None

	return {
		"id": client_id,  
		"type": packet_type,
		"x": x,
		"y": y,
		"angle": float(angle / 100)
	}


def SERVER_FULL():
	"""
	Server won't accept new players
	"""
	return b"\xff" + types["SERVER_FULL"] + _EMPTY_DATA

def CLIENT_HELLO():
	"""
	Clients wants to register
	"""
	return b"\xff" + types["CLIENT_HELLO"] + _EMPTY_DATA


def SERVER_HELLO(new_id, x, y):
	"""
	Response to a CLIENT_HELLO, providing a correct ID to use and some coordinates to spawn at
	"""
	return pack("!B", new_id) + types["SERVER_HELLO"] + pack("!H", x) + pack("!H", y) + b"\x00\x00"


def CLIENT_UPDATE(client_id, new_x, new_y, new_angle):
	"""
	The client informs the server that he is moving
	"""
	new_angle = int(new_angle * 100)
	return pack("!B", client_id) + types["CLIENT_UPDATE"] + pack("!H", new_x) + pack("!H", new_y) + pack("!h", new_angle)


def SERVER_UPDATE(client_id, new_x, new_y, new_angle):
	"""
	The server informs that client_id is moving
	"""
	new_angle = int(new_angle * 100)
	return pack("!B", client_id) + types["SERVER_UPDATE"] + pack("!H", new_x) + pack("!H", new_y) + pack("!h", new_angle)


def CLIENT_FREEZE(client_id, x, y, angle):
	"""
	The clients ask the server to freeze a client_id
	"""
	angle = int(angle * 100)
	return pack("!B", client_id) + types["CLIENT_FREEZE"] + pack("!H", x) + pack("!H", y) + pack("!h", angle)


def SERVER_FREEZE(client_id, x, y, angle):
	"""
	The server ask a client to freeze
	"""
	angle = int(angle * 100)
	return pack("!B", client_id) + types["SERVER_FREEZE"] + pack("!H", x) + pack("!H", y) + pack("!h", angle)



def CLIENT_GOODBYE(client_id):
	"""
	Client is leaving
	"""
	return pack("!B", client_id) + types["CLIENT_GOODBYE"] + _EMPTY_DATA


def SERVER_GOODBYE(client_id):
	"""
	Notify a client that someone is leaving
	"someone" can be the client himself
	"""
	return pack("!B", client_id) + types["SERVER_GOODBYE"] + _EMPTY_DATA