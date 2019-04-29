"""
    Module, that defines table object
"""
from deck import Deck
from player import IncorrectInputException, Combination
import json
from time import sleep

# Exception, which raised if one player are sitting on the table
class OnePlayerException(Exception):
    def __init__(self, player, message=""):
        super().__init__(message)
        self.player = player

# function, that can return only one char from keyboard 
def get_char():
    # figure out which function to use once, and store it in _func
    if "_func" not in get_char.__dict__:
        try:
            # for Windows-based systems
            import msvcrt # If successful, we are on Windows
            get_char._func=msvcrt.getch

        except ImportError:
            # for POSIX-based systems (with termios & tty support)
            import tty, sys, termios # raises ImportError if unsupported

            def _ttyRead():
                fd = sys.stdin.fileno()
                oldSettings = termios.tcgetattr(fd)

                try:
                    tty.setcbreak(fd)
                    answer = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)

                return answer

            get_char._func=_ttyRead

    return get_char._func()

# function, that clear terminal
def clear_scr():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

class Table:
    """
       Class, that initiate working with table.
       Has attributes:
       - [] : current players
       - [] : table cards
       - {} : current bank
       - deck
       - small blind
       - index player with small blind
    """

    def __init__(self, smallblind, *players):
        self.players = list(players)        
        self.table_cards = []        
        self.deck = Deck()
        self.current_smallblind_player = 0 # index player
        self.smallblind = smallblind

        # index player : 1-bet_value, 2-all-in
        self.bank = {index : [0, False] for index in range(len(self.players))}             
    
     
    def pre_flop(self):
        # check len players
        if len(self.players) == 1:
            raise OnePlayerException(player=self.players[0])

        # players cards
        for player in self.players:
            player.cards = [self.deck.pop(), self.deck.pop()]

        # blinds
        if self.current_smallblind_player >= len(self.players):
            self.current_smallblind_player = 0
        self.players[self.current_smallblind_player].do_raise(self, self.smallblind, sb=True)

        if self.current_smallblind_player + 1 == len(self.players):
            self.current_smallblind_player = 0
        else:
            self.current_smallblind_player += 1
        
        self.players[self.current_smallblind_player].do_raise(self, self.smallblind * 2, bb=True)


    def flop(self):
        # table cards
        for _ in range(3):
            self.table_cards.append(self.deck.pop()) 

    def turn(self):
        # table cards
        self.table_cards.append(self.deck.pop())

    def river(self):
        # table cards
        self.table_cards.append(self.deck.pop())


    def print_info(self, round):
        clear_scr()

        print(f"           {round.upper()}")
        print("  Table cards:  ")
        for card in self.table_cards:
            print(f"        {card.short_name}", end="")
        print()
        
        bank_sum = 0
        # find bank value
        for bank in self.bank.values():
            bank_sum += bank[0]
        print(f"  Table bank:    {bank_sum}")
        print()

        print("  Players answers:  ")
        for player in self.players:
            print(f"    {player.name} (bet:{player.bet})\t-- {player.answer}")
        print()


    def ask_players(self, round):
        # first cycle (ask all players)
        # return if one player must be asked
        if len([player for player in self.players if player.answer.passed != True and self.bank[self.players.index(player)][1] != True]) <= 1:
                return

        for player in self.players:
            if player.answer.passed or self.bank[self.players.index(player)][1]:
                continue

            self.print_info(round)
            
            ready = False
            while not ready:
                print(f"{player.name}, press 'Enter' to continue....")
                ready = True if get_char() == b"\r" else False

            # output private information
            print("  Your cards:  ")
            for card in player.cards:
                print(f"        {card.short_name}", end="")
            print()
            print(f"  Your stack:    {player.stack}")
            
            correct_answer = False
            while not correct_answer:
                try:
                    player.ask(self)
                except IncorrectInputException as error:
                    print(error)
                    print("Try again!")
                else:
                    correct_answer = True
        
        # second cycle (ask players to call if len(set(bank_sum)) != 1) 
        stack_list = [bank[0] for index, bank in self.bank.items() if self.players[index].answer.passed != True]
        
        players_list = [player for player in self.players if player.answer.passed != True and \
            self.bank[self.players.index(player)][1] != True and \
            player.bet != max(stack_list)]

        while len(players_list) > 0:

            for player in self.players:
                # skip asking players with max bet, or passed, or who go all-in
                if player.answer.passed or \
                    self.bank[self.players.index(player)][0] == max(stack_list) or \
                    self.bank[self.players.index(player)][1]:
                    continue

                self.print_info(round)
            
                ready = False
                while not ready:
                    print(f"{player.name}, press 'Enter' to continue....")
                    ready = True if get_char() == b"\r" else False

                # output private information
                print("  Your cards:  ")
                for card in player.cards:
                    print(f"        {card.short_name}", end="")
                print()
                print(f"  Your stack:    {player.stack}")
                correct_answer = False
                while not correct_answer:
                    try:
                        player.ask(self)
                    except IncorrectInputException as error:
                        print(error)
                        print("Try again!")
                    else:
                        correct_answer = True

            #stack_list = [bank[0] for index, bank in self.bank.items() if bank[1] == False and self.players[index].answer.passed != True]
            stack_list = [bank[0] for index, bank in self.bank.items() if self.players[index].answer.passed != True]
        
            players_list = [player for player in self.players if player.answer.passed != True and \
                self.bank[self.players.index(player)][1] != True and \
                player.bet != max(stack_list)]

        # reset answers for next row
        for player in self.players:
            player.answer.reset()

        
    def show_winner(self):
        # find winners and pay them

        winners_list = []

        bank_sum = 0
        for bank in self.bank.values():
            bank_sum += bank[0]

        players_alive = [player for player in self.players if player.answer.passed != True]
      
        # calculate combinations
        for player in players_alive:
            player.find_combination(self.table_cards + player.cards)

        # pay players
        while bank_sum > 0:
            winners = Combination.find_max(players_alive)
            
            # deleting and sorting winners
            for index in range(len(winners)):
                if winners[index].bet == 0:
                    del winners[index]

            winners.sort(key=lambda x: x.bet)

            while winners:
                #form subbank and delete from bank and player.bet
                win_bet = winners[0].bet
                subbank = 0
                for player in self.players:
                    player_bet = player.bet
                    if player_bet > win_bet:
                        player.bet -= win_bet
                        self.bank[self.players.index(player)][0] -= win_bet
                        subbank += win_bet
                    else:
                        player.bet = 0
                        self.bank[self.players.index(player)][0] = 0
                        subbank += player_bet

                # paid
                for winner in winners:
                    winner.stack += subbank // len(winners)

                winners_list.append(winners[0])
                del players_alive[players_alive.index(winners[0])]
                del winners[0]
                
                
            # re-calculate bank-sum
            bank_sum = 0
            for bank in self.bank.values():
                bank_sum += bank[0]

        # print info...
        clear_scr()

        print("  Table cards:  ")
        for card in self.table_cards:
            print(f"        {card.short_name}", end="")
        print()
        
        bank_sum = 0
        # find bank value
        for bank in self.bank.values():
            bank_sum += bank[0]
        print(f"  Table bank:    {bank_sum}")
        print()

        for player in self.players:
            print(f"{player.name} cards:  {player.cards[0].short_name}  {player.cards[1].short_name}") 
            print(f"{player.name} have {player.stack} funds.")
            print(f"{player.name} answer is {player.answer}.")
            print()

        print()

        if len(winners_list) == 1:
            print(f'Player {winners_list[0].name} win with {winners_list[0].combination}')
        else:
            print("  Winners:  ")
            for index, winner in enumerate(winners_list, 1):
                print(f'{index}. Player {winner.name} win with {winner.combination}')

        # kick players with zero stack, if thoose 
        self.players = list(filter(lambda item: item.stack > 0, self.players))

        input("Press enter to continue.....")


    def reset_table(self):
        self.table_cards = []
        self.deck = Deck()
        self.bank = {index : [0, False] for index in range(len(self.players))} 

        for player in self.players:
            player.answer.reset()
            player.answer.passed = False
            player.combination = None


class TableNet(Table):
    """
        Class, that provides working with table. Inherits class Table. 
        Contains some override functions and functions, which can communicate with players
    """

    @staticmethod
    def send_data_to_player(player, message, ask_ch=False, ask=False, clear=False):
        data = {
            'clear' : clear,
            'ask_ch' : ask_ch,
            'ask' : ask,
            'message' : message,
            }
        player.socket.send(json.dumps(data).encode())
        sleep(0.05) # fucking shit, but works

    @staticmethod
    def receive_data(player):
        return player.socket.recv(1024).decode('utf-8')

    def ask_players(self, round):
        # first cycle (ask all players)
        # return if one player must be asked
        if len([player for player in self.players if player.answer.passed != True and self.bank[self.players.index(player)][1] != True]) <= 1:
                return

        for player in self.players:
            if player.answer.passed or self.bank[self.players.index(player)][1]:
                continue

            self.print_info(round)
                        
            correct_answer = False
            while not correct_answer:
                try:
                    player.ask(self)
                except IncorrectInputException as error:
                    print(error)
                    print("Try again!")
                else:
                    correct_answer = True
        
        # second cycle (ask players to call if len(set(bank_sum)) != 1) 
        stack_list = [bank[0] for index, bank in self.bank.items() if self.players[index].answer.passed != True]
        
        players_list = [player for player in self.players if player.answer.passed != True and \
            self.bank[self.players.index(player)][1] != True and \
            player.bet != max(stack_list)]

        while len(players_list) > 0:

            for player in self.players:
                # skip asking players with max bet, or passed, or who go all-in
                if player.answer.passed or \
                    self.bank[self.players.index(player)][0] == max(stack_list) or \
                    self.bank[self.players.index(player)][1]:
                    continue

                self.print_info(round)
            
                correct_answer = False
                while not correct_answer:
                    try:
                        player.ask(self)
                    except IncorrectInputException as error:
                        print(error)
                        print("Try again!")
                    else:
                        correct_answer = True

            stack_list = [bank[0] for index, bank in self.bank.items() if self.players[index].answer.passed != True]
        
            players_list = [player for player in self.players if player.answer.passed != True and \
                self.bank[self.players.index(player)][1] != True and \
                player.bet != max(stack_list)]

        # reset answers for next row
        for player in self.players:
            player.answer.reset()


    def print_info(self, round):
        message = ""

        message += f"           {round.upper()}\n"
        message += "  Table cards:  \n"
        for card in self.table_cards:
            message += f"        {card.short_name}"
        message += "\n"
        
        bank_sum = 0
        # find bank value
        for bank in self.bank.values():
            bank_sum += bank[0]
        message += f"  Table bank:    {bank_sum}\n"
        message += "\n"

        message += "  Players answers:\n"
        for player in self.players:
           message += f"    {player.name} (bet:{player.bet})\t-- {player.answer}\n"
        message += "\n"

        # send data to players with private info
        for player in self.players:
            message_p = "  Your cards:  \n"
            for card in player.cards:
                message_p += f"        {card.short_name}"
            message_p += "\n"
            message_p += f"  Your stack:    {player.stack}\n"

            self.send_data_to_player(player, message + message_p, clear=True)
            

    def show_winner(self):
        # find winners and pay them

        winners_list = []

        bank_sum = 0
        for bank in self.bank.values():
            bank_sum += bank[0]

        players_alive = [player for player in self.players if player.answer.passed != True]
      
        # calculate combinations
        for player in players_alive:
            player.find_combination(self.table_cards + player.cards)

        # pay players
        while bank_sum > 0:
            winners = Combination.find_max(players_alive)
            
            # deleting and sorting winners
            for index in range(len(winners)):
                if winners[index].bet == 0:
                    del winners[index]

            winners.sort(key=lambda x: x.bet)

            while winners:
                #form subbank and delete from bank and player.bet
                win_bet = winners[0].bet
                subbank = 0
                for player in self.players:
                    player_bet = player.bet
                    if player_bet > win_bet:
                        player.bet -= win_bet
                        self.bank[self.players.index(player)][0] -= win_bet
                        subbank += win_bet
                    else:
                        player.bet = 0
                        self.bank[self.players.index(player)][0] = 0
                        subbank += player_bet

                # paid
                for winner in winners:
                    winner.stack += subbank // len(winners)

                winners_list.append(winners[0])
                del players_alive[players_alive.index(winners[0])]
                del winners[0]
                
                
            # re-calculate bank-sum
            bank_sum = 0
            for bank in self.bank.values():
                bank_sum += bank[0]

        # print info...
        
        message = "  Table cards:  \n"
        for card in self.table_cards:
            message += f"        {card.short_name}"
        message += "\n"
        
        bank_sum = 0
        # find bank value
        for bank in self.bank.values():
            bank_sum += bank[0]
        message += f"  Table bank:    {bank_sum}\n"
        message += "\n"

        for player in self.players:
            message += f"{player.name} cards:  {player.cards[0].short_name}  {player.cards[1].short_name}\n" 
            message += f"{player.name} have {player.stack} funds.\n\n"


        if len(winners_list) == 1:
            message += f'Player {winners_list[0].name} win with {winners_list[0].combination}\n'
        else:
            message += "  Winners:  \n"
            for index, winner in enumerate(winners_list, 1):
                message += f'{index}. Player {winner.name} win with {winner.combination}\n'

        # inform loosers...
        for player in self.players:
            if player.stack <= 0:
                self.send_data_to_player(player, "You lose! \n     :(", clear=True)
        # kick players with zero stack, if thoose 
        self.players = list(filter(lambda item: item.stack > 0, self.players))

        message += "Next row will be start after 10 seconds...."

        # send message
        for player in self.players:
            self.send_data_to_player(player, message, clear=True)

        sleep(10)
