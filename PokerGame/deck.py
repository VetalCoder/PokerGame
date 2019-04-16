"""
    Module, that defines class deck for working with deck of cards.
    Needs card module. 
"""

import card
import random
from itertools import product

class Deck:
    """
       Class, that contains methods for correct working with deck of cards.
       
    """

    # Constructor
    def __init__(self):
        self.__deck = [card.Card(suit, value) for suit, value in product(card.SUITS, card.VALUES_STR) if value != 1]
        random.shuffle(self.__deck)
                

    # String representation
    def __repr__(self):
        return "Deck object"

    def __str__(self):
        return self.__deck

    def print_deck(self):
        for item in self:
            print(item)


    # Iterable interface
    def __getitem__(self, value):
        return self.__deck[value]

    def __len__(self):
        return len(self.__deck)

    # return next card from deck
    def pop(self):
        return self.__deck.pop()

