from __future__ import print_function
import sys
import time
from classes import *
from utilities import *
from rules import *
from player_input import *
from chessbot import *


#Top level function
def start_game():

	print("\nWelcome to Chess")
	print("This program is under development\n")


	#Initiate game class, get user input to define values for players and game mode
	g = Game()
	g.set_up_board()
	g.set_mode(get_game_mode())
	g.set_theory(load_theory())

	#If game mode is "load", load log from .chs file, execute moves, and exit program
	if g.mode == "load":
		g.log = get_file()
		play_test(g)
		exit()

	#Set boolean to True if game mode is test
	if g.mode == "test":
		output = True
	output = False

	#Get user input to define players
	get_players(g)

	#Define counter to track which player's turn is happening
	player = 1
	int_to_player = {1:g.white_player,0:g.black_player}

	#Go back and forth between white and black playing one turn each until checkmate or stalemate
	while keep_playing(int_to_player[player], g, True):

		play_turn(int_to_player[player], g, output)
		#increment the turn counter only if the completed turn was for black player
		g.turn = g.turn + 1 - player
		#switch the player counter
		player = 1 - player

	#Initiate end script
	g.display_board()
	g.draw_board()
	
	end_game(g)

#Play one turn for player p in game g; output is a boolean that indicates whether AI decision trees should be printed
def play_turn(p, g, output):

	#Display the board
	player_to_char = {g.white_player:'w',g.black_player:'b'}
	print(g.turn, end='')
	print(player_to_char[p])
	g.display_board()
	g.draw_board()

	#Either get player input or call AI decision tree
	if p.type == "human":
		m = get_move(p, g)
	else:
		m = get_computer_move(p,g,output)

	#Record the move in the game log
	record(g,m)

	#print the move in algebraic notation
	print(unparse(m,g))

	#implementent the move
	g.execute(m)

#Implement all moves from a .chs file
def play_test(g):
	
	player = 1
	int_to_player = {1:g.white_player,0:g.black_player}

	g.display_log()

	while keep_playing(int_to_player[player], g, True) and g.turn <= len(g.log):

		int_to_char = {1:'w',0:'b'}
		print(str(g.turn) + int_to_char[player] + ". ", end='')
		print(g.log[g.turn-1][1-player])

		#If last cell in the log (white moved last), option to analyze and break out of the loop
		if g.log[g.turn-1][1-player] == ".":
			print("Game Complete")
			
			#Player input to get a computer anlysis of final position
			if ask_analyze():
				int_to_player[player].type = ask_computer_type()
				get_computer_move(int_to_player[player], g, True).display()
			return

		m = parse(int_to_player[player], g, g.log[g.turn-1][1-player])
		g.execute(m)

		g.display_board()
		g.draw_board()

		#increment the turn counter only if the completed turn was for black
		g.turn = g.turn + 1 - player
		#switch the player counter
		player = 1 - player

	#If last cell in the log (black moved last), option to analyze and break out of the loop
	print("Game complete")
	if ask_analyze():
		int_to_player[player].type = ask_computer_type()		
		get_computer_move(int_to_player[player], g, True).display()

	return



start_game()










