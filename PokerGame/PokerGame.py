"""
    Module, that starts game...
"""

import sys
from table import Table
from player import Player

game_matrix = [[],[],[],
               [],[],[],
               [],[],[]]





def print_game(matrix):

    print("sfdgbfhgnjhkjl")
    #clear_scr()

    console = sys.stdout

    # print table
    console.write("┌")


#print_game(game_matrix)


def init_game():
    table = Table(50, Player("Vasya", 1500), Player("Petya", 1200), Player("Dusia", 2000))
                  #Player("Anya", 1500), Player("Vova", 1500), Player("Pupsik", 1500),
                  #Player("Serhio", 1500), Player("Pedro", 1500), Player("Margo", 1500))

    table.pre_flop()
    table.ask_players("pre-flop")
    
    table.flop()
    table.ask_players("flop")

    table.turn()
    table.ask_players("turn")

    table.river()
    table.ask_players("river")
    
    table.show_winner()


init_game()