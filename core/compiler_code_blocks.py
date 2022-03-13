class Global:
    SETVAR, DOCOREFUNC = range(2)
    FUNC, LOCALVAR, TECHVAR, GLOBALVAR, FIXEDVAR = range(5)

    @staticmethod
    def back_funcs(value_to_name):
        return ['SETVAR', 'DOCOREFUNC'][value_to_name]

class BlockSequence:
    def __init__(self, blocks: list = []):
        self.blocks = blocks
    def muladd(self, other):
        self.blocks.extend(other)
    def add(self, other):
        self.blocks.append(other)
    def append(self, other):
        self.add(other)
    def __iadd__(self, other):
        self.add(other)
    def __add__(self, other):
        return self.blocks + other.blocks
    def __call__(self):
        for b in self.blocks:
            b()
    def __getitem__(self, index):
        return self.blocks[index]
    def __setitem__(self, index, value):
        self.blocks[index] = value
    def __str__(self):
        return f'<BlockSequence [{", ".join(str(x) for x in self.blocks)}]>'
    def __repr__(self):
        return f'<BlockSequence L{len(self.blocks)}>'
    def recursive_str(self, tab=0):
        spaces = ' '*(4*tab)
        return '\n'.join([spaces+'<Block Sentence:', *[x.recursive_str(tab+1) for x in self.blocks], spaces+'>'])

class Gate:
    def __init__(self, cond_blocks = None, false_block = None):
        if cond_blocks is None:
            cond_blocks = []
        self.cb = cond_blocks
        self.fb = false_block
    def __call__(self):
        for cond in self.cb:
            self.cb[cond]()
            break
        else:
            if self.fb is not None:
                self.fb()

class While:
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block
    def __call__(self):
        while self.cond():
            self.block()

class Block:
    def __init__(self, type, *data):
        self.type = type
        self.data = data
    def __call__(self):
        match self.type:
            case Global.SETVAR:
                writeto, readfrom = self.data
                writeto.write(readfrom.read())
            case _:
                pass
    def __str__(self):
        return f'<Block {Global.back_funcs(self.type)} ({", ".join(map(str, self.data))})>'

class Value:
    def __init__(self, type, value, source=None):
        self.type = type
        self.value = value
        self.source = source
    def read(self):
        match self.type:
            case Global.FUNC:
                return self.value()
            case Global.LOCALVAR:
                return self.source.localvars[self.value]
            case Global.TECHVAR:
                return self.source.techvars[self.value]
            case Global.GLOBALVAR:
                return self.source[self.value]
            case Global.FIXEDVAR:
                return self.value
    def write(self, newvalue):
        match self.type:
            case Global.LOCALVAR:
                self.source.localvars[self.value] = newvalue
            case Global.TECHVAR:
                self.source.techvars[self.value] = newvalue
            case Global.GLOBALVAR:
                self.source[self.value] = newvalue
    def __repr__(self):
        match self.type:
            case Global.FUNC:
                ret = f'F {self.value}' if (self.source is None) else f'F {self.source}.{self.value}'
            case Global.LOCALVAR:
                ret = f'L {self.value}' if (self.source is None) else f'L {self.source}.{self.value}'
            case Global.TECHVAR:
                ret = f'T {self.value}' if (self.source is None) else f'T {self.source}.{self.value}'
            case Global.GLOBALVAR:
                ret = f'@{self.value}' if (self.source is None) else f'@{self.source}.{self.value}'
            case Global.FIXEDVAR:
                ret = str(self.value)
            case _:
                ret = 'None'
        return f'<Val-{ret}>'
    def __str__(self):
        match self.type:
            case Global.FUNC:
                ret = f'Func {self.value}' if (self.source is None) else f'Func {self.source}.{self.value}'
            case Global.LOCALVAR:
                ret = f'Local {self.value}' if (self.source is None) else f'Local {self.source}.{self.value}'
            case Global.TECHVAR:
                ret = f'Tech {self.value}' if (self.source is None) else f'Tech {self.source}.{self.value}'
            case Global.GLOBALVAR:
                ret = f'Global {self.value}' if (self.source is None) else f'Global {self.source}.{self.value}'
            case Global.FIXEDVAR:
                ret = str(self.value)
            case _:
                ret = 'Empty'
        return f'<Value-{ret}>'