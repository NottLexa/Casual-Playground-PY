# Casual Playground Compiler - version 1
#
# Hello world!

from .compiler_other_instruments import *
from . import compiler_code_blocks as ccb

MO = MATHOPERATORS = ['+-', '*/']
SET_MO = set(''.join(MO))

class Order:
    SET_CELL, = range(1)
    def __init__(self, type, *args):
        self.type = type
        self.args = args

def chapter_cell(code: str, startl: int):
    l = startl
    ret = {}
    if code[l:l+4] == 'CELL':
        l += 4
        ret['type'] = 'CELL'

        write, concl, cur = split_args1(code, l, '\n')
        if not correct_concl(concl):
            return 0, {}, concl, cur
        if len(write) > 0:
            ret['name'] = eval(write[0])
        if len(write) > 1:
            ret['desc'] = eval(write[1])
    return l, ret, CompilerConclusion(0), None

def chapter_notexture(code: str, startl: int):
    l = startl
    ret = {}
    if code[l:l+9] == 'NOTEXTURE':
        ret['notexture'] = [0, 0, 0]
        l += 9

        l, write, concl, cur = split_args2(code, l)
        if not correct_concl(concl):
            return 0, {}, concl, cur
        if len(write) > 0:
            ret['notexture'][0] = int(float(write[0]))
        if len(write) > 1:
            ret['notexture'][1] = int(float(write[1]))
        if len(write) > 2:
            ret['notexture'][2] = int(float(write[2]))
    return l, ret, CompilerConclusion(0), None

def chapter_localization(code: str, startl: int):
    l = startl
    ret_localization = {}
    if code[l:l + 12] == 'LOCALIZATION':
        ret_localization = {}
        l += 12
        while code[l] != '\n':
            l += 1
        l += 1
        while code[l:l + 4] == '    ':
            l += 4
            l, write, concl, cur = split_args2(code, l)
            if not correct_concl(concl):
                return 0, {}, concl, cur
            lang, name, desc = write
            ret_localization[lang] = {'name': eval(name), 'desc': eval(desc)}
    return l, ret_localization, CompilerConclusion(0), None

def chapter_script(code: str, startl: int, version: int):
    l = startl
    ret_script = {}
    if code[l:l + 6] == 'SCRIPT':
        l += 6
        while code[l] == ' ':
            l += 1
        write = ''
        while code[l] not in '\n ':
            write += code[l]
            l += 1
        script_type = write.lower()
        while code[l] != '\n':
            l += 1
        l += 1
        l, ret_script[script_type], concl, cur = read_code(code, l, tab=1, version=version)
        if concl != CompilerConclusion(0):
            return 0, {}, concl, cur
    return l, ret_script, CompilerConclusion(0), None

def get(code: str, start: int, end: int = None) -> get_hinting:
    if end is None:
        end = len(code)
    else:
        end = min(end, len(code))

    ret = {'version': 1,
           'type': 'CELL',
           'name': 'Cell',
           'desc': 'No description given.',
           'notexture': [255, 255, 255],
           'localization': {},
           'script': {'create': None,
                      'step': None}}

    l = start
    while l < end:
        l, ret_expand, concl, cursor = chapter_cell(code, l)
        if concl != CompilerConclusion(0):
            return {}, concl, cursor
        ret.update(ret_expand)
        l, ret_expand, concl, cursor = chapter_notexture(code, l)
        if concl != CompilerConclusion(0):
            return {}, concl, cursor
        ret.update(ret_expand)
        l, ret_expand, concl, cursor = chapter_localization(code, l)
        if concl != CompilerConclusion(0):
            return {}, concl, cursor
        ret['localization'].update(ret_expand)
        l, ret_expand, concl, cursor = chapter_script(code, l, ret['version'])
        if concl != CompilerConclusion(0):
            return {}, concl, cursor
        ret['script'].update(ret_expand)

        l += 1

    return ret, CompilerConclusion(0), None

def read_code(code: str, startl: int, version: int, tab: int = 0):
    code_sequence = ccb.BlockSequence()
    end = len(code)
    l = startl
    while l < end:
        spaces = 0
        while code[l] == ' ':
            l += 1
            spaces += 1
        if spaces < tab*4: # not in tab
            break
        elif spaces > tab*4: # upper tab
            l, upper_tab, concl, cur = read_code(code, l-spaces, tab+1, version)
            if concl != CompilerConclusion(0):
                return 0, ccb.BlockSequence(), concl, cur
            if type(code_sequence[-1]) is ccb.While:
                code_sequence[-1].block = upper_tab
        else:
            block, l, concl, cur = read_line(code, l-spaces, version, tab)
            if concl != CompilerConclusion(0):
                return 0, ccb.BlockSequence(), concl, cur
            code_sequence.add(block)
    return l, code_sequence, CompilerConclusion(0), None

def read_line(code: str, startl: int, version: int, tab: int = 0):
    end = len(code)
    l = startl
    brackets = {'r': 0, # round
                's': 0, # square
                'c': 0, # curly
                'q': 0, # quotemarks
                't': False} # quotemarks type (False - ", True - ')

    l, write, concl, cur = split_args2(code, l)
    if not correct_concl(concl): return None, 0, concl, cur
    block = definer(write)
    return block, l, CompilerConclusion(0), None

def definer(parts: list[str]) -> (ccb.Block, CompilerConclusion, (CompilerCursor | None)):
    if len(parts) == 1:
        parts = parts[0]
        if (ind := '=' in parts) != -1: # SETVAR
            return definer_setvar([parts[:ind], parts[ind:ind+1], parts[ind+1:]])
        else:
            return ccb.Block(ccb.Global.UNKNOWNBLOCK)
    else:
        if '=' == parts[1]: # SETVAR
            return definer_setvar(parts)
        else:
            return ccb.Block(ccb.Global.UNKNOWNBLOCK)

def definer_setvar(parts: list[str]) -> (ccb.Block, CompilerConclusion, (CompilerCursor | None)):
    w, concl, cur = value_determinant(parts[0:1])
    if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
    r, concl, cur = value_determinant(parts[2:])
    if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
    return ccb.Block(ccb.Global.SETVAR, w, r)

def complex_determinant(codeparts: list[str]) -> (ccb.Value, CompilerConclusion, (CompilerCursor | None)):
    joined = ''.join(codeparts)
    if any(m in joined for m in SET_MO): #any(x in SET_MO for x in codeparts): # math
        inp = []
        for part in codeparts:
            write, concl, cur = split_args3(part, *SET_MO)
            if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
            inp.extend(write)
        return math_resolver(inp)

def simple_determinant(codepart: str) -> (ccb.Value, CompilerConclusion, (CompilerCursor | None)):
    if codepart[0] == '_': # localvar
        return ccb.Value(ccb.Global.LOCALVAR, codepart[1:]), CompilerConclusion(0), None
    elif codepart[0] == ':': # function
        l0, l1, w, concl, cur = cep.string_embedded_brackets(codepart, 1, '()')
        if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
        getargs, concl, cur = split_args3(codepart[l0+1:l1-1], ',')
        if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
        args = []
        for v in getargs[::2]:
            _, sv, concl, cur = split_args2(v, 0)
            if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
            nv, concl, cur = value_determinant(sv)
            if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
            args.append(nv)
        return ccb.Value(ccb.Global.FUNC, codepart[1:l0], CoreFuncs, args), CompilerConclusion(0), None
    elif codepart.isdigit():
        return ccb.Value(ccb.Global.FIXEDVAR, int(codepart)), CompilerConclusion(0), None
    elif codepart.replace('.', '', 1).isdigit():
        return ccb.Value(ccb.Global.FIXEDVAR, float(codepart)), CompilerConclusion(0), None
    elif codepart[0] in '"\'':
        st = cep.EOC_index[codepart[0]]
        l0, l1, write, concl, cur = cep.string_only_embedded(codepart, 0, st)
        if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
        return ccb.Value(ccb.Global.FIXEDVAR, write, CompilerConclusion(0), None)
    else:
        return ccb.Value(ccb.Global.EMPTY), CompilerConclusion(205), None

def value_determinant(codeparts: list[str]) -> (ccb.Value, CompilerConclusion, (CompilerCursor | None)):
    if len(codeparts) == 1:
        return simple_determinant(codeparts[0])
    else:
        return complex_determinant(codeparts)

def math_resolver(allparts: list[str]) -> (ccb.Value, CompilerConclusion, (CompilerCursor | None)):
    for mop in MO:
        for mos in mop:
            try:
                l = allparts.index(mos)
                vd1, concl, cur = value_determinant(allparts[:l])
                if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
                vd2, concl, cur = value_determinant(allparts[l+1:])
                if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
                args = [vd1, vd2]
                return ccb.Value(ccb.Global.FUNC, {'+':'add', '-':'sub', '*':'mul', '/':'div'}[mos], CoreFuncs, args), CompilerConclusion(0), None
            except ValueError:
                continue

class CoreFuncs:
    @staticmethod
    def add(data, a, b):
        return a.read(data) + b.read(data)
    @staticmethod
    def sub(data, a, b):
        return a.read(data) - b.read(data)
    @staticmethod
    def mul(data, a, b):
        return a.read(data) * b.read(data)
    @staticmethod
    def div(data, a, b):
        return a.read(data) / b.read(data)
    # @staticmethod
    # def getcell(data, x, y):
    #     cell = data.board[y][x]
    #     return cell.code
    # @staticmethod
    # def setcell(data, x, y, cell):
    #     data.orders.append(Order(Order.SET_CELL), x, y, cell)