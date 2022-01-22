from __future__ import print_function
from utilities import *
from classes import *
import sys
import time

#Return True is move m can legally me made in game g
#test_check is a boolean that indicates whether the function should consider revealed check
def legal_move(m, g, test_check):

	p = m.from_tile.occupant
	d = distance(m.from_tile, m.to_tile)
	ptype = path_type(m.from_tile, m.to_tile)

	#Verify that destination tile is not already occupied by one of the moving player's pieces
	if m.to_tile.occupant != None and m.to_tile.occupant.color == m.player.color:
		if m.real:
			print("Invalid move: Tile occupied by player's own piece")
		return False

	#Normal moves
	if m.type == "normal":

		#Verify that path all intermediate tiles are empty (unless the moving piece is a knight)
		if p.type != 'N' and not clear_path(m,g):
			if m.real:
				print("Invalid move: Path obstructed")
			return False

		#Rules for kings
		if p.type == 'K':

			#Kings can only move a distance of 1
			if d > 1 :
				if m.real:
					print("Invalid move: Kings can only move one space unless castling")
				return False

		#Rules for queens
		if p.type == 'Q':
			if ptype == "other":
				if m.real:
					print("Invalid move: Queen can only move along straight lines or diagonals")
				return False

		if p.type == "R":
			if ptype != "straight":
				if m.real:
					print("Invalid move: Rooks can only move along straight lines")
				return False

		#Rules for bishops
		if p.type == 'B':
			if ptype != "diagonal":
				if m.real:
					print("Invalid move: Bishops can only move along diagonals")
				return False

		#Rules for knights
		if p.type == 'N':
			if ptype != "other" or d != 2:
				if m.real:
					print("Invalid move: Knights can only move in the 'L' shape")
				return False

		#Rules for pawns
		if p.type == 'P':

			#Pawns must move forwards
			if (m.player.color == "white" and m.to_tile.y - m.from_tile.y <= 0) or (m.player.color == "black" and m.to_tile.y - m.from_tile.y >= 0):
				if m.real:
					print("Invalid move: Pawns can only advance towards the opponent's side")
				return False

			#Pawns move 1 tile unless it's their first move, in which case they may move 2
			if d == 2 and ((m.player.color == "white" and m.from_tile.y != 1) or (m.player.color == "black" and m.from_tile.y != 6)):
				if m.real:
					print("Invalid move: Pawns can only move two spaces if they haven't already been moved")
				return False

			#Pawns can't capture if they're moving 2 spaces
			if d == 2 and m.to_tile.x != m.from_tile.x:
				if m.real:
					print("Invalid move: If moving two spaces, pawns must move in a straight line")
				return False

			#Pawns can never move more than 2 tiles
			if d > 2:
				if m.real:
					print("Invalid move: Pawns can never move more than two spaces at a time")
				return False

			#Pawns can only capture diagonally
			if m.to_tile.x == m.from_tile.x and m.to_tile.occupant != None:
				if m.real:
					print("Invalid move: Pawns can only capture diagonally")
				return False

			#Pawns can only move diagonally when capturing
			if m.to_tile.x != m.from_tile.x and m.to_tile.occupant == None:
				if m.real:
					print("Invald move: Pawns can only move diagonally if capturing")
				return False

	#Castling moves
	elif m.type == "castle":

		#Verify that moving player is not currently in check
		if in_check(m.player, g):
			if m.real:
				print("Invalid move: Cannot castle out of check")
			return False

		#Verify that moving player has not yet moved their King or relevant rook
		if m.to_tile.x == 6 and not m.player.short_castle:
			if m.real:
				print("Invalid move: Player can no longer castle kingside")
			return False

		if m.to_tile.x == 3 and not m.player.long_castle:
			if m.real:
				print("Invalid move: Player can no longer castle queenside")
			return False

		#Verify that the relevant rook hasn't been captured
		if ((m.to_tile.x == 6 and g.board[m.from_tile.y][7].occupant != None
			and (g.board[m.from_tile.y][7].occupant.type != 'R' or g.board[m.from_tile.y][7].occupant.color != m.player.color)) 
			or (m.to_tile.x == 3 and g.board[m.from_tile.y][0].occupant != None
			and (g.board[m.from_tile.y][0].occupant.type != 'R' or g.board[m.from_tile.y][0].occupant.color != m.player.color))):
			if m.real:
				print("Invalid move: Player cannot castle without Rook")
			return False

		#Verify that all intermediate tiles are unthreatened and unoccupied
		if p.color == "white":
			if m.to_tile.name() == "c1":
				if can_attack(g.black_player, g.board[0][3], g):
					if m.real:
						print("Invalid move: d1 is threatened")
					return False
				for i in range(1,4):
					if g.board[0][i].occupant != None:
						if m.real:
							print("Invalid move: castling path obstructed")
						return False
			elif m.to_tile.name() == "g1":
				if can_attack(g.black_player, g.board[0][5], g):
					if m.real:
						print("Invalid move: f1 is threatened")
					return False
				for i in range(5,7):
					if g.board[0][i].occupant != None:
						if m.real:
							print("Invalid move: castling path obstructed")
						return False
			else:
				if m.real:
					print("Invlaid move: Cannot castle to specified tile")
				return False
		else:
			if m.to_tile.name() == "c8":
				if can_attack(g.white_player, g.board[7][3], g):
					if m.real:
						print("Invalid move: d8 is threatened")
					return False
				for i in range (1,4):
					if g.board[7][i].occupant != None:
						if m.real:
							print("Invalid move: castling path obstructed")
						return False
			elif m.to_tile.name() == "g8":
				if can_attack(g.white_player, g.board[7][5], g):
					if m.real:
						print("Invalid move: f8 is threatened")
					return False
				for i in range (5,7):
					if g.board[7][i].occupant != None:
						if m.real:
							print("Invalid move: castling path obstructed")
						return False
			else:
				if m.real:
					print("Invalid move: Cannot castle to specified tile")
				return False

	elif m.type == "en passant":

		#Verify that the opposing player has a pawn that can be captured en passant
		if g.en_passant == None:
			if m.real:
				print("Invalid en passant move: no pawns are elgible to be captured en passant")
			return False

		#Verify that the designated destination is the correct tile for en passant capture
		if (m.to_tile.x != g.en_passant.x) or (p.color == "white" and m.to_tile.y != 6) or (p.color == "black" and m.to_tile != 3):
			if m.real:
				print("Invalid en passant move: designated destination is incorrect")
			return False

		#Verify that the designated pawn is in position to capture en passant
		if (m.from_tile.y != g.en_passant.y) or (abs(m.from_tile.x - g.en_passant.x) != 1):
			if m.real:
				print("Invalid en passant move: designated piece in not position to capture en passant")
			return False

	elif "promotion" in m.type:

		#Pawns must move forwards
		if (m.player.color == "white" and m.to_tile.y - m.from_tile.y <= 0) or (m.player.color == "black" and m.to_tile.y - m.from_tile.y >= 0):
			if m.real:
				print("Invalid promotion move: Pawns can only advance towards the opponent's side")
			return False

		#Promoting awns move 1 tile
		if d != 1:
			if m.real:
				print("Invalid promotion move: promoting pawns can only move 1 tile")
			return False

		#Pawns can only capture diagonally
		if m.to_tile.x == m.from_tile.x and m.to_tile.occupant != None:
			if m.real:
				print("Invalid move: Promoting pawns can only capture diagonally")
			return False

		#Pawns can only move diagonally when capturing
		if m.to_tile.x != m.from_tile.x and m.to_tile.occupant == None:
			if m.real:
				print("Invald move: Promoting pawns can only move diagonally if capturing")
			return False

	else:
		call_error(7)

	#Player cannot make a move that puts themselves in check
	if test_check:
		g1 = g.clone()
		m1 = m.clone(g1)
		g1.execute(m1)
		if in_check(m1.player, g1):
			if m.real:
				print("Invalid move: Results in check")
			return False

	#move passes all relevant tests
	return True

#Returns distance between two tile in terms of turns for a King to travel from t1 to t2
def distance(t1, t2):
	x_distance = abs(t1.x - t2.x)
	y_distance = abs(t1.y - t2.y)
	return max(x_distance, y_distance)

#Identifies the path from t1 to t2 as "straight", "diagonal", or "other"
def path_type(t1, t2):
	if t1.x == t2.x or t1.y == t2.y:
		return "straight"
	if abs(t1.x - t2.x) == abs(t1.y - t2.y):
		return "diagonal"
	return "other"

#Returns True if a given move is unobstructed
def clear_path(m, g):
	t1 = m.from_tile
	t2 = m.to_tile
	res = []

	#Test straight path moves in a given olumn
	if t1.x == t2.x:
		for i in range(min(t1.y,t2.y)+1, max(t1.y,t2.y)):
			if g.board[i][t1.x].occupant != None:
				return False
		return True

	#Test straight path moves in a given row
	if t1.y == t2.y:
		for i in range(min(t1.x, t2.x)+1, max(t1.x,t2.x)):
			if g.board[t1.y][i].occupant != None:
				return False
		return True

	#Test diagonal moves
	if abs(t1.x - t2.x) == abs(t1.y - t2.y):

		#SW -> NE
		if t1.x < t2.x and t1.y < t2.y:
			for i in range(1, abs(t1.x-t2.x)):
				if g.board[t1.y + i][t1.x + i].occupant != None:
					return False
			return True

		#NW ->SE
		if t1.x < t2.x and t1.y > t2.y:
			for i in range(1, abs(t1.x-t2.x)):
				if g.board[t1.y - i][t1.x + i].occupant != None:
					return False
			return True

		#SE -> NW
		if t1.x > t2.x and t1.y < t2.y:
			for i in range(1, abs(t1.x-t2.x)):
				if g.board[t1.y + i][t1.x - i].occupant != None:
					return False
			return True

		#NE -> SW
		if t1.x > t2.x and t1.y > t2.y:
			for i in range(1, abs(t1.x-t2.x)):
				if g.board[t1.y - i][t1.x - i].occupant != None:
					return False
			return True

	#All non-straight, non-diagaonal paths return True
	return True

#Returns True if player p is in check
def in_check(p, g):

	opponent = g.white_player
	if p.color == "white":
		opponent = g.black_player

	return can_attack(opponent, find('K',p,g)[0], g)

#Return True if player p can attack attack the piece on tile t in game g
def can_attack(p,t,g):

	#from classes import Move

	if t == None:
		call_error(4)

	for i in range(8):
		for j in range(8):
			if g.board[i][j] != t and g.board[i][j].occupant != None and g.board[i][j].occupant.color == p.color and legal_move(Move(g.board[i][j], t, p, False), g, False):
				return True
	return False

#Returns a list of tiles from g.board that contain a piece of type c belonging to player p in game g
def find(c,p,g):
	res = []
	for i in range(8):
		for j in range(8):
			if g.board[i][j].occupant != None and g.board[i][j].occupant.type == c and g.board[i][j].occupant.color == p.color:
				res.append(g.board[i][j])

	return res

#Return true if player p has any legal move, else return false
#message is a boolean that indicates whether the function prints out a status
def keep_playing(p, g, message):

	#Repeating cycles of moves end the game
	if g.log_cycle == 2:
		return False

	for i in range(8):
		for j in range(8):
			if g.board[i][j].occupant != None and g.board[i][j].occupant.color == p.color and can_move(p,g,g.board[i][j]):
				
				return True
	return False

	if message:
		if in_check(p,g):
			print(p.color + " player in checkmate")
		else:
			print("Stalemate")
			
	return False


def can_move(p, g, t):

	for i in range(8):
		for j in range(8):
			if legal_move(Move(t, g.board[i][j], p, False), g, True):
				return True

	return False















