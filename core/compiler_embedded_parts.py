from core.compiler_conclusions_cursors import *

ROUND, SQUARE, CURLY, DOUBLEQUOTEMARK, SINGLEQUOTEMARK = range(5)
QUOTEMARK = DOUBLEQUOTEMARK
EOC = EMBEDDED_OPENING_CHARS = '([{"\''
EOC_index = {EOC[x]:x for x in range(len(EOC))}
SET_EOC = set(EOC)
BS = '\\'

def string_embedded_quotemark(code: str, start: int, sepsym: str):
    indexes = [-1, -1]
    l = start
    write = ''
    count = 0
    while (l < len(code)):
        if code[l] == sepsym:
            indexes[count] = l
            count += 1
        if count > 0:
            if code[l] == BS:
                if code[l + 1] == BS:
                    write += BS
                    l += 2
                elif code[l + 1] == sepsym:
                    write += sepsym
                    l += 2
                else:
                    return 0, 0, '', CompilerConclusion(202), CompilerCursor(code, l)
            else:
                write += code[l]
                l += 1
        if count >= 2:
            break
    else:
        return 0, 0, '', CompilerConclusion(201), CompilerCursor(code, start)
    return indexes[0], indexes[1]+1, write, CompilerConclusion(0), None

def string_embedded_brackets(code: str, start: int, sepsym: str):
    indexes = [-1, -1]
    l = start
    write = ''
    count = 0
    opened = False
    while (l < len(code)):
        if code[l] in SET_EOC:
            if code[l] == sepsym[0]:
                if not opened:
                    indexes[0] = l
                    opened = True
                    write += code[l]
                    l += 1
                else:
                    _, l, add, concl, cur = string_embedded(code, l, EOC_index[code[l]])
                    if not correct_concl(concl):
                        return 0, 0, '', concl, cur
                    write += add
            else:
                _, l, add, concl, cur = string_embedded(code, l, EOC_index[code[l]])
                if not correct_concl(concl):
                    return 0, 0, '', concl, cur
                write += add
        elif code[l] == sepsym[1]:
            if opened == True:
                indexes[1] = l
                write += code[l]
                break
            else:
                return 0, 0, '', CompilerConclusion(201), CompilerCursor(code, l)
        else:
            write += code[l]
            l += 1
    else:
        return 0, 0, '', CompilerConclusion(201), CompilerCursor(code, start)
    return indexes[0], indexes[1]+1, write, CompilerConclusion(0), None

def string_embedded(code: str, start: int, separationtype: int):
    sepsym = ['()', '[]', '{}', '"', "'"][separationtype]
    type = (separationtype in [DOUBLEQUOTEMARK, SINGLEQUOTEMARK]) # False - brackets, True - quote marks
    if type:
        return string_embedded_quotemark(code, start, sepsym)
    else:
        return string_embedded_brackets(code, start, sepsym)

def string_only_embedded(code: str, start: int, separationtype: int):
    ret = string_embedded(code, start, separationtype)
    if not correct_concl(ret[3]):
        return ret[0], ret[1], ret[2][1:-1], ret[3], EOC_index[ret[2][0]], None
    else:
        return ret