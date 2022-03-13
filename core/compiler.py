from core.compiler_conclusions_cursors import *
from core.compiler_versions import V1

COMPILER_VERSIONS = [V1]
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
    def __init__(self, technical_values: dict, cell_code: dict):
        self.techvars = {'X': 0,
                         'Y': 0}.update(technical_values)
        self.code = cell_code.copy()
        self.localvars = {}
        if self.code['script']['create'] is not None:
            execreturn = self.code['script']['create'](localcell=self)
    def step(self):
        if self.code['script']['step'] is not None:
            execreturn = self.code['script']['step'](localcell=self)