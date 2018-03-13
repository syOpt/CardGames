import colorama
import os, msvcrt, console, time
import Macro, Card
from CmdGameFrame import CmdGameFrameManager
colorama.init(autoreset = False)

COLOMN = 8
CELL = 4
PILES = 4
INITIAL_NUM = (7, 7, 7, 7, 6, 6, 6, 6)
MENU = 'F1/H: help\tEsc/Q: quit'
# Error codes
NORMAL_OPERATE = 0
NORMAL_EXIT = 1
RUNTIME_ERROR = 2
IO_ERROR = 3
ASSERTION_ERROR = 4
# assertions
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


class FreeCellFrameManager(CmdGameFrameManager):
    def __init__(self, mode = 'cmd'):
        CmdGameFrameManager.__init__(self)
        self.__mode = mode
        self.__deck = FreeCellDeck()
        self.__outputString = ""
        self.__numOutputLineCount = 0
        self.__maxOutputLineCount = 0
        self.__WINDOWWIDTH = 56
        self.__promote = ""
        self.__keyFuncDict = None
        self.__defaultKeyFuncDict = {Macro.KEYCODE_LEFTARROW: self.__onLeftRight,
                                     Macro.KEYCODE_RIGHTARROW: self.__onLeftRight,
                                     Macro.KEYCODE_UPARROW: self.__onUpDown,
                                     Macro.KEYCODE_DOWNARROW: self.__onUpDown,
                                     Macro.KEYCODE_ENTER: self.__onEnter,
                                     Macro.KEYCODE_SPACE: self.__onSpace,
                                     Macro.KEYCODE_F: self.__onF,
                                     Macro.KEYCODE_H: self.__onH,
                                     Macro.KEYCODE_Q: self.__onQ,
                                     Macro.KEYCODE_S: self.__onS,
                                     Macro.KEYCODE_CAPITAL_F: self.__onF,
                                     Macro.KEYCODE_CAPITAL_H: self.__onH,
                                     Macro.KEYCODE_CAPITAL_Q: self.__onQ,
                                     Macro.KEYCODE_CAPITAL_S: self.__onS,
                                     Macro.KEYCODE_CTRL_N: self.__onCtrl_N,
                                     Macro.KEYCODE_CTRL_Z: self.__onCtrl_Z,
                                     Macro.KEYCODE_F1: self.__onF1,
                                     Macro.KEYCODE_F2: self.__onF2,
                                     Macro.KEYCODE_F5: self.__onF5,
                                     Macro.KEYCODE_ESC: self.__onEsc,
        }
        self.__setKeyFuncDict(self.__defaultKeyFuncDict)

    def mainLoop(self):
        os.system('cls')
        self.__promote = "Ready."
        self.__show()
        status = (NORMAL_OPERATE, "")
        while status[0] == NORMAL_OPERATE:
            try:
                ch = getCh()
                if ch in self.__keyFuncDict.keys():
                    status = self.__keyFuncDict[ch](ch)
                    assert type(status) == type((NORMAL_OPERATE, "")) and len(status) == 2
            except AssertionError as err:
                status = (ASSERTION_ERROR, err)
            except IOError as err:
                status = (IO_ERROR, err)
            except Exception as err:
                status = (RUNTIME_ERROR, err)
            finally:
                pass
        if not status[0] == NORMAL_EXIT:
            self.__promote = status[1]
            self.__show()

    def __autoComplete(self):
        pass

    def __checkAndExit(self):
        return self.__ensure("Sure to exit?", "Exit...", "Ready.")

    def __checkAndPileUp(self, rk, st):
        ret = None
        if not self.__deck.finished[st] == rk - 1:
            self.__promote = "Cannot operate."
            ret = False
        else:
            # move to finished piles
            self.__deck.finished[st] += 1
            if self.__deck.sZ == 0:
                self.__deck.table[self.__deck.sX].pop()
                self.__deck.sY -= 1
            else:
                self.__deck.cells[self.__deck.sX] = None
            self.__promote = "Piled up."
            ret = True
        return ret

    def __checkChooseable(self, x, y, z):
        if x == None or y == None or z == None:
            return False
        else:
            if z == 1:
                return True
            else:
                if len(self.__deck.table[x]) == 0:
                    return False
                elif y == len(self.__deck.table[x]) - 1:
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

    def __checkSelected(self, z, x, y):
        ret = False
        if self.__deck.sZ == z and self.__deck.sX == x:
            if z == 1:
                ret = True
            else:
                if y >= self.__deck.sY:
                    ret = True
        return ret

    def __checksXYZ(self):
        assert self.__deck.sZ == 0 or self.__deck.sZ == 1
        if self.__deck.sZ == 0:
            assert self.__deck.sX >= 0 and self.__deck.sX < COLOMN
            if len(self.__deck.table[self.__deck.sX]) > 0:
                assert self.__deck.sY >= 0 and self.__deck.sY < len(self.__deck.table[self.__deck.sX])
        else:
            assert self.__deck.sX >= 0 and self.__deck.sX < CELL

    def __checkYesNo(self):
        yesKeys = (Macro.KEYCODE_CAPITAL_Y, Macro.KEYCODE_Y)
        noKeys = (Macro.KEYCODE_CAPITAL_N, Macro.KEYCODE_N)
        ch = getCh()
        while not (ch in yesKeys or ch in noKeys):
            ch = getCh()
        if ch in yesKeys:
            return True
        else:
            return False

    def __chooseOrMove(self):
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

    def __cmdShowCardFormatted(self, cd, totalLength, selected = False, color = None):
        length = 0
        chars = None
        if type(cd) == type('123'):
            chars = cd
            length = len(chars)
            if color == None:
                color = colorama.Fore.WHITE
        else:
            chars = cd.__str__()
            length = len(chars)
            assert length == 2 or length == 3, str(cd) + ' ' + str(length)    # no jokers in freecell games
            if color == None:
                color = cd.color
        numLeftSpace = int((totalLength - length) / 2)
        numRightSpace = totalLength - length - numLeftSpace
        assert numLeftSpace > 0 and numRightSpace > 0
        if selected:
            color += (colorama.Style.BRIGHT + colorama.Back.CYAN)
        self.__outputString += (color + ' ' * numLeftSpace + chars + ' ' * numRightSpace)
        self.__outputString += (colorama.Style.RESET_ALL)

    def __cmdShowDeck(self):
        # parameters for style controlling
        lineWidth = self.__WINDOWWIDTH
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

        self.__outputString += (' ' * lineWidth + '\n')
        self.__numOutputLineCount += 1
        # show cells
        for i in range(CELL):
            if self.__deck.cells[i] == None:
                self.__cmdShowCardFormatted(emptyCellSymbol, lenEmptyCell, self.__checkSelected(1, i, 0))
            else:
                self.__cmdShowCardFormatted(self.__deck.cells[i], lenEmptyCell, self.__checkSelected(1, i, 0))
        # interval
        self.__outputString += (' ' * numTopLeftSpace + topMidSymbol + ' ' * numTopRightSpace)
        # show finished piles
        for i in range(PILES):
            if self.__deck.finished[i] == 0:
                self.__cmdShowCardFormatted(emptyCellSymbol, lenEmptyCell)
            else:
                self.__cmdShowCardFormatted(FreeCellCard(self.__deck.finished[i], Card.Suit(i)), lenEmptyCell)
        # seperator
        self.__outputString += ('\n' + seperator * numSeperator + '\n')
        self.__numOutputLineCount += 2
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
                    self.__cmdShowCardFormatted(chr(Macro.ASCII_UPARROW), columnWidth, False, colorama.Fore.CYAN + colorama.Style.BRIGHT)
                else:
                    self.__cmdShowCardFormatted('', columnWidth)
            i += 1
            self.__outputString += '\n'
            self.__numOutputLineCount += 1

    def __cmdShowPromote(self):
        lineWidth = self.__WINDOWWIDTH
        lenPromote = len(self.__promote)
        lenMenu = len(MENU)
        numSpaces = lineWidth - lenPromote
        self.__outputString += (colorama.Style.RESET_ALL + ' ' * lineWidth +'\n' + self.__promote + ' ' * numSpaces + '\n')
        self.__outputString += (' ' * lineWidth + '\n')
        numSpaces = lineWidth - lenMenu
        self.__outputString += (MENU + ' ' * numSpaces + '\n')
        self.__numOutputLineCount += 4

    def __debug(self):
        self.__deck = FreeCellDeck()
        x, y = 0, 0
        for i in range(13, 0, -1):
            for j in range(4):
                if x == COLOMN:
                    x, y = 0, y+1
                self.__deck.table[x][y] = FreeCellCard(i, Card.Suit(j))
                x += 1
        self.__show()

    def __ensure(self, prmtOnEnsure, prmtOnYes, prmtOnNo):
        self.__promote = prmtOnEnsure + " (Y/N)"
        self.__show()
        ret = self.__checkYesNo()
        if ret:
            self.__promote = prmtOnYes
        else:
            self.__promote = prmtOnNo
        self.__show()
        return ret

    def __freeUp(self):
        if self.__deck.toMoveX == None:
            if self.__deck.sZ == None:
                self.__promote = "Cannot operate: no card is selected."
            elif self.__deck.sZ == 0:
                if self.__deck.sX == None:
                    self.__promote = "Cannot operate: no card is selected."
                elif self.__deck.sY == None or self.__deck.sY < 0:
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

    def __getNextStep(self):
        pass

    def __moveLR(self, ch):
        # move selection to the left or the right
        direc = 1
        self.__promote = "Pressed " + chr(Macro.ASCII_RIGHTARROW) + "."
        if ch == Macro.KEYCODE_LEFTARROW:
            direc = -1
            self.__promote = "Pressed " + chr(Macro.ASCII_LEFTARROW) + "."
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

    def __moveUP(self, ch):
        # move selection up or down
        direc = 1
        self.__promote = "Pressed " + chr(Macro.ASCII_DOWNARROW) + "."
        if ch == Macro.KEYCODE_UPARROW:
            direc = -1
            self.__promote = "Pressed " + chr(Macro.ASCII_UPARROW) + "."
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

    def __newGame(self):
        if self.__ensure("Start a new game?", "New Game.", "Ready."):
            self.__deck = FreeCellDeck()
            self.__show()
        else:
            pass

    def __onCtrl_N(self, ch):
        self.__newGame()
        return (NORMAL_OPERATE, "")

    def __onCtrl_Z(self, ch):
        self.__recall()
        self.__show()
        return (NORMAL_OPERATE, "")

    def __onEnter(self, ch):
        self.__pileUp()
        self.__show()
        return (NORMAL_OPERATE, "")

    def __onEsc(self, ch):
        if self.__checkAndExit():
            return (NORMAL_EXIT, "")
        else:
            return (NORMAL_OPERATE, "")

    def __onF(self, ch):
        self.__freeUp()
        self.__show()
        return (NORMAL_OPERATE, "")

    def __onF1(self, ch):
        pass
        return (NORMAL_OPERATE, "")

    def __onF2(self, ch):
        self.__restart()
        return (NORMAL_OPERATE, "")

    def __onF5(self, ch):
        self.__debug()
        return (NORMAL_OPERATE, "")

    def __onH(self, ch):
        pass
        return (NORMAL_OPERATE, "")

    def __onLeftRight(self, ch):
        self.__moveLR(ch)
        self.__checksXYZ()
        self.__show()
        return (NORMAL_OPERATE, "")

    def __onQ(self, ch):
        if self.__checkAndExit():
            return (NORMAL_EXIT, "")
        else:
            return (NORMAL_OPERATE, "")

    def __onS(self, ch):
        # do settings
        pass
        return (NORMAL_OPERATE, "")

    def __onSpace(self, ch):
        self.__chooseOrMove()
        self.__show()
        return (NORMAL_OPERATE, "")

    def __onUpDown(self, ch):
        self.__moveUP(ch)
        self.__checksXYZ()
        self.__show()
        return (NORMAL_OPERATE, "")

    def __pileUp(self):
        if self.__deck.toMoveX == None:
            if self.__deck.sZ == None:
                self.__promote = "Cannot operate: no card is selected."
            elif self.__deck.sZ == 0:
                if self.__deck.sX == None:
                    self.__promote = "Cannot operate: no card is selected."
                elif self.__deck.sY == None:
                    self.__promote = "Cannot operate: no card is selected."
                elif len(self.__deck.table[self.__deck.sX]) > 0 and self.__deck.sY == len(self.__deck.table[self.__deck.sX]) - 1:  
                    rk = self.__deck.table[self.__deck.sX][self.__deck.sY].rank
                    st = self.__deck.table[self.__deck.sX][self.__deck.sY].suit.value
                    #self.__checkAndPileUp(rk, st)
                    if not self.__checkAndPileUp(rk, st):
                        self.__chooseOrMove()
                else:
                    self.__chooseOrMove()
                    #self.__promote = "Cannot operate."
            else:
                if self.__deck.sX == None or self.__deck.cells[self.__deck.sX] == None:
                    self.__promote = "Cannot operate: no card is selected."
                else:
                    rk = self.__deck.cells[self.__deck.sX].rank
                    st = self.__deck.cells[self.__deck.sX].suit.value
                    #self.__checkAndPileUp(rk, st)
                    if not self.__checkAndPileUp(rk, st):
                        self.__chooseOrMove()
        else:
            self.__chooseOrMove()
            #self.__promote = "Cannot operate: need to finish current movement first."

    def __recall(self):
        pass

    def __restart(self):
        pass

    def __setKeyFuncDict(self, dict):
        self.__keyFuncDict = dict

    def __show(self):
        if self.__mode == 'cmd':
            self.__outputString = colorama.Style.RESET_ALL
            print('\x1b[1A' * self.__numOutputLineCount + '\x1b[2K'+'\r')
            self.__numOutputLineCount = 1
            self.__cmdShowDeck()
            self.__cmdShowPromote()
            if self.__numOutputLineCount > self.__maxOutputLineCount:
                self.__maxOutputLineCount = self.__numOutputLineCount
            else:
                for i in range(self.__maxOutputLineCount - self.__numOutputLineCount):
                    self.__outputString += (' ' * self.__WINDOWWIDTH + '\n')
                    self.__numOutputLineCount += 1
            self.__numOutputLineCount += 1
            print(self.__outputString)
            
        else:
            pass


if __name__ == '__main__':
    game = FreeCellFrameManager()
    game.mainLoop()
    