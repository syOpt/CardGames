import os, sys, msvcrt, ctypes, time
import Macro, Card

COLOMN = 8
CELL = 4
INITIAL_NUM = (7, 7, 7, 7, 6, 6, 6, 6)
assert(len(INITIAL_NUM) == COLOMN)

def getCh():
    a = ord(msvcrt.getch())         # get first byte of keyscan code  
    if a == 0 or a == 224:          # is it a function key?
        b = ord(msvcrt.getch())     # get next byte of key scan code
        x = a + (b * 256)             # cook it.
        return x                    # return cooked scancode
    else:
        return a                    # else return ascii code

def setCmdTextColor(color):
        stdOutHandle = ctypes.windll.kernel32.GetStdHandle(Macro.STD_OUTPUT_HANDLE)
        res = ctypes.windll.kernel32.SetConsoleTextAttribute(stdOutHandle, color)
        return res

class FreeCellCard(Card.Card):
    def __init__(self, rk ,st):
        Card.Card.__init__(self, rk, st)


class FreeCellDeck(Card.Deck):
    def __init__(self):
        Card.Deck.__init__(self)
        self.table = list()
        self.initTable()
        self.finished = [0, 0, 0, 0]
        self.cells = [None, None, None, None]
        self.sX = None
        self.sY = None
        self.sZ = None
        self.toMoveX = None
        self.toMoveY = None
        self.toMoveZ = None
        assert(len(self.cells) == CELL)

    def initTable(self):
        for x in range(4):
            for y in range(1, 14):
                self.pile.append(FreeCellCard(y, Card.Suit(x)))
        self.shuffle()
        p = 0
        for i in range(len(INITIAL_NUM)):
            col = self.pile[p : p + INITIAL_NUM[i]]
            self.table.append(col)
            p += INITIAL_NUM[i]


class FrameManager():
    def __init__(self):
        self.deck = FreeCellDeck()
        self.promote = ''

    def __del__(self):
        os.system('echo on')

    def mainLoop(self):
        os.system('echo off')
        self.promote = 'ready'
        self.show('cmd')
        exits = False
        while not exits:
            ch = getCh()
            if self.checkExit(ch):
                exits = True
            
    def checkExit(self, ch):
        exitKeys = (Macro.KEYCODE_E, Macro.KEYCODE_Q, Macro.KEYCODE_CAPITAL_E, Macro.KEYCODE_CAPITAL_Q)
        if ch in exitKeys:
            return True
        else:
            return False

    def show(self, dest):
        if dest == 'cmd':
            self.cmdShowDeck()
            self.cmdShowPromote()
        else:
            pass

    def cmdShowCard(self, cd, color = None):
        chars = cd.__str__()
        if color == None:
            color = cd.color
        setCmdTextColor(color)
        sys.stdout.write(chars)
        sys.stdout.flush()
        setCmdTextColor(Macro.FOREGROUND_DARKWHITE)
        return self

    def cmdShowDeck(self):
        os.system('cls')
        i = 0
        finish = False
        while not finish:
            finish = True
            for j in range(COLOMN):
                if len(self.deck.table[j]) > i:
                    finish = False
                    self.cmdShowCard(self.deck.table[j][i])
                    sys.stdout.write('\t')
            i += 1
            sys.stdout.write('\n')   

    def cmdShowPromote(self):
        setCmdTextColor(Macro.FOREGROUND_DARKWHITE)
        sys.stdout.write('\n' + self.promote)
        setCmdTextColor(Macro.FOREGROUND_DARKWHITE)

if __name__ == '__main__':
    game = FrameManager()
    game.mainLoop()
    