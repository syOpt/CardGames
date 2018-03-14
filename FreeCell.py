import colorama
import os, msvcrt, console, time, random
import Macro, Card
from CmdGameFrame import CmdGameFrameManager, RetType
colorama.init(autoreset = False)


COLUMN = 8
CELL = 4
PILES = 4
INITIAL_NUM = (7, 7, 7, 7, 6, 6, 6, 6)
MENU = 'F1/H: help\tEsc/Q: quit'
EMPTY_SYMBOL = '*'
SEPERATOR = '- - '
TOP_MID_SYMBOL = 'FreeCell'
# assertions
assert len(INITIAL_NUM) == COLUMN
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
        self.__table = list()
        self.__finished = [0, 0, 0, 0]
        self.__cells = [None, None, None, None]
        self.__sX = None
        self.__sY = None
        self.__sZ = None
        self.__toMoveX = None
        self.__initTable()
        assert len(self.__cells) == CELL
        assert len(self.__finished) == PILES

    def __initTable(self):
        for x in range(4):
            for y in range(1, 14):
                self.pile.append(FreeCellCard(y, Card.Suit(x)))
        self.shuffle()
        p = 0
        for i in range(len(INITIAL_NUM)):
            col = self.pile[p : p + INITIAL_NUM[i]]
            self.__table.append(col)
            p += INITIAL_NUM[i]

    def checkPileUpAble(self, coord):
        ret = RetType(RetType.TRUE, "")
        try:
            self.__checkCoord(coord)
            x, y, z = coord
            if z == 0 and (y < 0 or y < len(self.__table[x]) - 1):
                ret.setFalse()
                ret.setMessage("exactly one card can be piled up once")
            else:
                cd = None
                if z == 0:
                    cd = self.__table[x][y]
                else:
                    cd = self.__cells[x]
                if cd == None:
                    ret.setFalse()
                    ret.setMessage("no card selected")
                else:
                    st = cd.suit.value
                    rk = cd.rank
                    if not self.__finished[st] == rk - 1:
                        ret.setFalse()
                        msg = cd.color + FreeCellCard(rk - 1, st).__str__() + colorama.Style.RESET_ALL + " has to be piled up first"
                        ret.setMessage(msg)
        except AssertionError as err:
            ret.setFalse()
            ret.exitMsg(err.__str__())
            raise err
        finally:
            return ret

    def checkChooseable(self, coord):
        ret = RetType(RetType.TRUE, "")
        try:
            self.__checkCoord(coord)
            x, y, z = coord
            if z == 1:
                if self.__cells[x] == None:
                    ret.setFalse()
                    ret.setMessage("no card can be selected")
                else:
                    pass
            else:
                if len(self.__table[x]) == 0:
                    ret.setFalse()
                    ret.setMessage("no card can be selected in an empty column")
                elif y == len(self.__table[x]) - 1:
                    pass
                else:
                    if self.__table[x][y].color == self.__table[x][y+1].color or not self.__table[x][y].rank == self.__table[x][y+1].rank + 1:
                        ret.setFalse()
                        ret.setMessage("only cards with contiguous ranks and alternant colors can be selected once")
                    else:
                        return self.checkChooseable((x, y + 1, z))
        except AssertionError as err:
            ret.setFalse()
            ret.exitMsg(str(err))
            raise err
        finally:
            return ret
    
    def checkFreeUpAble(self, coord):
        ret = RetType(RetType.TRUE, "")
        try:
            self.__checkCoord(coord)
            x, y, z = coord
            if z == 1:
                ret.setFalse()
                ret.setMessage("the card has already been freed")
            else:
                if len(self.__table[x]) == 0:
                    ret.setFalse()
                    ret.setMessage("no card can be moved in an empty column")
                elif not y == len(self.__table[x]) - 1:
                    ret.setFalse()
                    ret.setMessage("exactly one card can be freed once")
                else:
                    numEmptycell = self.__cells.count(None)
                    if numEmptycell == 0:
                        ret.setFalse()
                        ret.setMessage("no vacant position left")
        except AssertionError as err:
            ret.setFalse()
            ret.exitMsg(err.__str__())
            raise err
        finally:
            return ret

    def __checkCoord(self, coord):
        '''
        Ensure coord is a legal coordinate with one exception that the column in the table is empty.
        '''
        assert type(coord) == type((0, 0, 0)) and len(coord) == 3
        x, y, z = coord
        assert z == 0 or z == 1
        if z == 0:
            assert x >= 0 and x < COLUMN
            if len(self.__table[x]) > 0:
                assert y >= 0 and y < len(self.__table[x])
        else:
            assert x >= 0 and x < CELL

    def checkMoveable(self, toX, coord, checkedChooseablility = False):
        ret = RetType(RetType.TRUE, "")
        try:
            if not checkedChooseablility:
                ret = self.checkChooseable(coord)
            if ret:
                x, y, z = coord
                self.__checkToMoveX(toX)
                cd = None
                if z == 0:
                    cd = self.__table[x][y]
                else:
                    cd = self.__cells[x]
                if cd == None:
                    ret.setFalse()
                    ret.setMessage("no card is selected")
                elif not self.getColumnLength(toX) == 0 and (self.__table[toX][-1].color == cd.color or not self.__table[toX][-1].rank - 1 == cd.rank):
                    ret.setFalse()
                    ret.setMessage("card (or cards) can be moved either to an empty column or underneath a destination card, in the latter situation, the color of the card (or the top one of the cards) must be different from the destination card, and the rank must be exactly one smaller")
                else:
                    numEmptyCol = 0
                    for i in range(COLUMN):
                        if len(self.__table[i]) == 0:
                            numEmptyCol += 1
                    if len(self.__table[toX]) == 0:
                        numEmptyCol -= 1
                    numEmptyCell = self.__cells.count(None)
                    numMaxMove = (numEmptyCell + 1) * (numEmptyCol + 1)
                    numToMove = 1    # corresponds to the case of self.__sZ = 1
                    if z == 0:
                        numToMove = len(self.__table[x]) - y
                    if numToMove > numMaxMove:
                        ret.setFalse()
                        ret.setMessage("at most %d cards can be moved at present" %(numMaxMove))
        except AssertionError as err:
            ret.setFalse()
            ret.exitMsg(err.__str__())
            raise err
        finally:
            return ret

    def checkSelected(self, z, x, y):
        ret = RetType(RetType.FALSE, "")
        if self.__sZ == z and self.__sX == x:
            if z == 1:
                ret.setTrue()
            else:
                if y >= self.__sY:
                    ret.setTrue()
        return ret

    def __checksXYZ(self):
        self.__checkCoord(self.currentSXYZ())

    def __checkToMoveX(self, x = None):
        ret = RetType(RetType.TRUE, "")
        if x == None:
            x = self.__toMoveX
        assert type(x) == type(0), "illegal column index"
        if x < 0 or x > COLUMN:
            ret.setFalse()
        return ret

    def currentSXYZ(self):
        return (self.__sX, self.__sY, self.__sZ)

    def freeUp(self):
        # move to cell
        index = self.__cells.index(None)
        self.__cells[index] = self.__table[self.__sX][self.__sY]
        self.__table[self.__sX].pop()
        self.__sY -= 1
        if self.__sY < 0:
            self.__sY = 0
        return self

    def getCard(self, coord):
        self.__checkCoord(coord)
        x, y, z = coord
        if z == 0 and len(self.__table[x]) == 0:
            raise AssertionError("illegal coordinate of card")
        if z == 0:
            return self.__table[x][y]
        else:
            return self.__cells[x]

    def getColumnLength(self, j):
        assert type(j) == type(0) and j >= 0 and j <= COLUMN, "illegal column index"
        return len(self.__table[j])

    def getFinishedPileTop(self, i):
        assert type(i) == type(0) and i >= 0 and i < PILES, "illegal pile index"
        return self.__finished[i]

    def getNextPossibleStep(self):
        ret = []
        # search in the table
        for x in range(COLUMN):
            y = len(self.__table[x]) - 1
            deprt = [x, y, 0]
            if y >= 0 and self.checkPileUpAble(tuple(deprt)):
                ret.append((tuple(deprt), self.pileUp, None))
            if y >= 0 and self.checkFreeUpAble(tuple(deprt)):
                ret.append((tuple(deprt), self.freeUp, None))
            while y >= 0 and self.checkChooseable(tuple(deprt)):
                y -= 1
                deprt = [x, y, 0]
            y += 1
            deprt = [x, y, 0]
            while y < self.getColumnLength(x):
                for dest in range(COLUMN):
                    if self.checkMoveable(dest, tuple(deprt), True):
                        ret.append((tuple(deprt), self.move, dest))
                y += 1
                deprt = [x, y, 0]
        # search in cells
        for x in range(CELL):
            deprt = [x, 0, 1]
            if self.checkPileUpAble(tuple(deprt)):
                ret.append((tuple(deprt), self.pileUp, None))
            for dest in range(COLUMN):
                if self.checkMoveable(dest, tuple(deprt)):
                    ret.append((tuple(deprt), self.move, dest))
        return ret

    def getSX(self):
        return self.__sX

    def getToMoveX(self):
        return self.__toMoveX

    def move(self):
        if self.__sZ == 0:
            self.__table[self.__toMoveX].extend(self.__table[self.__sX][self.__sY : len(self.__table[self.__sX])])
            self.__table[self.__sX] = self.__table[self.__sX][0 : self.__sY]
        else:
            self.__table[self.__toMoveX].append(self.__cells[self.__sX])
            self.__cells[self.__sX] = None
        self.__sZ = 0
        self.__sX = self.__toMoveX
        self.__sY = len(self.__table[self.__sX]) - 1
        self.setToMoveX(None)
        return self

    def moveSXYZ(self, direc):
        legalDirec = (Macro.DIRECTION_LEFT, Macro.DIRECTION_RIGHT, Macro.DIRECTION_UP, Macro.DIRECTION_DOWN)
        assert direc in legalDirec
        # if the current sX, sY, or sZ is not legal, set them legal
        try:
            self.__checksXYZ()
        except AssertionError:
            self.__sZ = 0
            self.__sX = int(COLUMN / 2)
            self.__sY = len(self.__table[self.__sX]) - 1

        if self.__sZ == 0:
            if direc == Macro.DIRECTION_LEFT:
                self.__sX -= 1
                self.__sX %= COLUMN
                self.__sY = len(self.__table[self.__sX]) - 1
            elif direc == Macro.DIRECTION_RIGHT:
                self.__sX += 1
                self.__sX %= COLUMN
                self.__sY = len(self.__table[self.__sX]) - 1
            elif direc == Macro.DIRECTION_UP:
                self.__sY -= 1
                if self.__sY < 0:
                    self.__sZ = 1
                    if self.__sX >= CELL:
                        self.__sX = CELL - 1
                    self.__sY = 0
            elif direc == Macro.DIRECTION_DOWN:
                self.__sY += 1
                if self.__sY >= len(self.__table[self.__sX]):
                    self.__sY = len(self.__table[self.__sX]) - 1
        else:
            self.__sY = 0
            if direc == Macro.DIRECTION_LEFT:
                self.__sX -= 1
                self.__sX %= CELL
            elif direc == Macro.DIRECTION_RIGHT:
                self.__sX += 1
                self.__sX %= CELL
            elif direc == Macro.DIRECTION_DOWN:
                self.__sZ = 0
                self.__sY = len(self.__table[self.__sX]) - 1
        return self

    def moveToMoveX(self, direc):
        legalDirec = (Macro.DIRECTION_LEFT, Macro.DIRECTION_RIGHT)
        assert direc in legalDirec
        # if the current toMoveX is not legal, set them legal
        try:
            self.__checkToMoveX()
        except AssertionError:
            self.__toMoveX = 0
        
        if direc == Macro.DIRECTION_LEFT:
            self.__toMoveX -= 1
            self.__toMoveX %= COLUMN
        elif direc == Macro.DIRECTION_RIGHT:
            self.__toMoveX += 1
            self.__toMoveX %= COLUMN
        return self

    def isMoving(self):
        if self.__toMoveX == None:
            return False
        else:
            return True

    def pileUp(self):
        if self.__sZ == 0:
            st = self.__table[self.__sX][self.__sY].suit.value
            self.__table[self.__sX].pop()
            self.__sY -= 1
        else:
            st = self.__cells[self.__sX].suit.value
            self.__cells[self.__sX] = None
        self.__finished[st] += 1
        return self

    def setToMoveX(self, x):
        if not x == None:
            self.__checkToMoveX(x)
        self.__toMoveX = x
        return self



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
        status = RetType()
        while status.normalOp():
            try:
                ch = getCh()
                if ch in self.__keyFuncDict.keys():
                    status = self.__keyFuncDict[ch](ch)
                    assert type(status) == type(RetType())
            except AssertionError as err:
                status = RetType(RetType.ASSERTION_ERROR, err.__str__())
            except IOError as err:
                status = RetType(RetType.IO_ERROR, err.__str__())
        if not status.normalExit():
            self.__promote = status
            self.__show()

    def __autoComplete(self):
        pass

    def __checkAndExit(self):
        return self.__ensure("Sure to exit?", "Quit...", "Ready.")

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
            retCheck = self.__deck.checkMoveable(self.__deck.getToMoveX(), self.__deck.currentSXYZ())
            if retCheck:
                self.__deck.move()
            else:
                self.__promote = "Cannot move: " + str(retCheck) + "."
            self.__deck.setToMoveX(None)
        else:
            retCheck = self.__deck.checkChooseable(self.__deck.currentSXYZ())
            if retCheck:
                self.__deck.setToMoveX(self.__deck.getSX())
            else:
                self.__promote = "Cannot choose: " + str(retCheck) + "."
            
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
        columnWidth = int(lineWidth / COLUMN)
        lenTopMid = len(TOP_MID_SYMBOL)
        lenEmptyCell = 5
        lenSeperator = len(SEPERATOR)
        numSeperator = int(lineWidth / lenSeperator)
        numTopLeftSpace = int((lineWidth - (CELL + PILES) * lenEmptyCell - lenTopMid) / 2)
        numTopRightSpace = lineWidth - (CELL + PILES) * lenEmptyCell - lenTopMid - numTopLeftSpace
        assert lineWidth % COLUMN == 0
        assert lineWidth % lenSeperator == 0
        assert numTopLeftSpace > 0 and numTopRightSpace > 0

        self.__outputString += (' ' * lineWidth + '\n')
        self.__numOutputLineCount += 1
        # show cells
        for i in range(CELL):
            if self.__deck.getCard((i, 0, 1)) == None:
                self.__cmdShowCardFormatted(EMPTY_SYMBOL, lenEmptyCell, self.__deck.checkSelected(1, i, 0))
            else:
                self.__cmdShowCardFormatted(self.__deck.getCard((i, 0, 1)), lenEmptyCell, self.__deck.checkSelected(1, i, 0))
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
            for j in range(COLUMN):
                if self.__deck.getColumnLength(j) > i:
                    finish = False
                    self.__cmdShowCardFormatted(self.__deck.getCard((j, i, 0)), columnWidth, self.__deck.checkSelected(0, j, i))    # print suit and rank and spaces for lining up
                elif self.__deck.getColumnLength(j) == i and self.__deck.getToMoveX() == j:
                    self.__cmdShowCardFormatted(chr(Macro.ASCII_UPARROW), columnWidth, False, colorama.Fore.CYAN + colorama.Style.BRIGHT)
                else:
                    self.__cmdShowCardFormatted('', columnWidth)
            i += 1
            self.__outputString += '\n'
            self.__numOutputLineCount += 1

    def __cmdShowMenu(self):
        lineWidth = self.WINDOWWIDTH
        lenMenu = len(MENU)
        numSpaces = lineWidth - lenMenu
        # show menu
        self.__outputString += (' ' * lineWidth + '\n' + MENU + ' ' * numSpaces + '\n')
        self.__numOutputLineCount += 2

    def __cmdShowPromote(self):
        lineWidth = self.WINDOWWIDTH
        lenPromote = len(self.__promote)
        numSpaces = lineWidth - lenPromote % lineWidth
        
        self.__outputString += (colorama.Style.RESET_ALL + ' ' * lineWidth +'\n')
        self.__numOutputLineCount += 1
        # show promote
        i = -1
        for i in range(int(lenPromote / lineWidth)):
             self.__outputString += (self.__promote[i*lineWidth : (i+1)*lineWidth] + '\n')
             self.__numOutputLineCount += 1
        self.__outputString += (self.__promote[(i+1)*lineWidth : lenPromote] + ' ' * numSpaces + '\n')
        self.__numOutputLineCount += 1
        # self.__numOutputLineCount += int(lenPromote / lineWidth)
        # if lenPromote % lineWidth == 0:
        #     self.__numOutputLineCount -= 1
        
    def __debug(self):
        self.__deck = FreeCellDeck()
        x, y = 0, 0
        for i in range(13, 0, -1):
            for j in range(4):
                if x == COLUMN:
                    x, y = 0, y+1
                self.__deck._FreeCellDeck__table[x][y] = FreeCellCard(i, Card.Suit(j))    # thanks to name mangling
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

    def __getHint(self):
        hints = self.__deck.getNextPossibleStep()
        numHints = len(hints)
        if numHints > 0:
            indexHint = random.randrange(0, numHints)
            deprt, method, args = hints[indexHint]
            if method == self.__deck.pileUp:
                cd = self.__deck.getCard(deprt)
                self.__promote = "Pile up " + cd.color + cd.__str__() + colorama.Style.RESET_ALL
            elif method == self.__deck.freeUp:
                cd = self.__deck.getCard(deprt)
                self.__promote = "Free " + cd.color + cd.__str__() + colorama.Style.RESET_ALL
            elif method == self.__deck.move:
                self.__promote = "Move "
                x, y, z = deprt
                if z == 0:
                    while y < self.__deck.getColumnLength(x):
                        cd = self.__deck.getCard((x, y, z))
                        self.__promote += (cd.color + cd.__str__() + colorama.Style.RESET_ALL)
                        y += 1
                else:
                    cd = self.__deck.getCard((x, y, z))
                    self.__promote += (cd.color + cd.__str__() + colorama.Style.RESET_ALL)
                self.__promote += (" to column " + str(args + 1))
            self.__promote += " (%d / %d)" %(indexHint + 1, numHints)
        else:
            self.__promote = "Nowhere to go..."

    def __moveLR(self, ch):
        # move selection to the left or the right
        direc = Macro.DIRECTION_RIGHT
        self.__promote = "Pressed " + chr(Macro.ASCII_RIGHTARROW) + "."
        if ch == Macro.KEYCODE_LEFTARROW:
            direc = Macro.DIRECTION_LEFT
            self.__promote = "Pressed " + chr(Macro.ASCII_LEFTARROW) + "."
        if self.__deck.isMoving():
            self.__deck.moveToMoveX(direc)
        else:
            self.__deck.moveSXYZ(direc)

    def __moveUD(self, ch):
        # move selection up or down
        direc = Macro.DIRECTION_DOWN
        self.__promote = "Pressed " + chr(Macro.ASCII_DOWNARROW) + "."
        if ch == Macro.KEYCODE_UPARROW:
            direc = Macro.DIRECTION_UP
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
        return RetType()

    def __onCtrl_Z(self, ch):
        self.__recall()
        self.__show()
        return RetType()

    def __onEnter(self, ch):
        self.__pileUp()
        self.__show()
        return RetType()

    def __onEsc(self, ch):
        if self.__checkAndExit():
            return RetType(RetType.NORMAL_EXIT, "")
        else:
            return RetType()

    def __onF(self, ch):
        self.__freeUp()
        self.__show()
        return RetType()

    def __onF1(self, ch):
        pass
        return RetType()

    def __onF2(self, ch):
        self.__restart()
        return RetType()

    def __onF5(self, ch):
        self.__debug()
        return RetType()

    def __onH(self, ch):
        self.__getHint()
        self.__show()
        return RetType()

    def __onLeftRight(self, ch):
        self.__moveLR(ch)
        self.__show()
        return RetType()

    def __onQ(self, ch):
        if self.__checkAndExit():
            return RetType(RetType.NORMAL_EXIT, "")
        else:
            return RetType()

    def __onS(self, ch):
        # do settings
        pass
        return RetType()

    def __onSpace(self, ch):
        self.__chooseOrMove()
        self.__show()
        return RetType()

    def __onUpDown(self, ch):
        self.__moveUD(ch)
        self.__show()
        return RetType()

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
            self.__cmdShowMenu()
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
    