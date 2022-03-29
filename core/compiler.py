from core.compiler_conclusions_cursors import *
from core.compiler_versions import CPLv1
from datetime import datetime

COMPILER_VERSIONS = [CPLv1]
LAST_COMPILER_VERSION = len(COMPILER_VERSIONS)
X, Y, CELLID = range(3)

class LoggerClass:
    types = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    DEBUG, INFO, WARNING, ERROR, CRITICAL = range(len(types))

def get(code: str) -> get_hinting:
    if code == '':
        return {}, CompilerConclusion(1), None
    l = 0
    if code[l:l+7] == 'VERSION':
        l += 7
        while code[l] == ' ':
            l += 1
        write = ''
        while code[l] != '\n':
            write += code[l]
            l += 1
    else:
        return {}, CompilerConclusion(2), None

    version = int(write)

    if 0 < version <= LAST_COMPILER_VERSION:
        compiler = COMPILER_VERSIONS[version-1]
        ret = list(compiler.get(code, l))
    else:
        return {}, CompilerConclusion(3), CompilerCursor(code, 0, 0)

    if ret[1] == CompilerConclusion(0) and version != LAST_COMPILER_VERSION:
        ret[1] = CompilerConclusion(1)
    return ret

class Cell:
    REPLY_DEFAULT, = range(1)
    def __init__(self, technical_values: dict, cellid: int, board: list, globals_object: list):
        self.techvars = {'X': 0,
                         'Y': 0}
        self.techvars.update(technical_values)
        self.cellid = cellid
        self.locals = {}
        self.board = board
        self.globals = globals_object
        self.tasks = []
        self.code = self.globals[0]['objdata'][self.globals[0]['idlist'][self.cellid]]
        if self.code['script']['create'] is not None:
            self.code['script']['create'](self)
    def step(self):
        if self.code['script']['step'] is not None:
            self.code['script']['step'](self)
    def reply(self, type: int, message: str):
        if type == Cell.REPLY_DEFAULT:
            self.globals[0]['logger'].append([LoggerClass.DEBUG,
                                              datetime.now(),
                                              f'Reply from Cell[{self.techvars["X"]}, {self.techvars["Y"]}]'
                                              f' ({self.globals[0]["idlist"][self.cellid]})',
                                              *message.split('\n')])
