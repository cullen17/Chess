from __future__ import print_function
import sys
import time


def call_error(n):
	error_message = {1:"unrecognized move type in classes/game/execute",
	2:"invalid move passed to classes/move/display()",
	3:"invalid move type passed to rules/clear_path()",
	4:"Empty tile passed to rules/can_attack()",
	5:"You moved a pawn to the end rank without promoting; now your computer is broken and it's all your fault",
	6:"chessbot/best_score() called on an empty list of trees",
	7:"unrecognized move type passed to legal_move()",
	8:"move passed to chessbot/score() for a game that had alread ended",
	9:"unrecognized player_type passed to chessbot/get_parameters()"}
	print("error: "+error_message[n])
	exit()

def trim(string):
	strang = []
	for a in string:
		if a != '\n':
			strang.append(a)
	return "".join(strang)

def str_to_int(string):
	res = 0
	for i in range(len(string)):
		num = ord(string[i])
		if num < 48 or num > 57:
			call_error(2)
		res = res*10
		res = res+((num)-48)
	return res







	























