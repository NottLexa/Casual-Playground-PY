from core.compiler_conclusions_cursors import CompilerConclusion

ROUND, SQUARE, CURLY, DOUBLEQUOTEMARK, SINGLEQUOTEMARK = range(5)
QUOTEMARK = DOUBLEQUOTEMARK
EOC = EMBEDDED_OPENING_CHARS = '([{"\''
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
                    return 0, 0, '', CompilerConclusion(202)
            else:
                write += code[l]
                l += 1
        if count >= 2:
            break
    else:
        return 0, 0, '', CompilerConclusion(201)
    return indexes[0], indexes[1]+1, write, CompilerConclusion(0)

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
                    l0, l1, add, concl = string_embedded(code, l, EOC.index(code[l]))
                    if concl != CompilerConclusion(0):
                        return 0, 0, '', concl
                    write += add
                    l = l1
            else:
                l0, l1, add, concl = string_embedded(code, l, EOC.index(code[l]))
                if concl != CompilerConclusion(0):
                    return 0, 0, '', concl
                write += add
                l = l1
        elif code[l] == sepsym[1]:
            if opened == True:
                indexes[1] = l
                write += code[l]
                break
            else:
                return 0, 0, '', CompilerConclusion(201)
        else:
            write += code[l]
            l += 1
    else:
        return 0, 0, '', CompilerConclusion(201)
    return indexes[0], indexes[1]+1, write, CompilerConclusion(0)

def string_embedded(code: str, start: int, separationtype: int):
    sepsym = ['()', '[]', '{}', '"', "'"][separationtype]
    type = (separationtype in [DOUBLEQUOTEMARK, SINGLEQUOTEMARK]) # False - brackets, True - quote marks
    if type:
        return string_embedded_quotemark(code, start, sepsym)
    else:
        return string_embedded_brackets(code, start, sepsym)

def string_only_embedded(code: str, start: int, separationtype: int):
    ret = string_embedded(code, start, separationtype)
    if ret[3] == CompilerConclusion(0):
        return ret[0], ret[1], ret[2][1:-1], ret[3], EOC.index(ret[2][0])
    else:
        return ret