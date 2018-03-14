import os, abc

class CmdGameFrameManager():
    def __init__(self):
        os.system('echo off')
        self.__keyFuncDict = {}

    def __del__(self):
        os.system('echo on')

    @abc.abstractmethod
    def mainLoop(self):
        pass


class RetType():
    # Error codes
    NORMAL_OPERATE = 0
    NORMAL_EXIT = 1
    RUNTIME_ERROR = 2
    IO_ERROR = 3
    ASSERTION_ERROR = 4
    TRUE = -1
    FALSE = -2
    __CODE_RANGE = range(-2, 5)

    def __init__(self, exc = NORMAL_OPERATE, msg = ""):
        self.exitCode = exc
        self.exitMsg = msg

    def __str__(self):
        return str(self.exitMsg)

    def __bool__(self):
        if self.exitCode == RetType.TRUE:
            return True
        elif self.exitCode == RetType.FALSE:
            return False
        else:
            raise RuntimeError("Value of member self.exitCode of the RetType instance is not True or False.")

    def normalOp(self):
        if self.exitCode == RetType.NORMAL_OPERATE:
            return True
        else:
            return False

    def normalExit(self):
        if self.exitCode == RetType.NORMAL_EXIT:
            return True
        else:
            return False

    def setCode(self, code):
        assert code in RetType.__CODE_RANGE, "invalid exit code"
        self.exitCode = code
        return self

    def setFalse(self):
        self.exitCode = RetType.FALSE
        return self

    def setMessage(self, msg):
        self.exitMsg = msg
        return self

    def setTrue(self):
        self.exitCode = RetType.TRUE
        return self




if __name__ == "__main__":
    pass    