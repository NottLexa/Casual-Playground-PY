# Casual Playground Compiler - version 1
#
# Hello world!

from .compiler_other_instruments import *
from . import compiler_code_blocks as ccb
from . import compiler_block_definers as cbd

class LineType:
    ADDNEW, ADDCONDBLOCK, ADDFALSEBLOCK = range(3)

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
        if concl != CompilerConclusion(0): return 0, {}, concl, cur
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
            return 0, ccb.BlockSequence(), CompilerConclusion(206), CompilerCursor(code, l)
        else:
            linetype, block, l, concl, cur = read_line(code, l-spaces, version, tab)
            if not correct_concl(concl): return 0, ccb.BlockSequence(), concl, cur
            match linetype:
                case LineType.ADDNEW:
                    code_sequence.add(block)
                case LineType.ADDCONDBLOCK:
                    if isinstance(code_sequence[-1], ccb.Gate):
                        code_sequence[-1].cb.append(block)
                    else:
                        return 0, ccb.BlockSequence(), CompilerConclusion(207), None
                case LineType.ADDFALSEBLOCK:
                    if isinstance(code_sequence[-1], ccb.Gate):
                        if code_sequence[-1].fb is None:
                            code_sequence[-1].fb = block
                        else:
                            return 0, ccb.BlockSequence(), CompilerConclusion(209), None
                    else:
                        return 0, ccb.BlockSequence(), CompilerConclusion(208), None
                case _:
                    code_sequence.add(block)
    return l-spaces, code_sequence, CompilerConclusion(0), None

def read_line(code: str, startl: int, version: int, tab: int = 0):
    end = len(code)
    l = startl

    l, write, concl, cur = split_args2(code, l)
    if not correct_concl(concl): return LineType.ADDNEW, ccb.Block(ccb.Global.UNKNOWNBLOCK), 0, concl, cur
    if write[0] == 'IF':
        value, concl, cur = cbd.value_determinant(write[1:])
        if not correct_concl(concl): return ccb.Block(ccb.Global.UNKNOWNBLOCK), 0, concl, cur
        l, seq, concl, cur = read_code(code, l, version, tab+1)
        return LineType.ADDNEW, ccb.Gate([[value, seq]]), l, concl, cur
    elif write[0] == 'ELSEIF':
        value, concl, cur = cbd.value_determinant(write[1:])
        if not correct_concl(concl): return ccb.Block(ccb.Global.UNKNOWNBLOCK), 0, concl, cur
        l, seq, concl, cur = read_code(code, l, version, tab+1)
        return LineType.ADDCONDBLOCK, [value, seq], l, concl, cur
    elif write[0] == 'ELSE':
        l, seq, concl, cur = read_code(code, l, version, tab+1)
        return LineType.ADDFALSEBLOCK, seq, l, concl, cur
    else:
        block, concl, cur = cbd.definer(write)
        return LineType.ADDNEW, block, l, concl, cur