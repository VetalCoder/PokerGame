""" 
    Module, that defines class Card and some constants for correct working with it
"""

SUITS = ("spades", "hearts", "clubs", "diamonds")
VALUES_STR = {
        1 : "Ace",
        2 : "2",
        3 : "3",
        4 : "4",
        5 : "5",
        6 : "6",
        7 : "7",
        8 : "8",
        9 : "9",
        10 : "10",
        11 : "Jack",
        12 : "Queen",
        13 : "King",
        14 : "Ace",
    }

SHORT_SUIT_NAME = {
    "spades" : "♠",
    "hearts" : "♥",
    "clubs" : "♣",
    "diamonds" : "♦",
    "default" : ""
    }

SHORT_VALUE_NAME = {
    1 : "A",
    2 : "2",
    3 : "3",
    4 : "4",
    5 : "5",
    6 : "6",
    7 : "7",
    8 : "8",
    9 : "9",
    10 : "10",
    11 : "J",
    12 : "Q",
    13 : "K",
    14 : "A", # for checking straight
}

class Card:
    """ 
        Class that defines a card object
        * suit -- card suit ['spades', 'hearts', 'clubs', 'diamonds'] -- str
        * value -- card value (int):
            1 - Ace
            2 - 2
            3 - 3
            4 - 4
            5 - 5
            6 - 6
            7 - 7
            8 - 8
            9 - 9
            10 - 10
            11 - Jack
            12 - Queen
            13 - King

    """

    # Constructor
    def __init__(self, suit, value):
        if suit in SUITS or suit == 'default':
            self.__suit = suit
        else:
            raise ValueError("Suit is incorrect")
        
        if value in VALUES_STR:
            self.__value = value
        else:
            raise ValueError("Value of card is incorrect")

    # suit property
    @property
    def suit(self):
        return self.__suit

    @suit.setter
    def suit(self, value):
        if value in SUITS:
            self.__suit = value
        else:
            raise ValueError("Suit is incorrect")


    # value property
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value in VALUES_STR:
            self.__value = value
        else:
            raise ValueError("Value of card is incorrect")


    # string represents

    def __repr__(self):
        return f"Card({self.__suit}, {self.__value})"

    def __str__(self):
        return f"{VALUES_STR[self.__value]} of {self.__suit}"

    @property
    def short_name(self):
        return f"{SHORT_VALUE_NAME[self.__value]}{SHORT_SUIT_NAME[self.__suit]}"


    # compare methods

    def __eq__(self, other):
        return self.__suit == other.__suit and self.__value == other.__value

    def __gt__(self, other):
        return self.__value > other.__value

    def __ge__(self, other):
        return self.__value >= other.__value

    def __lt__(self, other):
        return self.__value < other.__value

    def __le__(self, other):
        return self.__value <= other.__value