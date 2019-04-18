"""
    Module, that starts game...
"""

from table import Table
from player import Player


def init_game():
    table = Table(50, Player("Vasya", 1500), Player("Petya", 1200), Player("Dusia", 2000))
                  #Player("Anya", 1500), Player("Vova", 1500), Player("Pupsik", 1500),
                  #Player("Serhio", 1500), Player("Pedro", 1500), Player("Margo", 1500))

    while True:
        table.pre_flop()
        table.ask_players("pre-flop")
    
        table.flop()
        table.ask_players("flop")

        table.turn()
        table.ask_players("turn")

        table.river()
        table.ask_players("river")
    
        table.show_winner()
        table.reset_table()

if __name__ == "__main__":
    init_game()