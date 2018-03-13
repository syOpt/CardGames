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



    