"""
    Module, that defines player objects
"""

from collections import Counter
import table as tb
from card import Card, SUITS

# function, which checks flush
def _check_flush(cards):
    spades = clubs = diamonds = hearts = 0

    for card in cards:
        if card.suit == SUITS[0]:
            spades += 1
        elif card.suit == SUITS[1]:
            hearts += 1
        elif card.suit == SUITS[2]:
            clubs += 1
        else:
            diamonds += 1

    if spades >= 5:
        return [x for x in cards if x.suit == SUITS[0]]
    elif hearts >= 5:
        return [x for x in cards if x.suit == SUITS[1]]
    elif clubs >= 5:
        return [x for x in cards if x.suit == SUITS[2]]
    elif diamonds >= 5:
        return [x for x in cards if x.suit == SUITS[3]]
    else:
        return False


# function, that checks straight
def _check_straight(cards):
    # add ace == 1, if ace in cards
    # returns High cards of straight or False
    
    cards_copy = cards.copy()

    for card in cards:
        if card.value == 14:
            cards_copy.insert(0, Card(card.suit, 1))

    straight = []

    for index in range(len(cards_copy) - 4):  # 4 -- 5 cards for one iteration
        current_value = cards_copy[index].value
        if cards_copy[index + 1].value == current_value + 1 and \
            cards_copy[index + 2].value == current_value + 2 and \
            cards_copy[index + 3].value == current_value + 3 and \
            cards_copy[index + 4].value == current_value + 4:
                straight.append(cards_copy[index + 4])         # biggest card

    if not straight:
        return False
    else:
        return straight
    

# function, that return dict with repetitions
def _check_repetitions(cards):
    #replace Ace == 1 with Ace == 14 for sorting....
    for card in cards:
        if card.value == 1:
            card.value == 14

    counter = Counter([card.value for card in cards])

    # key - count repetitions card
    # value -- cards
    result = {
        4 : [],
        3 : [],
        2 : [],
        1 : [],
        }

    for card, count in counter.items():
        result[count].append(card)

    # do transformations...
    # we don't need 2 "Three of a Kind" or 3 "Two pairs"....
    if result.get(4):           # 4 - 1, 3 - 0, 2 - 0
        result[1] += result[2] + result[3]
        result[2].clear()
        result[3].clear()
    elif result.get(3):         # 4 - 0, 3 - 1, 2 - 1(0)
        if len(result[3]) > 1:
            result[3].sort(reverse=True)
            result[1].append(result[3].pop())
        if len(result[2]) > 1:
            result[2].sort(reverse=True)
            result[1].append(result[2].pop())
    elif result.get(2):         # 4 - 0, 3 - 0, 2 - 2, 1, 0
        if len(result[2]) > 2:
            result[2].sort(reverse=True)
            result[1].append(result[2].pop())

    # sorting... bigger -- first
    for value in result.values():
        value.sort(reverse=True)

    return result

       
class IncorrectInputException(Exception):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    
class Combination:
    COMBINATIONS = {
        1 : "High Card",
        2 : "Pair",
        3 : "Two pairs",
        4 : "Three of a kind",
        5 : "Straight",
        6 : "Flush",
        7 : "Full house",
        8 : "Four of a kind",
        9 : "Straight flush",
        10 : "Royal flush",
        }

    def __init__(self, comb, card, kicker=None, chain=None):
        self.__combination = comb       # int
        self.__card = card              # Card (or list of Cards)
        self.__kicker = kicker
        self.__chain = chain

    # string representation
    def __str__(self):
        kick = f' and kicker "{self.__kicker.short_name}"' if self.__kicker else ''
        
        chain = ""
        if self.__chain:
            for item in self.__chain:
                chain += f'"{item.short_name}" '
            chain = f" and kickers {chain}"
        

        if type(self.__card) == list:
            cards = [f'"{card.short_name}"' for card in self.__card]
            cards = " and ".join(cards)
        else:
            cards = f'"{self.__card.short_name}"'

        return f"{self.COMBINATIONS[self.__combination]} with {cards}{kick}{chain}"

    # compare methods
    def __eq__(self, value):
        return self.__combination == value.__combination and \
                self.__card == value.__card and \
                self.__kicker == value.__kicker and \
                self.__chain == value.__chain

    def __gt__(self, value):
        if self.__combination > value.__combination:
            return True
        elif self.__combination == value.__combination:
            if self.__card > value.__card:
                return True
            elif self.__card < value.__card:
                return False

            if self.__kicker and value.__kicker:
                if self.__kicker > value.__kicker:
                    return True
                else:
                    return False

            if self.__chain and value.__chain:
                if self.__chain > value.__chain:
                    return True
                else:
                    return False

            return False
        else:
            return False


    def __ge__(self, value):
        if self.__combination > value.__combination:
            return True
        elif self.__combination == value.__combination:
            if self.__card > value.__card:
                return True
            elif self.__card < value.__card:
                return False

            if self.__kicker and value.__kicker:
                if self.__kicker >= value.__kicker:
                    return True
                else:
                    return False

            if self.__chain and value.__chain:
                if self.__chain >= value.__chain:
                    return True
                else:
                    return False

            return True
        else:
            return False



    # function, which find player with max combination. Returns list of
    # players with maximal combination
    @staticmethod
    def find_max(players):
        max_combo_player = max(players, key=lambda x: x.combination)

        result = [max_combo_player]

        for player in players:
            if player.combination == max_combo_player.combination and player != max_combo_player:
                result.append(player)

        return result



class Player:
    """
        Class defines players. Has attributes:
        - stack
        - cards
        - name

        Has methods:
        - do_check
        - do_pass
        - do_raise

        Has subclasses:
        - Answer -- subclass, that represents player answer
            
    """
    class _Answer:
        def __init__(self):
            self.__pass = False
            self.__check = False
            self.__raise = False   
            self.__asked = False   # value for controls. True if player has been asked minimum once

        @property
        def passed(self):
            return self.__pass

        @passed.setter
        def passed(self, value):
            if type(value) == bool:
                self.__pass = value

        @property
        def checked(self):
            return self.__check

        @checked.setter
        def checked(self, value):
            if type(value) == bool:
                self.__check = value

        @property
        def raised(self):
            return self.__raise

        @raised.setter
        def raised(self, value):
            if type(value) == bool:
                self.__raise = value

        @property
        def asked(self):
            return self.__asked

        @asked.setter
        def asked(self, value):
            if type(value) == bool:
                self.__asked = value

        def __eq__(self, value):
            return self.__pass == value.__pass and \
                self.__check == value.__check and \
                self.__raise == value.__raise and \
                self.__asked == value.__asked 

        def __str__(self):
            if self.__pass:
                return "passed"
            if self.__check:
                return "checked"
            if self.__raise:
                return "raised"
            if not self.__asked:
                return "not asked"

        # if passed -- do not touch later
        def reset(self):
            self.__check = False
            self.__raise = False   # can be integer, means value betting
            self.__asked = False   # value for controls. True if player has been asked minimum once


    def __init__(self, name, stack):
        self.__name = name
        self.__stack = stack
        self.__cards = []
        self.answer = self._Answer()
        self.combination = None
        self.__bet = 0

    # string represents
    def __repr__(self):
        return f"Player({self.__name, self.__stack})"

    def __str__(self):
        return f"Player {self.__name}"

    # properties
    @property
    def bet(self):
        return self.__bet

    @bet.setter
    def bet(self, value):
        self.__bet = value

    @property
    def stack(self):
        return self.__stack

    @stack.setter
    def stack(self, value):
        self.__stack = value


    @property
    def cards(self):
        return self.__cards

    @cards.setter
    def cards(self, value):
        if len(value) == 2:
            self.__cards = value
        else:
            raise ValueError("Too much cards for one player")

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if value:
            self.__name = value

    def __eq__(self, value):
        return self.__name == value.__name and \
            self.__stack == value.__stack and \
            self.__cards == value.__cards and \
            self.answer == value.answer and \
            self.combination == value.combination



    def do_check(self, table):
        self.answer.checked = True
        self.answer.asked = True
        #table.answers[self] = self.answer
        
        # check call (and do call)
        stack_list = [bank[0] for bank in table.bank.values()]

        if max(stack_list) != table.bank[table.players.index(self)][0]:
            difference = max(stack_list) - table.bank[table.players.index(self)][0]
            
            if difference > self.stack:
                table.bank[table.players.index(self)][0] += self.stack            
                self.answer.raised = True
                self.answer.asked = True
                self.bet += self.stack
                self.stack = 0
                table.bank[table.players.index(self)][1] = True
            else:
                table.bank[table.players.index(self)][0] += difference
                self.answer.raised = True
                self.answer.asked = True
                self.bet += difference
                self.stack -= difference



    def do_pass(self, table):
        self.answer.passed = True
        self.answer.asked = True
        #table.bank[table.players.index(self)][0] = self.answer


    def do_raise(self, table, value=0, all_in=False):
        if all_in:
            table.bank[table.players.index(self)][0] += self.stack            
            self.answer.raised = True
            self.answer.asked = True
            self.bet += self.stack
            self.stack = 0
            table.bank[table.players.index(self)][1] = True
        elif 0 < value <= self.stack:
            table.bank[table.players.index(self)][0] += value
            self.answer.raised = True
            self.answer.asked = True
            self.bet += value
            self.stack -= value
            
            # player go all-in
            if self.stack == 0:
                table.bank[table.players.index(self)][1] = True
        else:
            raise IncorrectInputException("This value are incorrect for betting....")

    def ask(self, table):
        print("Your move!\nYou can press 'p' for pass, 'c' for check (call), 'b' for bet or 'a' for all-in: ")
        
        answer = tb.get_char()


        # check answer
        #try:
        #    self.do_raise(table, int(answer))
        #except ValueError:
        if answer == b"p":
            self.do_pass(table)
        elif answer == b"c":
            self.do_check(table)
        elif answer == b"a":
            self.do_raise(table, all_in=True)
        elif answer == b'b':
            bet_value = input("Enter value for bet: ")
            try:
                self.do_raise(table, int(bet_value))
            except ValueError:
                raise IncorrectInputException("Incorrect value for bet...")
        else:
            raise IncorrectInputException("Incorrect input value...")


    # function, thats find the best combination and write this to Player.combination attribute
    # cards -- 7 cards, sum table cards (5) + player cards (2)
    

    def find_combination(self, cards):
        # sorting cards.... 
        cards.sort(key=lambda x: x.value)

        flush = _check_flush(cards)

        if flush:
            straight = _check_straight(flush) # may be straight flush
        else:
            straight = _check_straight(cards) # if straight flush isn't be

        if flush and straight:    
            # straight flush or royal flush
            # max card in straight...
            max_card = straight[0]

            for card in straight:
                if card > max_card:
                    max_card = card
                    
            if max_card.value == 14:        # royal flush                    
                self.combination = Combination(10, max_card)
                return
            else:                           # straight flush
                self.combination = Combination(9, max_card)
                return
        
        # if we have any of this combinations, "4 of a Kind" or "Full House" are impossible.
        # so this combinations in this case are maximal    
        elif flush:
            self.combination = Combination(6, flush[-1], chain=list(reversed(flush)))
            return
        elif straight:
            max_card = straight[0]

            for card in straight:
                if card > max_card:
                    max_card = card

            self.combination = Combination(5, max_card)
            return

        repetitions = _check_repetitions(cards)

        if repetitions.get(4):               # "4 of a Kind" found (may be only one)
            self.combination = Combination(8, Card('default', repetitions.get(4)[0]), kicker=Card('default', repetitions.get(1)[0]))
            return
        elif repetitions.get(3):             # "3 of a Kind" or "Full House"
            if repetitions.get(2):              # "Full House"
                self.combination = Combination(7, [Card('default', repetitions.get(3)[0]), Card('default', repetitions.get(2)[0])] )
                return
            else:                               # "3 of a Kind"
                self.combination = Combination(4, Card('default', repetitions.get(3)[0]), chain=[Card('default', repetitions.get(1)[0]),
                                                                                               Card('default', repetitions.get(1)[1])])
                return
        elif repetitions.get(2):             # "Pair" or "Two Pairs"
            if len(repetitions[2]) == 2:        # "Two Pairs"
                self.combination = Combination(3, [Card('default', repetitions.get(2)[0]), Card('default', repetitions.get(2)[1])], 
                                               kicker=Card('default', repetitions.get(1)[0]))
                return
            else:                               # "Pair"
                self.combination = Combination(2, Card('default', repetitions.get(2)[0]), 
                                               chain=[Card('default', repetitions.get(1)[index]) for index in range(3)] )
                return
        else:                                # "High Card"
            self.combination = Combination(1, Card('default', repetitions.get(1)[0]), 
                                               chain=[Card('default', repetitions.get(1)[index]) for index in range(1, 5)] )
            return


