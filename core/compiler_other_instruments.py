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
            print(l)
            i0, i1, string, concl, cur = cep.string_embedded(code, l, cep.DOUBLEQUOTEMARK)
            if concl != CompilerConclusion(0):
                return concl, cur
            l = i1 - 1
            write += string
        else:
            write += code[l]
        l += 1

    if write != '':
        args.append(write)

    return args, None

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
        elif code[l] == '"':
            i0, i1, string, concl, cur = cep.string_embedded(code, l, cep.DOUBLEQUOTEMARK)
            if concl != CompilerConclusion(0):
                return 0, concl, cur
            l = i1 - 1
            write += string
        else:
            write += code[l]
        l += 1

    if write != '':
        args.append(write)

    return end+1, args, None