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
EMPTY_SYMBOL = '*'
SEPERATOR = '- - '
TOP_MID_SYMBOL = 'FreeCell'
# direction
LEFT = (-1, 0)
RIGHT = (1, 0)
UP = (0, -1)
DOWN = (0, 1)
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

    def checkPileUpAble(self, coord):
        self.__checkCoord(coord)
        x, y, z = coord
        ret = True
        if z == 0 and (y < 0 or y < len(self.table[x]) - 1):
            ret = False
        else:
            cd = None
            if z == 0:
                cd = self.table[x][y]
            else:
                cd = self.cells[x]
            st = cd.suit.value
            rk = cd.rank
            if not self.finished[st] == rk - 1:
                ret = False
        return ret

    def checkChooseable(self, coord):
        self.__checkCoord(coord)
        x, y, z = coord
        if z == 1:
            return True
        else:
            if len(self.table[x]) == 0:
                return False
            elif y == len(self.table[x]) - 1:
                return True
            else:
                if self.table[x][y].color == self.table[x][y+1].color or not self.table[x][y].rank == self.table[x][y+1].rank + 1:
                    return False
                else:
                    return self.checkChooseable((x, y + 1, z))
    
    def checkFreeUpAble(self, coord):
        self.__checkCoord(coord)
        x, y, z = coord
        if z == 1:
            return False
        else:
            if len(self.table[x]) == 0:
                return False
            elif not y == len(self.table[x]) - 1:
                return False
            else:
                numEmptycell = self.cells.count(None)
                if numEmptycell == 0:
                    return False
                else:
                    return True

    def __checkCoord(self, coord):
        '''
        Ensure the coord can be legally selected with one exception that the column in the table is empty.
        '''
        assert type(coord) == type((0, 0, 0)) and len(coord) == 3
        x, y, z = coord
        assert z == 0 or z == 1
        if z == 0:
            assert x >= 0 and x < COLOMN
            if len(self.table[x]) > 0:
                assert y >= 0 and y < len(self.table[x])
        else:
            assert x >= 0 and x < CELL

    def checkMoveable(self, toX, coord):
        if not self.checkChooseable(coord):
            return False
        x, y, z = coord
        self.__checkToMoveX()
        cd = None
        if z == 0:
            cd = self.table[x][y]
        else:
            cd = self.cells[x]
        ret = True
        if not len(self.table[toX]) == 0 and (self.table[toX][-1].color == cd.color or not self.table[toX][-1].rank - 1 == cd.rank):
            ret = False
        else:
            numEmptyCol = 0
            for i in range(COLOMN):
                if len(self.table[i]) == 0:
                    numEmptyCol += 1
            if len(self.table[toX]) == 0:
                numEmptyCol -= 1
            numEmptyCell = self.cells.count(None)
            numMaxMove = (numEmptyCell + 1) * (numEmptyCol + 1)
            numToMove = 1    # corresponds to the case of self.sZ = 1
            if z == 0:
                numToMove = len(self.table[x]) - y
            if numToMove > numMaxMove:
                ret = False
        return ret

    def __checksXYZ(self):
        self.__checkCoord(self.currentSXYZ())

    def __checkToMoveX(self, x = None):
        if x == None:
            x = self.toMoveX
        assert(type(x) == type(0))
        if x < 0 or x > COLOMN:
            return False
        else:
            return True

    def currentSXYZ(self):
        return (self.sX, self.sY, self.sZ)

    def freeUp(self):
        # move to cell
        index = self.cells.index(None)
        self.cells[index] = self.table[self.sX][self.sY]
        self.table[self.sX].pop()
        self.sY -= 1
        if self.sY < 0:
            self.sY = 0

    def getCard(self, coord):
        self.__checkCoord(coord)
        x, y, z = coord
        if z == 0 and len(self.table[x]) == 0:
            raise AssertionError("Illegal coordinate of card.")
        if z == 0:
            return self.table[x][y]
        else:
            return self.cells[x]

    def getColumnLength(self, j):
        assert type(j) == type(0) and j >= 0 and j <= COLOMN
        return len(self.table[j])

    def getFinishedPileTop(self, i):
        assert type(i) == type(0) and i >= 0 and i < PILES
        return self.finished[i]

    def getSX(self):
        return self.sX

    def getToMoveX(self):
        return self.toMoveX

    def move(self):
        if self.sZ == 0:
            self.table[self.toMoveX].extend(self.table[self.sX][self.sY : len(self.table[self.sX])])
            self.table[self.sX] = self.table[self.sX][0 : self.sY]
        else:
            self.table[self.toMoveX].append(self.cells[self.sX])
            self.cells[self.sX] = None
        self.sZ = 0
        self.sX = self.toMoveX
        self.sY = len(self.table[self.sX]) - 1
        self.setToMoveX(None)

    def moveSXYZ(self, direc):
        legalDirec = (LEFT, RIGHT, UP, DOWN)
        assert direc in legalDirec
        try:
            self.__checksXYZ()
        except AssertionError:
            self.sZ = 0
            self.sX = int(COLOMN / 2)
            self.sY = len(self.table[self.sX]) - 1
        if self.sZ == 0:
            if direc == LEFT:
                self.sX -= 1
                self.sX %= COLOMN
                self.sY = len(self.table[self.sX]) - 1
            elif direc == RIGHT:
                self.sX += 1
                self.sX %= COLOMN
                self.sY = len(self.table[self.sX]) - 1
            elif direc == UP:
                self.sY -= 1
                if self.sY < 0:
                    self.sZ = 1
                    if self.sX >= CELL:
                        self.sX = CELL - 1
                    self.sY = 0
            elif direc == DOWN:
                self.sY += 1
                if self.sY >= len(self.table[self.sX]):
                    self.sY = len(self.table[self.sX]) - 1
        else:
            self.sY = 0
            if direc == LEFT:
                self.sX -= 1
                self.sX %= CELL
            elif direc == RIGHT:
                self.sX += 1
                self.sX %= CELL
            elif direc == DOWN:
                self.sZ = 0
                self.sY = len(self.table[self.sX]) - 1

    def moveToMoveX(self, direc):
        legalDirec = (LEFT, RIGHT)
        assert direc in legalDirec
        try:
            self.__checkToMoveX()
        except AssertionError:
            self.toMoveX = 0
        if direc == LEFT:
            self.toMoveX -= 1
            self.toMoveX %= COLOMN
        elif direc == RIGHT:
            self.toMoveX += 1
            self.toMoveX %= COLOMN

    def isMoving(self):
        if self.toMoveX == None:
            return False
        else:
            return True

    def pileUp(self):
        if self.sZ == 0:
            st = self.table[self.sX][self.sY].suit.value
            self.table[self.sX].pop()
            self.sY -= 1
        else:
            st = self.cells[self.sX].suit.value
            self.cells[self.sX] = None
        self.finished[st] += 1

    def setToMoveX(self, x):
        if not x == None:
            self.__checkToMoveX(x)
        self.toMoveX = x



class FreeCellFrameManager(CmdGameFrameManager):
    def __init__(self, mode = 'cmd'):
        CmdGameFrameManager.__init__(self)
        self.__mode = mode
        self.__deck = FreeCellDeck()
        self.__outputString = ""
        self.__numOutputLineCount = 0
        self.__maxOutputLineCount = 0
        
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

        self.WINDOWWIDTH = 56

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
            #except Exception as err:
                #status = (RUNTIME_ERROR, err)
            finally:
                pass
        if not status[0] == NORMAL_EXIT:
            self.__promote = status[1].__str__()
            self.__show()

    def __autoComplete(self):
        pass

    def __checkAndExit(self):
        return self.__ensure("Sure to exit?", "Quit...", "Ready.")

    def __checkSelected(self, z, x, y):
        ret = False
        if self.__deck.sZ == z and self.__deck.sX == x:
            if z == 1:
                ret = True
            else:
                if y >= self.__deck.sY:
                    ret = True
        return ret

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
        if self.__deck.isMoving():
            if self.__deck.checkMoveable(self.__deck.getToMoveX(), self.__deck.currentSXYZ()):
                self.__deck.move()
            else:
                self.__promote = "Cannot move."
            self.__deck.setToMoveX(None)
        else:
            if self.__deck.checkChooseable(self.__deck.currentSXYZ()):
                self.__deck.setToMoveX(self.__deck.getSX())
            else:
                self.__promote = "Cannot choose."
            
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
        lineWidth = self.WINDOWWIDTH
        columnWidth = int(lineWidth / COLOMN)
        lenTopMid = len(TOP_MID_SYMBOL)
        lenEmptyCell = 5
        lenSeperator = len(SEPERATOR)
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
            if self.__deck.getCard((i, 0, 1)) == None:
                self.__cmdShowCardFormatted(EMPTY_SYMBOL, lenEmptyCell, self.__checkSelected(1, i, 0))
            else:
                self.__cmdShowCardFormatted(self.__deck.getCard((i, 0, 1)), lenEmptyCell, self.__checkSelected(1, i, 0))
        # interval
        self.__outputString += (' ' * numTopLeftSpace + TOP_MID_SYMBOL + ' ' * numTopRightSpace)
        # show finished piles
        for i in range(PILES):
            if self.__deck.getFinishedPileTop(i) == 0:
                self.__cmdShowCardFormatted(EMPTY_SYMBOL, lenEmptyCell)
            else:
                self.__cmdShowCardFormatted(FreeCellCard(self.__deck.getFinishedPileTop(i), Card.Suit(i)), lenEmptyCell)
        # SEPERATOR
        self.__outputString += ('\n' + SEPERATOR * numSeperator + '\n')
        self.__numOutputLineCount += 2
        # show table
        i = 0
        finish = False
        while not finish:
            finish = True
            for j in range(COLOMN):
                if self.__deck.getColumnLength(j) > i:
                    finish = False
                    self.__cmdShowCardFormatted(self.__deck.getCard((j, i, 0)), columnWidth, self.__checkSelected(0, j, i))    # print suit and rank and spaces for lining up
                elif self.__deck.getColumnLength(j) == i and self.__deck.getToMoveX() == j:
                    self.__cmdShowCardFormatted(chr(Macro.ASCII_UPARROW), columnWidth, False, colorama.Fore.CYAN + colorama.Style.BRIGHT)
                else:
                    self.__cmdShowCardFormatted('', columnWidth)
            i += 1
            self.__outputString += '\n'
            self.__numOutputLineCount += 1

    def __cmdShowPromote(self):
        lineWidth = self.WINDOWWIDTH
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
        if self.__deck.isMoving():
            self.__promote = "Cannot operate: need to finish current movement first."
        else:
            if self.__deck.checkFreeUpAble(self.__deck.currentSXYZ()):
                self.__deck.freeUp()
                self.__promote = "Freed."
            else:
                self.__promote = "Cannot operate."

    def __getNextStep(self):
        pass

    def __moveLR(self, ch):
        # move selection to the left or the right
        direc = RIGHT
        self.__promote = "Pressed " + chr(Macro.ASCII_RIGHTARROW) + "."
        if ch == Macro.KEYCODE_LEFTARROW:
            direc = LEFT
            self.__promote = "Pressed " + chr(Macro.ASCII_LEFTARROW) + "."
        if self.__deck.isMoving():
            self.__deck.moveToMoveX(direc)
        else:
            self.__deck.moveSXYZ(direc)

    def __moveUD(self, ch):
        # move selection up or down
        direc = DOWN
        self.__promote = "Pressed " + chr(Macro.ASCII_DOWNARROW) + "."
        if ch == Macro.KEYCODE_UPARROW:
            direc = UP
            self.__promote = "Pressed " + chr(Macro.ASCII_UPARROW) + "."
        if self.__deck.isMoving():
            pass
        else:
            self.__deck.moveSXYZ(direc)
            
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
        self.__moveUD(ch)
        self.__show()
        return (NORMAL_OPERATE, "")

    def __pileUp(self):
        if self.__deck.isMoving():
            self.__chooseOrMove()
        else:
            if self.__deck.checkPileUpAble(self.__deck.currentSXYZ()):
                self.__deck.pileUp()
            else:
                self.__chooseOrMove()

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
                    self.__outputString += (' ' * self.WINDOWWIDTH + '\n')
                    self.__numOutputLineCount += 1
            self.__numOutputLineCount += 1
            print(self.__outputString)
            
        else:
            pass


if __name__ == '__main__':
    game = FreeCellFrameManager()
    game.mainLoop()
    