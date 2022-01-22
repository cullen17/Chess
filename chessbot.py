from __future__ import print_function
import sys
import time
from classes import *
from utilities import *
from rules import *
from player_input import *
import random
import os

#Activate decision trees to select the best move for player p in game g
#Output is a boolean that indicates whether the decision tree should be printed
def get_computer_move(p, g, output):

	#Try for a theory move if available
	tm = None
	if g.turn <= 10:
		tm = theory_move(p, g)

	if tm != None:
		return tm

	#If no theory is available, set parameters and build decision trees
	trees = build_trees(p, g, get_parameters(p.type), 1)
	rescore(trees)

	print()

	#Select the best scored move
	m = choose_move(trees, g)
	m.real = True

	#print output, if specified
	if output:
		update_output(trees, g)

	return m

#Assign a score to a given move
def score(m, p, g, weights):

	#Check that the given game has not already ended
	if not keep_playing(p, g, False):
		call_error(8)

	#Enter the hypothetical in which the move has been made
	g1 = g.clone()
	m1 = m.clone(g1)
	g1.execute(m1)

	m.score = board_score(m1, p, g1, weights)

	return

#Calculate score for a board position
def board_score(m, p, g, weights):
	
	#Identify opponent
	o = g.white_player
	if p.color == "white":
		o = g.black_player

	#Assign scores for checkmate and stalemate
	if not keep_playing(o, g, False):
		if in_check(o, g):
			return 1000
		else:
			return 0

	#Counters
	gross_material = tally_material(g)
	net_material = 0
	score = 0

	#Weights
	Ct = weights[0]
	Ch = weights[1]
	K = weights[2]
	PA = weights[3]
	Dv = weights[4]
	Cs = weights[5]
	CX = weights[6]

	#Adjust weights for game stage...
	#Middle game
	if gross_material >= 28 and gross_material < 66:
		Dv = .5*Dv

	#Late game
	elif gross_material < 28:
		Ct = 0
		K = 0
		PA = 5*PA
		Dv = 0
		CS = 0
		CX = 0

	piece_to_score = {'P':1,'B':3,'N':3,'Q':9,'R':5,'K':0}

	#Adjust score for check
	if in_check(p, g):
		score = score - Ch
	if in_check(o, g):
		score = score + Ch

	#Adjust score for castling
	if p.castled:
		score = score + Cs
	if o.castled:
		score = score - Cs
	if (not p.short_castle) and (not p.long_castle):
		score = score - CX
	if (not p.short_castle) and (not p.long_castle):
		score = score + CX

	#Adjust score for position and material
	for i in range(8):
		for j in range(8):
			if g.board[i][j].occupant == None:
				continue

			#Raw material
			c = g.board[i][j].occupant
			if c.color == p.color:
				sign = 1
			else:
				sign = -1
			score = score + sign*piece_to_score[c.type]

			#Center control
			if g.turn <= 20:
				if g.board[i][j].name() == "d4" or g.board[i][j].name() == "d5" or g.board[i][j].name() == "e4" or g.board[i][j].name() == "e5":
					score = score + sign*Ct*piece_to_score[c.type]

			#King position
			if g.turn <= 40:
				if c.type == 'K':
					score = score + sign*K*(min(abs(3-i), abs(i-4)) + min(abs(3-j), abs(j-4)))
					
			#Advance pawns
			if c.type == 'P':
				if c.color == "white":
					score = score + sign*PA*(j - 2)
				else:
					score = score + sign*PA*(7 - j)

			#Develop Pieces
			if g.turn <= 30:
				if c.type == 'B':
					if p.color == "white" and g.board[i][j].name() != "c1" and g.board[i][j].name() != "f1":
						score = score + sign*Dv*3
					elif p.color == "black" and g.board[i][j].name() != "c8" and g.board[i][j].name() != "f8":
						score = score + sign*Dv*3

				if c.type == 'N':
					if p.color == "white" and g.board[i][j].name() != "b1" and g.board[i][j].name() != "g1":
						score = score + sign*Dv*3
					elif p.color == "black" and g.board[i][j].name() != "b8" and g.board[i][j].name() != "g8":
						score = score + sign*Dv*3

				if c.type == 'Q':
					if p.color == "white" and g.board[i][j].name() != "d1":
						score = score + sign*Dv*3
					elif p.color == "black" and g.board[i][j].name() != "d8":
						score = score + sign*Dv*3

	return score

#Return a list of all possible moves that player p can make in game g, scoring with weights
def all_player_moves(p ,g, weights):
	
	res = []
	for i in range(8):
		for j in range(8):
			if g.board[i][j].occupant != None and g.board[i][j].occupant.color == p.color:
				res = res + all_piece_moves(p, g, g.board[i][j], weights)

	#print("leaving all_player moves")
	return res

#Return a list of all possible moves that player p's piece on tile t can make in game g scoring with weights
def all_piece_moves(p, g, t, weights):

	res = []
	for i in range(8):
		for j in range(8):
			m = Move(t, g.board[i][j], p, False)
			m.type = get_move_type(m, g)

			if legal_move(m, g, True):
				res.append(m)
				score(m, p, g, weights)
	return res

#Return a list of trees for player p in game g of specified parameters
#level is an indicator to track recursion
def build_trees(p, g, pm, level):

	depth = pm[0]
	breadth = pm[1]
	weights = pm[2:]

	#Indicate that computer is thinking by printng a period each time a new branch is created
	if level == 2:
		print(".",end='')
		sys.stdout.flush()

	#Recursive bottom
	res = []
	if level > depth:
		return res

	#Identify opponent
	if p.color == "white":
		opponent = g.black_player
	else:
		opponent = g.white_player

	#Ignore breadth constraint at the top level
	if level == 1:
		moves = all_player_moves(p, g, weights)
		#If move results in checkmate, return it as a singleton
		for m in moves:
			if m.score == 1000:
				return [Tree(m)]
	else:
		moves = some_player_moves(p, g, breadth, weights)

	for move in moves:
		t = Tree(move)

		g1 = g.clone()
		m1 = move.clone(g1)
		g1.execute(m1)

		#Build another level as long as the game isn't in checkmate or stalemate
		if keep_playing(opponent, g1, False):
			t.children = build_trees(opponent, g1, pm, level+1)
			res.append(t)

	return res

#Returns a list of the most promising breadth moves for player p in game g
def some_player_moves(p, g, breadth, weights):
	moves = all_player_moves(p, g, weights)
	if len(moves) <= breadth or breadth == -1:
		return moves

	res = []
	for i in range(breadth):
		best = moves[0]
		for move in moves:
			if move.score > best.score:
				best = move
		res.append(best)
		moves.remove(best)
	return res

#Recursively assign the score of the best branch to each top level move
def rescore(trees):
	if trees == []:
		return

	for t in trees:
		if t.children != []:
			rescore(t.children)
			t.parent.score = -1*best_score(t.children)

#Identify the best score from a list of trees
def best_score(trees):
	if trees == []:
		call_error(6)

	res = trees[0].parent.score
	for t in trees:
		if t.parent.score > res:
			res = t.parent.score

	return res

#print out tree t
def show_path(t):
	t.parent.display()
	if t.children == []:
		return

	for t1 in t.children:
		if t1.parent.score == -1*t.parent.score:
			show_path(t1)
			return

#Assign the correct type to move m in game g
def get_move_type(m, g):
	if m.from_tile.occupant.type == 'K' and abs(m.to_tile.x - m.from_tile.x) == 2:
		return "castle"

	elif m.from_tile.occupant.type == 'P' and ((m.player.color == "white" and m.to_tile.y == 7) or (m.player.color == "black" and m.to_tile.y == 0)):
		return "promotion=Q"

	elif g.en_passant != None and m.from_tile.occupant.type == 'P' and m.to_tile.x != m.from_tile.x and m.to_tile.occupant == None and m.to_tile.y == g.en_passant.y:
		return "en passant"

	return "normal"

#Select a move from list of trees
def choose_move(trees, g):
	best = trees[0].parent.score
	for t in trees:
		if t.parent.score > best:
			best = t.parent.score

	candidates = []
	for t in trees:
		if t.parent.score == best:
			candidates.append(t.parent)
			#t.parent.display()

	if len(candidates) > 1:
		rand = random.randrange(len(candidates))
		return candidates[rand]

	#If there's only one optimal move, there's a 1 in 10 chance of choosing the second best move
	# rand = random.randrange(10)
	# #print(rand)
	# if rand == 0 and len(trees) > 1:
	# 	#print("Choosing sub-optimal")
	# 	for t in trees:
	# 		if t.parent == candidates[0]:
	# 			trees.remove(t)
	# 	return choose_move(trees)

	#In this new version, we actually check the log to see if there's a cycle emerging
	#If Hal perceives themselves to be losing by a significant margin, they will always choose the top move
	#Otherwise, they will opt to avoid cycles by reverting to the second best move

	if len(trees) > 1 and g.log_cycle() == 1 and candidates[0].score > -2:
		for t in trees:
			if t.parent == candidates[0]:
				trees.remove(t)
		return choose_move(trees, g)


	return candidates[0]

#Sort and display a list of trees
def sort_and_show(trees, g, init):

	if init:
		trees1 = []
		for t in trees:
			trees1.append(t.clone(g))

		sort_and_show(trees1, g, False)
		return

	if len(trees) == 1:
		trees[0].parent.display()
		return

	best = trees[0]
	for t in trees:
		if t.parent.score > best.parent.score:
			best = t

	best.parent.display()
	
#Print output for trees 
def update_output(trees, g):

	file_name = g.white_player.name + " vs " + g.black_player.name + " Chessbot output"
	path = "Chessbot output/" + file_name +".txt"
	myfile = open(path,'a')

	print("*********************************************************************", file=myfile)
	print("Turn " + str(g.turn), file=myfile)

	myfile.close()

	trees = sort(trees)

	for t in trees:
		write_levels(t, g, 1, path)

#Sort list of trees by score
def sort(trees):

	trees_res = []

	for t in trees:
		t.children = sort(t.children)

	length = len(trees)

	while len(trees_res) < length:
		best = 0
		for i in range(len(trees)):
			if trees[i].parent.score > trees[best].parent.score:
				best = i

		trees_res.append(trees[best])
		trees.remove(trees[best])

	return trees_res

#Write level l of tree t in game g to specified file path 
def write_levels(t, g, l, path):
		
		f = open(path,'a')

		for i in range(l):
			print("\t",end='', file=f)

		color_return = {"white":'w',"black":'b'}

		print(color_return[t.parent.from_tile.occupant.color] + ": " + unparse(t.parent, g)+ "\t" +str(t.parent.score), file=f)

		f.close()

		for child in t.children:
			write_levels(child,g,l+1,path)

#Check theory logs and return a move if available
def theory_move(p, g):

	player_coord = 0
	if p == g.black_player:
		player_coord = 1

	#identify all theory logs that apply
	on_path = []
	for l in g.theory:
		if g.log_subset(l):
			on_path.append(l)

	#if there are none, return empty
	if len(on_path) == 0:
		return None

	#if only one, return the next move
	if len(on_path) == 1:
		return parse(p, g, on_path[0][g.turn-1][player_coord])

	#if 2 or more, choose randomly between the available
	if len(on_path) > 1:
		rand = random.randrange(len(on_path))
		return parse(p, g, on_path[rand][g.turn-1][player_coord])

#Specify parameters for each AI type
def get_parameters(player_type):

	'''
	Paramenter registery:
	D: Depth
	B: Breadth
	Ct: Center weight
	Ch: Check weight
	K: King weight
	PA: Pawn Advance weight
	Dv: Development weight
	CS: Castling weight
	'''

		#	[D,	B,	Ct,	Ch,	K,	PA,	Dv,	Cs,	X,	X,	X,	X]
	beta_1 = 	[4, 6,	.2,	1,	.1,	.1,	.2,	1,	1,	0,	0,	0]
	beta_2 = 	[5, 4,	.2,	1,	.1,	.1,	.2,	1,	1,	0,	0,	0]


	if player_type == "beta_1":
		return beta_1
	elif player_type == "beta_2":
		return beta_2
	else:
		call_error(9)

#Tally the gross material on the board
def tally_material(g):

	piece_to_score = {'P':1,'B':3,'N':3,'Q':9,'R':5,'K':0}

	res = 0

	for i in range(8):
		for j in range(8):
			if g.board[i][j].occupant != None:
				res = res + piece_to_score[g.board[i][j].occupant.type]

	return res

