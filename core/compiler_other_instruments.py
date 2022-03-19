import core.compiler_embedded_parts as cep
from core.compiler_conclusions_cursors import *

def split_args1(code: str, start: int = 0, end: int | str = None):
    newlinestop = False
    if end is None:
        end = len(code)
    elif end == '\n':
        newlinestop = True
        end = len(code)
    else:
        end = min(end, len(code))

    args = []

    write = ''

    l = start
    while l < end:
        if newlinestop and code[l] == '\n':
            break
        if code[l] == ' ' or code[l] == '\n' or code[l] == '\t':
            if write != '':
                args.append(write)
                write = ''
        elif code[l] == '"':
            i0, i1, string, concl, cur = cep.string_embedded(code, l, cep.DOUBLEQUOTEMARK)
            if concl != CompilerConclusion(0):
                return [], concl, cur
            l = i1 - 1
            write += string
        else:
            write += code[l]
        l += 1

    if write != '':
        args.append(write)

    return args, CompilerConclusion(0), None

def split_args2(code: str, start: int = 0):
    end = len(code)
    args = []
    write = ''
    l = start
    while l < end:
        if code[l] == '\n':
            end = l
            break
        if code[l] == ' ' or code[l] == '\n' or code[l] == '\t':
            if write != '':
                args.append(write)
                write = ''
            l += 1
        elif code[l] in cep.SET_EOC:
            i0, i1, string, concl, cur = cep.string_embedded(code, l, cep.EOC_index[code[l]])
            if not correct_concl(concl):
                return 0, [], concl, cur
            l = i1
            write += string
        else:
            write += code[l]
            l += 1

    if write != '':
        args.append(write)

    return end+1, args, CompilerConclusion(0), None

def split_args3(code: str, *splitters, start: int = 0, end: int = None):
    if end is None:
        end = len(code)

    splitters = sorted(splitters, reverse=True)

    ret = ['']

    l = start
    while l < end:
        for spl in splitters:
            if code[l:l+(len(spl))] == spl:
                if ret[-1] == '':
                    ret.pop(-1)
                ret.extend((spl, ''))
                l += len(spl)
                break
        else:
            if code[l] in cep.SET_EOC:
                l0, l1, write, concl, cur = cep.string_embedded(code, l, cep.EOC_index[code[l]])
                if not correct_concl(concl):
                    return [], concl, cur
                ret[-1] += write
                l = l1
            else:
                ret[-1] += code[l]
                l += 1
    if ret[-1] == '':
        ret.pop(-1)
    return ret, CompilerConclusion(0), None