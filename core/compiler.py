from core.compiler_conclusions_cursors import *
from core.compiler_versions import CPLv1

COMPILER_VERSIONS = [CPLv1]
LAST_COMPILER_VERSION = len(COMPILER_VERSIONS)
X, Y, CELLID = range(3)

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
    def __init__(self, technical_values: dict, codeid: int, board: list, globals_object: list):
        self.techvars = {'X': 0,
                         'Y': 0}
        self.techvars.update(technical_values)
        self.codeid = codeid
        self.locals = {}
        self.board = board
        self.globals = globals_object
        self.tasks = []
        self.code = self.globals[0]['objdata'][self.globals[0]['idlist'][self.codeid]]
        if self.code['script']['create'] is not None:
            self.code['script']['create'](self)
    def step(self):
        if self.code['script']['step'] is not None:
            self.code['script']['step'](self)