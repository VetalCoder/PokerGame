"""
    Module, that defines table object
"""
from deck import Deck
from player import IncorrectInputException, Combination

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
       - current bank
    """

    def __init__(self, smallblind, *players):
        self.players = list(players)        
        self.table_cards = []        
        self.deck = Deck()
        self.current_smallblind_player = 0 # index player
        self.smallblind = smallblind

        # 1-answer, 2-player stack, 3-all-in?
        self.bank = {index : [0, False] for index in range(len(self.players))}             
        

        #self.answers = [player.answer for player in self.players]  # some fucks...   {player : player.answer for player in self.players}

    ## True if player must be asked, False - if not.
    #def check_answer(self, player):
    #    if player.answer.passed:
    #        return False
        
    #    if not player.answer.asked:
    #        return True

    #    raising_values = [value.raised for value in self.answers.values()]

    #    # if all elements are equal -- len(set(...)) == 1
    #    if len(set(raising_values)) == 1:
    #        return False
        
    #    if max(raising_values) == player.answer.raised:
    #        return False
    #    else:
    #        return True

    ## true -- if all players get answer
    #def check_all_answers(self):
    #    for player in self.answers:
    #        if self.check_answer(player):
    #            return False
    #    return True

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
        #if len([player for player in self.players if player.answer.passed != True and self.bank[self.players.index(player)][1] != True]) <= 1:
        #    return

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


    #def ask_players(self, round):
    #    while not self.check_all_answers():
    #        for player in self.players:
    #            if not self.check_answer(player):
    #                continue
                
    #            clear_scr()

    #            #print info
    #            print(f"           {round.upper()}")
    #            print("  Table cards:  ")
    #            for card in self.table_cards:
    #                print(f"        {card.short_name}", end="")
    #            print()
    #            print(f"  Table bank:    {self.bank}")
    #            print()
    #            print("  Players answers:  ")
    #            for ans in self.players:
    #                print(f"    {ans.name} -- {ans.answer}")
    #            print()
            
    #            ready = False
    #            while not ready:
    #                print(f"{player.name}, press 'Enter' to continue....")
    #                ready = True if get_char() == b"\r" else False

    #            print("  Your cards:  ")
    #            for card in player.cards:
    #                print(f"        {card.short_name}", end="")
    #            print()
    #            print(f"  Your stack:    {player.stack}")
    #            correct_answer = False
    #            while not correct_answer:
    #                try:
    #                    player.ask(self)
    #                except IncorrectInputException as error:
    #                    print(error)
    #                    print("Try again!")
    #                else:
    #                    correct_answer = True
    #    else:
    #        for player in self.players:
    #            player.answer.reset()
    #        self.answers = {player : player.answer for player in self.players}


    # check winner
    #def __check_winner(self):      
    #    for player in self.players:
    #        player.find_combination(self.table_cards + player.cards)

    #    return Combination.find_max(self)

    #def __pay_winners(self, winners):
    #    # TODO: self.bank must be added to winner.stack
    #    pass
        
    def show_winner(self):
        # find winners and pay them

        winners_list = []

        bank_sum = 0
        for bank in self.bank.values():
            bank_sum += bank[0]

        #players_alive = {index : player for index, player in enumerate(self.players) if player.answer.passed != True}
        players_alive = [player for player in self.players if player.answer.passed != True]
        # find maximum value betting
        # max_bet = self.bank[max(players_alive, key=lambda x: self.bank[x][0])][0]

        
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
