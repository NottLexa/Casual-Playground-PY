class Global:
    UNKNOWNBLOCK, SETVAR, RUNFUNC = range(3)
    FUNC, LOCALVAR, TECHVAR, GLOBALVAR, FIXEDVAR, EMPTY = range(6)

    @staticmethod
    def back_funcs(value_to_name):
        return ['UNKNOWNBLOCK', 'SETVAR', 'RUNFUNC'][value_to_name]

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
        return BlockSequence(self.blocks + other.blocks)
    def __call__(self, localcell = None):
        for b in self.blocks:
            b(localcell=localcell)
    def __getitem__(self, index):
        return self.blocks[index]
    def __setitem__(self, index, value):
        self.blocks[index] = value
    def __str__(self):
        return f'<BlockSequence [{", ".join(str(x) for x in self.blocks)}]>'
    def __repr__(self):
        return f'<BlockSeq:{len(self.blocks)}>'
    def recursive_str(self, tab=0):
        spaces = ' '*(4*tab)
        return '\n'.join([spaces+'<Block Sentence:', *[x.recursive_str(tab+1) for x in self.blocks], spaces+'>'])
    def __iter__(self):
        self.iter_count = 0
        return self
    def __next__(self):
        if self.iter_count < len(self.blocks):
            x = self.blocks[self.iter_count]
            self.iter_count += 1
            return repr(x)
        else:
            raise StopIteration

class Gate:
    def __init__(self, cond_blocks = None, false_block = None):
        if cond_blocks is None:
            cond_blocks = []
        self.cb = cond_blocks
        self.fb = false_block
    def __call__(self, localcell = None):
        for cond in self.cb:
            self.cb[cond](localcell=localcell)
            break
        else:
            if self.fb is not None:
                self.fb(localcell=localcell)

class While:
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block
    def __call__(self, localcell = None):
        while self.cond(localcell=localcell):
            self.block(localcell=localcell)

class Block:
    def __init__(self, type, *data):
        self.type = type
        self.data = data
    def __call__(self, localcell = None):
        match self.type:
            case Global.SETVAR:
                writeto, readfrom = self.data
                writeto.write(readfrom.read(localcell=localcell), localcell=localcell)
            case Global.RUNFUNC:
                self.data[0](localcell=localcell)
            case _:
                pass
    def __str__(self):
        return f'<Block {Global.back_funcs(self.type)} ({", ".join(map(str, self.data))})>'
    def __repr__(self):
        return f'<B:{Global.back_funcs(self.type)}:({", ".join(map(str, self.data))})>'

class Value:
    def __init__(self, type, value=None, source=None, args: list = None):
        if args is None:
            args = []
        self.type = type
        self.value = value
        self.source = source
        self.args = args
    def read(self, localcell = None):
        if localcell is not None:
            localsource = localcell
        else:
            localsource = self.source
        match self.type:
            case Global.FUNC:
                return self.value(*self.args)
            case Global.LOCALVAR:
                return localsource.localvars[self.value]
            case Global.TECHVAR:
                return localsource.techvars[self.value]
            case Global.GLOBALVAR:
                return self.source[self.value]
            case Global.FIXEDVAR:
                return self.value
    def write(self, newvalue, localcell = None):
        if localcell is not None:
            localsource = localcell
        else:
            localsource = self.source
        match self.type:
            case Global.LOCALVAR:
                localsource.localvars[self.value] = newvalue
            case Global.TECHVAR:
                localsource.techvars[self.value] = newvalue
            case Global.GLOBALVAR:
                self.source[self.value] = newvalue
    def __repr__(self):
        match self.type:
            case Global.FUNC:
                ret_args = f'[{", ".join([str(x) for x in self.args])}]'
                ret = (f'F {self.value}' if (self.source is None) else f'F {self.source}.{self.value}') + f' {ret_args}'
            case Global.LOCALVAR:
                ret = f'L {self.value}' if (self.source is None) else f'L {self.source}.{self.value}'
            case Global.TECHVAR:
                ret = f'T {self.value}' if (self.source is None) else f'T {self.source}.{self.value}'
            case Global.GLOBALVAR:
                ret = f'@{self.value}' if (self.source is None) else f'@{self.source}.{self.value}'
            case Global.FIXEDVAR:
                ret = str(self.value)
            case Global.EMPTY:
                ret = f'Empty'
            case _:
                ret = 'None'
        return f'<Val-{ret}>'
    def __str__(self):
        match self.type:
            case Global.FUNC:
                ret = (f'Func {self.value}' if (self.source is None) else f'Func {self.source}.{self.value}') + f' [{len(self.args)}]'
            case Global.LOCALVAR:
                ret = f'Local {self.value}' if (self.source is None) else f'Local {self.source}.{self.value}'
            case Global.TECHVAR:
                ret = f'Tech {self.value}' if (self.source is None) else f'Tech {self.source}.{self.value}'
            case Global.GLOBALVAR:
                ret = f'Global {self.value}' if (self.source is None) else f'Global {self.source}.{self.value}'
            case Global.FIXEDVAR:
                ret = str(self.value)
            case Global.EMPTY:
                ret = f'Empty'
            case _:
                ret = 'None'
        return f'<Value-{ret}>'