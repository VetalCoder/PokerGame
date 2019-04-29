"""
    Server program. Here contains main logic to control users and game.
"""

import socket
import json
from table import TableNet, OnePlayerException
from player import PlayerNet


# function, that read basic settings for game
def setup_server():
    print("   HELLO!!!   Welcome to PokerGame Server!")

    while True:
        try:
            number_of_players = int(input("Enter player numbers for begin (must be in a diapazone from 2 to 9): "))
            blind = int(input("Enter small blind on this server: "))
        except ValueError:
            print("Error! Try again...")
            continue
        else:
            if number_of_players < 2:
                return 2, blind
            elif number_of_players > 9:
                return 9, blind
            else:
                return number_of_players, blind


# game lobby. Here we wait for connections... Returns list of connected players
def start(count_players, blind):
    s = socket.socket()         # Создание object socket
    host = socket.gethostbyname(socket.gethostname()) # Получить имя компьютера 
    port = 27030                # Зарезервируйте порт для обслуживания
    s.bind((host, port))        # Привязка к порту
    s.listen()                 # Теперь дождитесь подключения клиента.

    print()
    print(f'Server started at: {host}. Could connect {count_players} peoples.')
    list_connected_players = []
    
    while True:
        sock, addr = s.accept()     # Установить соединение с клиентом.

        data = json.loads(sock.recv(1024).decode())
        print(f"Player {addr} was connected...")
        list_connected_players.append(PlayerNet(data['name'], int(data['stack']), addr, sock))

        message = f"In lobby waiting {len(list_connected_players)} peoples:\n"
        for index, player in enumerate(list_connected_players, 1):
            message += f"{index}. Player {player.name} with stack {player.stack}. Address: {player.address}\n"

        resp = {
            'clear' : True,
            'ask_ch' : False,
            'ask' : False,
            'message' : message,
            }

        for player in list_connected_players:
            player.socket.send(json.dumps(resp).encode())
           
        if len(list_connected_players) == count_players:
            return list_connected_players, blind


# main function, where create table and do playing....
def game(player_lst, blind):
    table = TableNet(blind, *player_lst)
    
    while True:
        try:
            table.pre_flop()
        except OnePlayerException as exception:
            table.send_data_to_player(exception.player, \
                f"You win this match with stack {exception.player.stack}. Congratulations!", clear=True)
            break

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
    game(*start(*setup_server()))