from enum import Enum, unique
import colorama
import Macro

@unique
class Suit(Enum):
    heart = 0
    diamond = 1
    club = 2
    spade = 3
    none = 4

SuitDict = {Suit.heart:chr(Macro.ASCII_HEART), Suit.diamond:chr(Macro.ASCII_DIAMOND), Suit.club:chr(Macro.ASCII_CLUB), Suit.spade:chr(Macro.ASCII_SPADE), Suit.none:' '}
RankDict = {1:'A', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'10', 11:'J', 12:'Q', 13:'K', 14:'Joker-', 15:'Joker+'}

class Card:
    def __init__(self, rk, st = None):
        assert(type(rk) == type(0) and rk > 0 and rk < 16)
        assert(st == None or type(st) == type(Suit(0)))
        if rk > 13:
            assert(st == None or st == Suit.none)
        self.rank = rk
        self.suit = st
        self.color = colorama.Fore.WHITE
        #self.color = Macro.FOREGROUND_DARKWHITE
        if self.suit == Suit.heart or self.suit == Suit.diamond:
            self.color = colorama.Fore.RED
            #self.color = Macro.FOREGROUND_DARKRED

    def __str__(self):
        return SuitDict[self.suit] + RankDict[self.rank]

    def __cmp__(self, rhs):
        if self.rank < rhs.rank:
            if self.rank == 1 and rhs.rank <= 13:
                return 1
            else:
                return -1
        elif self.rank > rhs.rank:
            if rhs.rank == 1 and self.rank <= 13:
                return -1
            else:
                return 1
        else:
            return 0


class Deck:
    def __init__(self):
        self.pile = list()

    def __call__(self, pileCount = 1, jokers = False):
        for s in range(pileCount):
            for x in range(4):
                for y in range(1, 14):
                    self.pile.append(Card(y, Suit(x)))
            if jokers:
                self.pile.append(Card(14))
                self.pile.append(Card(15))

    def shuffle(self):
        import random
        n = len(self.pile)
        for i in range(n):
            j = random.randrange(i, n)
            self.pile[i], self.pile[j] = self.pile[j], self.pile[i]
        return self


if __name__ == '__main__':
    pass