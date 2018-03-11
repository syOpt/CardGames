import os, sys, msvcrt, ctypes, time
import Macro, Card

COLOMN = 8
CELL = 4
PILES = 4
INITIAL_NUM = (7, 7, 7, 7, 6, 6, 6, 6)
assert len(INITIAL_NUM) == COLOMN
assert CELL == 4
assert PILES == 4

def getCh():
    '''
    Return the keycode of the striked key.
    '''
    a = ord(msvcrt.getch())         # get the first byte of the keyscan code  
    if a == 0 or a == 224:          # check if it is a function key
        b = ord(msvcrt.getch())     # get the next byte of the key scan code
        x = a + (b * 256)           # cook it
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
        self.finished = [0, 0, 0, 0]
        self.cells = [None, None, None, None]
        self.sX = None
        self.sY = None
        self.sZ = None
        self.toMoveX = None
        self.__initTable()
        assert len(self.cells) == CELL
        assert len(self.finished) == PILES

    def __initTable(self):
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
    def __init__(self, mode = 'cmd'):
        self.__mode = mode
        self.__deck = FreeCellDeck()
        self.__promote = ''

    def __del__(self):
        os.system('echo on')

    def mainLoop(self):
        os.system('echo off')
        self.__promote = 'H: help\tM: menu\tE: exit'
        self.__show()
        exits = False
        while not exits:
            ch = getCh()
            if self.__checkExit(ch):
                # to exit
                exits = True
            elif ch == Macro.KEYCODE_LEFTARROW or ch == Macro.KEYCODE_RIGHTARROW:
                # move selection to the left or the right
                direc = 1
                self.__promote = "Pressed" + chr(Macro.ASCII_RIGHTARROW) + "."
                if ch == Macro.KEYCODE_LEFTARROW:
                    direc = -1
                    self.__promote = "Pressed" + chr(Macro.ASCII_LEFTARROW) + "."
                if self.__deck.toMoveX == None:
                    if self.__deck.sZ == None:
                        self.__deck.sZ = 0
                        if self.__deck.sX == None:
                            self.__deck.sX = int(COLOMN / 2)
                        if self.__deck.sY == None:
                            self.__deck.sY = len(self.__deck.table[self.__deck.sX]) - 1
                    elif self.__deck.sZ == 1:
                        if self.__deck.sX == None:
                            self.__deck.sX = 0
                        else:
                            self.__deck.sX += direc
                            self.__deck.sX %= CELL
                    else:
                        if self.__deck.sX == None:
                            self.__deck.sX = int(COLOMN / 2)
                        else:
                            self.__deck.sX += direc
                            self.__deck.sX %= COLOMN
                        self.__deck.sY = len(self.__deck.table[self.__deck.sX]) - 1
                else:
                    self.__deck.toMoveX += direc
                    self.__deck.toMoveX %= COLOMN
                self.__checksXYZ()
                self.__show()
            elif ch == Macro.KEYCODE_UPARROW or ch == Macro.KEYCODE_DOWNARROW:
                # move selection up or down
                direc = 1
                self.__promote = "Pressed" + chr(Macro.ASCII_DOWNARROW) + "."
                if ch == Macro.KEYCODE_UPARROW:
                    direc = -1
                    self.__promote = "Pressed" + chr(Macro.ASCII_UPARROW) + "."
                if self.__deck.toMoveX == None:
                    if self.__deck.sZ == None:
                        self.__deck.sZ = 0
                        if self.__deck.sX == None:
                            self.__deck.sX = int(COLOMN / 2)
                        if self.__deck.sY == None:
                            self.__deck.sY = len(self.__deck.table[self.__deck.sX]) - 1
                    elif self.__deck.sZ == 1:
                        if self.__deck.sX == None:
                            self.__deck.sX = 0
                        elif ch == Macro.KEYCODE_DOWNARROW:
                            self.__deck.sZ = 0
                            self.__deck.sY = len(self.__deck.table[self.__deck.sX]) - 1
                    else:
                        if self.__deck.sX == None or self.__deck.sY == None:
                            if self.__deck.sX == None:
                                self.__deck.sX = int(COLOMN / 2)
                            if self.__deck.sY == None:
                                self.__deck.sY = len(self.__deck.table[self.__deck.sX]) - 1
                        else:
                            self.__deck.sY += direc
                            if self.__deck.sY < 0:
                                self.__deck.sZ = 1
                                if self.__deck.sX >= CELL:
                                    self.__deck.sX = CELL - 1
                            elif self.__deck.sY == len(self.__deck.table[self.__deck.sX]):
                                self.__deck.sY -= 1
                else:
                    pass
                self.__checksXYZ()
                self.__show()
            elif ch == Macro.KEYCODE_SPACE:
                if self.__deck.toMoveX == None:
                    if self.__checkChooseable(self.__deck.sX, self.__deck.sY, self.__deck.sZ):
                        self.__deck.toMoveX = self.__deck.sX
                    else:
                        self.__promote = "Cannot operate."
                else:
                    if self.__checkMoveable(self.__deck.toMoveX):
                        if self.__deck.sZ == 0:
                            self.__deck.table[self.__deck.toMoveX].extend(self.__deck.table[self.__deck.sX][self.__deck.sY : len(self.__deck.table[self.__deck.sX])])
                            self.__deck.table[self.__deck.sX] = self.__deck.table[self.__deck.sX][0 : self.__deck.sY]
                        else:
                            self.__deck.table[self.__deck.toMoveX].append(self.__deck.cells[self.__deck.sX])
                            self.__deck.cells[self.__deck.sX] = None
                        self.__deck.sZ = 0
                        self.__deck.sX = self.__deck.toMoveX
                        self.__deck.sY = len(self.__deck.table[self.__deck.sX]) - 1
                    else:
                        self.__promote = "Cannot operate."
                    self.__deck.toMoveX = None
                self.__show()
            elif ch == Macro.KEYCODE_ENTER:
                if self.__deck.toMoveX == None:
                    if self.__deck.sZ == None:
                        self.__promote = "Cannot operate: no card is selected."
                    elif self.__deck.sZ == 0:
                        if self.__deck.sX == None:
                            self.__promote = "Cannot operate: no card is selected."
                        elif self.__deck.sY == None:
                            self.__promote = "Cannot operate: no card is selected."
                        elif self.__deck.sY == len(self.__deck.table[self.__deck.sX]) - 1:  
                            rk = self.__deck.table[self.__deck.sX][self.__deck.sY].rank
                            st = self.__deck.table[self.__deck.sX][self.__deck.sY].suit.value
                            self.__checkAndPileUp(rk, st)
                        else:
                            self.__promote = "Cannot operate: only one card can be piled up at once."
                    else:
                        if self.__deck.sX == None:
                            self.__promote = "Cannot operate: no card is selected."
                        else:
                            rk = self.__deck.cells[self.__deck.sX].rank
                            st = self.__deck.cells[self.__deck.sX].suit.value
                            self.__checkAndPileUp(rk, st)
                else:
                    self.__promote = "Cannot operate: need to finish current movement first."
                self.__show()
            elif ch == Macro.KEYCODE_F or ch == Macro.KEYCODE_CAPITAL_F:
                if self.__deck.toMoveX == None:
                    if self.__deck.sZ == None:
                        self.__promote = "Cannot operate: no card is selected."
                    elif self.__deck.sZ == 0:
                        if self.__deck.sX == None:
                            self.__promote = "Cannot operate: no card is selected."
                        elif self.__deck.sY == None:
                            self.__promote = "Cannot operate: no card is selected."
                        elif self.__deck.sY == len(self.__deck.table[self.__deck.sX]) - 1:
                            numEmptycell = self.__deck.cells.count(None)
                            if numEmptycell == 0:
                                self.__promote = "Cannot move to cell: no free cell left."
                            else:
                                # move to cell
                                index = self.__deck.cells.index(None)
                                self.__deck.cells[index] = self.__deck.table[self.__deck.sX][self.__deck.sY]
                                self.__deck.table[self.__deck.sX].pop()
                                self.__deck.sY -= 1
                                self.__promote = "Moved to cell."
                        else:
                            self.__promote = "Cannot move to cell: only one card can be freed at once."
                    else:
                        pass
                else:
                    self.__promote = "Cannot operate: need to finish current movement first."
                self.__show()
            elif ch == Macro.KEYCODE_F1:
                self.__promote = self.__getHelp()

    def __autoComplete(self):
        pass

    def __checkAndPileUp(self, rk, st):
        if not self.__deck.finished[st] == rk - 1:
            self.__promote = "Cannot operate."
        else:
            # move to finished piles
            self.__deck.finished[st] += 1
            if self.__deck.sZ == 0:
                self.__deck.table[self.__deck.sX].pop()
                self.__deck.sY -= 1
            else:
                self.__deck.cells[self.__deck.sX] = None
            self.__promote = "Piled up."

    def __checkExit(self, ch):
        exitKeys = (Macro.KEYCODE_E, Macro.KEYCODE_Q, Macro.KEYCODE_CAPITAL_E, Macro.KEYCODE_CAPITAL_Q)
        if ch in exitKeys:
            return True
        else:
            return False

    def __checkChooseable(self, x, y, z):
        if x == None or y == None or z == None:
            return False
        else:
            if z == 1:
                return True
            else:
                if y == len(self.__deck.table[x]) - 1:
                    return True
                else:
                    if self.__deck.table[x][y].color == self.__deck.table[x][y+1].color or not self.__deck.table[x][y].rank == self.__deck.table[x][y+1].rank + 1:
                        return False
                    else:
                        return self.__checkChooseable(x, y + 1, z)

    def __checkMoveable(self, x):
        cd = None
        if self.__deck.sZ == 0:
            cd = self.__deck.table[self.__deck.sX][self.__deck.sY]
        else:
            cd = self.__deck.cells[self.__deck.sX]
        ret = True
        if not len(self.__deck.table[x]) == 0 and (self.__deck.table[x][-1].color == cd.color or not self.__deck.table[x][-1].rank - 1 == cd.rank):
            ret = False
        else:
            numEmptyCol = 0
            for i in range(COLOMN):
                if len(self.__deck.table[i]) == 0:
                    numEmptyCol += 1
            if len(self.__deck.table[x]) == 0:
                numEmptyCol -= 1
            numEmptyCell = self.__deck.cells.count(None)
            numMaxMove = (numEmptyCell + 1) * (numEmptyCol + 1)
            numToMove = 1    # corresponds to the case of self.__deck.sZ = 1
            if self.__deck.sZ == 0:
                numToMove = len(self.__deck.table[self.__deck.sX]) - self.__deck.sY 
            if numToMove > numMaxMove:
                ret = False
        return ret

    def __checksXYZ(self):
        assert self.__deck.sZ == 0 or self.__deck.sZ == 1
        if self.__deck.sZ == 0:
            assert self.__deck.sX >= 0 and self.__deck.sX < COLOMN
            if len(self.__deck.table[self.__deck.sX]) > 0:
                assert self.__deck.sY >= 0 and self.__deck.sY < len(self.__deck.table[self.__deck.sX])
        else:
            assert self.__deck.sX >= 0 and self.__deck.sX < CELL

    def __checkSelected(self, z, x, y):
        ret = False
        if self.__deck.sZ == z and self.__deck.sX == x:
            if z == 1:
                ret = True
            else:
                if y >= self.__deck.sY:
                    ret = True
        return ret

    def __cmdShowCardFormatted(self, cd, totalLength, selected = False, color = None):
        length = 0
        chars = None
        if type(cd) == type('123'):
            chars = cd
            length = len(chars)
            if color == None:
                color = Macro.FOREGROUND_DARKWHITE
        else:
            chars = cd.__str__()
            length = len(chars)
            assert length == 2 or length == 3, str(cd) + ' ' + str(length)    # no jokers in freecell games
            if color == None:
                color = cd.color
        numLeftSpace = int((totalLength - length) / 2)
        numRightSpace = totalLength - length - numLeftSpace
        #if selected:
        #    numRightSpace -= 1
        assert numLeftSpace > 0 and numRightSpace > 0
        if selected:
            color |= (Macro.FOREGROUND_INTENSITY | Macro.BACKGROUND_DARKPINK | Macro.BACKGROUND_DARKYELLOW)
        setCmdTextColor(color)
        sys.stdout.write(' ' * numLeftSpace + chars + ' ' * numRightSpace)
        sys.stdout.flush()
        #if selected:
        #    setCmdTextColor(Macro.FOREGROUND_CYAN)
        #    sys.stdout.write(chr(Macro.ASCII_LEFTARROW))
        #   sys.stdout.flush()
        setCmdTextColor(Macro.FOREGROUND_DARKWHITE)

    def __cmdShowDeck(self):
        # parameters for style controlling
        lineWidth = 56
        columnWidth = int(lineWidth / COLOMN)
        emptyCellSymbol = '*'
        seperator = '- - '
        topMidSymbol = 'FreeCell'
        lenTopMid = len(topMidSymbol)
        lenEmptyCell = 5
        lenSeperator = len(seperator)
        numSeperator = int(lineWidth / lenSeperator)
        numTopLeftSpace = int((lineWidth - (CELL + PILES) * lenEmptyCell - lenTopMid) / 2)
        numTopRightSpace = lineWidth - (CELL + PILES) * lenEmptyCell - lenTopMid - numTopLeftSpace
        assert lineWidth % COLOMN == 0
        assert lineWidth % lenSeperator == 0
        assert numTopLeftSpace > 0 and numTopRightSpace > 0

        os.system('cls')
        sys.stdout.write('\n')
        # show cells
        for i in range(CELL):
            if self.__deck.cells[i] == None:
                self.__cmdShowCardFormatted(emptyCellSymbol, lenEmptyCell, self.__checkSelected(1, i, 0))
            else:
                self.__cmdShowCardFormatted(self.__deck.cells[i], lenEmptyCell, self.__checkSelected(1, i, 0))
        # interval
        sys.stdout.write(' ' * numTopLeftSpace + topMidSymbol + ' ' * numTopRightSpace)
        sys.stdout.flush()
        # show finished piles
        for i in range(PILES):
            if self.__deck.finished[i] == 0:
                self.__cmdShowCardFormatted(emptyCellSymbol, lenEmptyCell)
            else:
                self.__cmdShowCardFormatted(FreeCellCard(self.__deck.finished[i], Card.Suit(i)), lenEmptyCell)
        # seperator
        sys.stdout.write('\n' + seperator * numSeperator + '\n')
        # show table
        i = 0
        finish = False
        while not finish:
            finish = True
            for j in range(COLOMN):
                if len(self.__deck.table[j]) > i:
                    finish = False
                    self.__cmdShowCardFormatted(self.__deck.table[j][i], columnWidth, self.__checkSelected(0, j, i))    # print suit and rank and spaces for lining up
                elif len(self.__deck.table[j]) == i and self.__deck.toMoveX == j:
                    self.__cmdShowCardFormatted(chr(Macro.ASCII_UPARROW), columnWidth, False, Macro.FOREGROUND_CYAN | Macro.FOREGROUND_INTENSITY)
                else:
                    self.__cmdShowCardFormatted('', columnWidth)
            i += 1
            sys.stdout.write('\n')   

    def __cmdShowPromote(self):
        setCmdTextColor(Macro.FOREGROUND_DARKWHITE)
        sys.stdout.write('\n' + self.__promote)
        sys.stdout.flush()

    def __getHelp(self):
        pass

    def __show(self):
        if self.__mode == 'cmd':
            self.__cmdShowDeck()
            self.__cmdShowPromote()
        else:
            pass


if __name__ == '__main__':
    game = FrameManager()
    game.mainLoop()
    