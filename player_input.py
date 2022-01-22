from __future__ import print_function
import sys
import time
from classes import *
from utilities import *
from rules import *


prompt = "=> "

#Get user input to specify game mode, return one of three strings
def get_game_mode():

	print("Select game type:")
	print("\t(1) standard")
	print("\t(2) load")
	print("\t(3) test")
	print(prompt,end='')
	sys.stdout.flush()
	res = str_to_int(trim(sys.stdin.readline(16)))

	while res != 1 and res != 2 and res != 3:
		print("invalid input")
		print("Select game type:")
		print("\t(1) standard")
		print("\t(2) load")
		print("\t(3) test")
		print(prompt,end='')
		sys.stdout.flush()
		res = str_to_int(trim(sys.stdin.readline(16)))

	mode_return = {1:"standard",2:"load",3:"test"}
	return mode_return[res]

#Get user input to define player parameters, updates player classes in g
def get_players(g):

	print("Enter name for player controlling white pieces:")
	print(prompt,end='')
	sys.stdout.flush()
	res = trim(sys.stdin.readline(32))

	g.white_player.name = res

	print("Select player type:")
	print("\t(1) Human")
	print("\t(2) Computer: beta_1")
	print("\t(3) Computer: beta_2")
	print(prompt,end='')
	sys.stdout.flush()
	res = str_to_int(trim(sys.stdin.readline(16)))

	while res != 1 and res != 2 and res != 3:
		print("invalid input")
		print("Select player type:")
		print("\t(1) Human")
		print("\t(2) Computer: beta_1")
		print("\t(3) Computer: beta_2")
		print(prompt,end='')
		sys.stdout.flush()
		res = str_to_int(trim(sys.stdin.readline(16)))

	type_return = {1:"human",2:"beta_1",3:"beta_2"}
	g.white_player.type = type_return[res]

	print("Enter name for player controlling black pieces:")
	print(prompt,end='')
	sys.stdout.flush()
	res = trim(sys.stdin.readline(32))

	g.black_player.name = res

	print("Select player type:")
	print("\t(1) Human")
	print("\t(2) Computer: beta_1")
	print("\t(3) Computer: beta_2")
	print(prompt,end='')
	sys.stdout.flush()
	res = str_to_int(trim(sys.stdin.readline(16)))

	while res != 1 and res != 2 and res != 3:
		print("invalid input")
		print("Select player type:")
		print("\t(1) Human")
		print("\t(2) Computer: beta_1")
		print("\t(3) Computer: beta_2")
		print(prompt,end='')
		sys.stdout.flush()
		res = str_to_int(trim(sys.stdin.readline(16)))

	g.black_player.type = type_return[res]

#Get user input to make a move (input must be in algebraic notation), returns a move (class)
def get_move(p, g):

	print(prompt,end='')
	sys.stdout.flush()
	res = trim(sys.stdin.readline(16))
	m = parse(p, g, res)

	#Verify that input can be parsed and that the specified move is legal
	while m == None or legal_move(m, g, True) == False:
		print(prompt,end='')
		sys.stdout.flush()
		res = trim(sys.stdin.readline(16))
		m = parse(p, g, res)
	
	return m

#user specifies .chs filename, returns log format (2xturns matrix of strings)
def get_file():
	print("Specify .chs test file (without file extension):")
	print(prompt,end='')
	sys.stdout.flush()
	file_name = trim(sys.stdin.readline(256))
	path = "Saved Games/" + file_name + ".chs"

	myfile = open(path, 'r')
	my_text = myfile.readlines()
	
	return text_to_log(my_text)

#user specifies whether game log should be saved
def ask_save_log(g):

	res = "unset"
	while res[0] != 'n' and res[0] != 'y':
		print("Would you like to save the game log? (y/n)")
		print(prompt,end='')
		sys.stdout.flush()
		res = trim(sys.stdin.readline(16))

	if res[0] == 'n':
		return

	#add a . if game ended on Black's turn
	if len(g.log[g.turn-2]) == 1:
		g.log[g.turn-1].append(".")

	g.write_log()
	return

#user specifies there should be computer analysis of final position
def ask_analyze():
	res = "unset"
	while res[0] != 'n' and res[0] != 'y':
		print("Would you like to analyze this board? (y/n)")
		print(prompt,end='')
		sys.stdout.flush()
		res = trim(sys.stdin.readline(16))

	if res[0] == 'n':
		return False

	return True

#valid_command examines player input string s to determine if it is plausibel chess algebra
#it does not make any determination about the legality of the proposed move
#Returns a boolean
def valid_command(s):

	#Define sets of characters
	x_values = ['a','b','c','d','e','f','g','h']
	y_values = ['1','2','3','4','5','6','7','8']
	other_values = ['x','R','N','B','Q','K']

	#test castle
	if s == "0-0" or s == "0-0-0":
		return True

	#test surrender
	if s == "QQ":
		return True
	
	#test promotion
	if '=' in s:
		prom_values = ['Q','R','B','N']

		#case in which pawn moves forward one tile to promote
		if len(s) == 4:
			if s[0] in x_values and (s[1] == '1' or s[1] == '8') and s[2] == '=' and s[3] in prom_values:
				return True
			else:
				return False

		#case in which pawn captures diagonally to promote
		if len(s) == 6:
			if s[0] in x_values and s[1] == 'x' and s[2] in x_values and (s[3] == '1' or s[3] == '8') and s[4] == '=' and s[5] in prom_values:
				return True
			else:
				return False
		else:
			return False

	#don't permit pawn moves to end row without promotion
	if s[0] in x_values and (s[1] == '1' or s[1] == '8') and s[2] != '=':
		return False

	#test length
	if len(s) > 5 or len(s) < 2:
		return False

	#character by character parameters (working backwards)
	i = 1
	while i <= len(s):

		#isolate the ith to last character in the string
		char = s[len(s)-i]

		#last char
		if i == 1:
			if char not in y_values:
				return False

		#second to last char
		elif i == 2:
			if char not in x_values:
				return False

		#third to last char
		elif i == 3:
			if len(s) == 3:
				if char not in other_values:
					return False
			if len(s) == 4:
				if char not in x_values and char not in y_values and char not in other_values:
					return False
			if len(s) == 5:
				if char != 'x':
					return False

		#fourth to last char
		elif i == 4:
			if len(s) == 4:
				if char not in x_values and char not in other_values:
					return False
			if len(s) == 5:
				if char not in x_values and char not in y_values:
					return False

		else:
			if char not in other_values:
				return False

		i = i + 1

	return True
	
#Takes a chess algebra string s and evaluates as a move m for player p in game g
#returns a move or None if string is not parsable
def parse(p, g, s):

	if s == "":
		return None

	#Check that s adheres to the basic requirements of chess algebra
	if valid_command(s) == False:
		return None

	#Deal with surrender, exits function
	if s == "QQ":
		surrender(p,g)

	#deal with castling
	if s[0] == '0':

		if p.color == "white":
			x_coord = 0
		else:
			x_coord = 7

		from_y_coord = 4
		if len(s) == 3:
			to_y_coord = 6
		else:
			to_y_coord = 2

		res = Move(g.board[x_coord][from_y_coord],g.board[x_coord][to_y_coord],p,True)
		res.type = "castle"

		return res

	#deal with promotion
	if '=' in s:
		res = parse(p,g,s[:-2])
		res.type = "promotion=" + s[len(s)-1]
		print("set move type to: " + res.type)
		return res 

	#Take last two characters as coordinates for to_tile
	x = s[len(s)-1]
	y = s[len(s)-2]
	char_to_coord = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
	x_coord = str_to_int(x) - 1
	y_coord = char_to_coord[y]
	t = g.board[x_coord][y_coord]

	#identify type of piece by first character
	if s[0] == 'K' or s[0] == 'Q' or s[0] == 'B' or s[0] == 'N' or s[0] == 'R': 
		c = s[0]
	else:
		c = 'P'

	#generate a list of tiles with pieces of specified type that can move to to_tile
	tile_list = find_tile(p, g, c, t)
	
	#deal with en_passant
	if c == 'P' and t.occupant == None and g.en_passant != None and t.x == g.en_passant.x and ((p.color == "white" and t.y - g.en_passant.y == 1) or (p.color == "black" and t.y - g.en_passant.y == -1)):
		
		#Only one pawn is in position to capture en passant
		if len(tile_list) == 1:
			res = Move(tile_list[0], t, p, g)
			res.type = "en passant"
			return res

		#Two pawns are in position to capture en passant
		else:
			for x in tile_list:
				if x.x == s[0]:
					res = Move(tile_list[0], t, p, g)
					res.type = "en passant"
					return res

	#If there are no pieces of specified type that can move to specified type, then return None
	if len(tile_list) == 0:
		return None

	#if only one tile in list, use it as from_tile
	elif len(tile_list) == 1:
		return Move(tile_list[0], t, p, True)

	#if two or more, then use the second char to ID correct tile
	elif c == 'R' or c == 'N' or c == 'B' or c == 'Q':
		if len(s) != 4 and len(s) != 5:
			return None
		z = s[1]
		for tile in tile_list:
			if tile.name()[0] == z or tile.name()[1] == z:
				return Move(tile, t, p, True)
		return None

	#except for pawns, which require first char
	elif c == 'P':
		for tile in tile_list:
			if tile.name()[0] == s[0]:
				return Move(tile, t, p, True)
		return None

	else:
		return None

def unparse(m, g):
	res = []
	c = m.from_tile.occupant.type
	player = m.player.color

	#Which piece is being moved?
	#If Castle, just return the standard castle strings
	if m.type == "castle":
		if m.to_tile.x == 2:
			return "0-0-0"
		else:
			return "0-0"
	#for non-pawns, add type character
	elif c != 'P':
		res.append(c)
	#for a pawn capture, add starting file
	elif m.to_tile.occupant != None or m.type == "en_passant":
		res.append(m.from_tile.name()[0])

	#Is the move ambiguous?
	tile_list = find_tile(m.player, g, c, m.to_tile)
	if len(tile_list) > 1:
		#If files are different, add starting file
		if tile_list[0].x != tile_list[1].x:
			res.append(m.from_tile.name()[0])
		#otherwise, add starting rank
		else:
			res.append(m.from_tile.name()[1])

	#Is the move a capture?
	if m.to_tile.occupant != None:
		res.append('x')

	#add destination tile name
	res.append(m.to_tile.name()[0])
	res.append(m.to_tile.name()[1])

	#Was a pawn promoted?
	if "promotion" in m.type:
		res.append(m.type[len(m.type)-2])
		res.append(m.type[len(m.type)-1])

	return "".join(res)

#Return a list of tiles containing pieces of type c belonging to player p that can legally move to tile t in game g
def find_tile(p, g, c, t):
	candidates = find(c,p,g)
	res = []
	for x in candidates:
		if legal_move(Move(x,t,p,False),g,False):
			res.append(x)
	return res

#Record move m in the log for game g
def record(g, m):
	if m.player.color == "white":
		g.log.append([])
	g.log[g.turn-1].append(unparse(m, g))

#Initiate end of game script following a surrender
def surrender(p, g):
	print(p.name + " surrenders")
	end_game(g)

#Ask whether log should be saved, exit program
def end_game(g):
	ask_save_log(g)
	print("Thanks for playing!")
	exit()

def ask_computer_type():

	type_return = {1:"beta_1",2:"beta_2"}


	print("Select player type:")
	print("\t(1) Computer: beta_1")
	print("\t(2) Computer: beta_2")
	print(prompt,end='')
	sys.stdout.flush()
	res = str_to_int(trim(sys.stdin.readline(16)))

	while res != 1 and res != 2:
		print("invalid input")
		print("Select player type:")
		print("\t(1) Computer: beta_1")
		print("\t(2) Computer: beta_2")
		print(prompt,end='')
		sys.stdout.flush()
		res = str_to_int(trim(sys.stdin.readline(16)))

	return type_return[res]