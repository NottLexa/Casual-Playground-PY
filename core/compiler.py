from typing import Union

def first_string(code: str, start: int):
    indexes = [-1, -1]
    l = start
    write = ''
    qmcount = 0
    while (l < len(code)) and (qmcount < 2):
        if code[l] == '"':
            indexes[qmcount] = l
            qmcount += 1
        elif qmcount == 1:
            if code[l] == '\\':
                if code[l:l+2] == '\\"':
                    write += '"'
                    l += 1
                elif code[l:l+2] == '\\\\':
                    write += '\\'
                    l += 1
            else:
                write += code[l]
        l += 1
    return indexes[0], indexes[1]+1, write

def split_args1(code: str, start: int = None, end: Union[int, str] = None):
    newlinestop = False
    if start is None:
        start = 0
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
            i0, i1, string = first_string(code, l)
            l = i1 - 1
            write += f'"{string}"'
        else:
            write += code[l]
        l += 1

    if write != '':
        args.append(write)

    return args

def split_args2(code: str, start: int = None):
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
            i0, i1, string = first_string(code, l)
            l = i1 - 1
            write += f'"{string}"'
        else:
            write += code[l]
        l += 1

    if write != '':
        args.append(write)

    return end, args

def get(code: str):
    l = 0
    if code[l:l+7] == 'VERSION':
        l += 7
        while code[l] == ' ':
            l += 1
        write = ''
        while code[l] != '\n':
            write += code[l]
            l += 1

    version = int(write)

    if version == 1:
        return get_version1(code, l)

def get_version1(code: str, start: int, end: int = None):
    if end is None:
        end = len(code)
    else:
        end = min(end, len(code))

    ret = {'version': 0,
           'type': 'CELL',
           'name': 'Cell',
           'desc': 'No description given.',
           'notexture': [255, 255, 255],
           'localization': {},
           'script': {'create': '',
                      'step': ''}}

    l = start
    wstart = 0
    while l < end:
        if code[l:l+4] == 'CELL':
            l += 4
            ret['type'] = 'CELL'

            write = split_args1(code, l, '\n')
            if len(write) > 0:
                ret['name'] = eval(write[0])
            if len(write) > 1:
                ret['desc'] = eval(write[1])

        elif code[l:l+9] == 'NOTEXTURE':
            l += 9

            l, write = split_args2(code, l)
            l += 1
            if len(write) > 0:
                ret['notexture'][0] = int(float(write[0]))
            if len(write) > 1:
                ret['notexture'][1] = int(float(write[1]))
            if len(write) > 2:
                ret['notexture'][2] = int(float(write[2]))

        elif code[l:l+12] == 'LOCALIZATION':
            l += 12
            while code[l] != '\n':
                l += 1
            l += 1
            while code[l:l+4] == '    ':
                l += 4
                l, (lang, name, desc) = split_args1(code, l)
                l += 1
                ret['localization'][lang] = {'name': eval(name), 'desc': eval(desc)}

        l += 1

    return ret

class CompilerConclusion:
    ids = [
        # 0-- / Basic problems
        ['Not a .mod file',
         'Version of code is not stated in the start of .mod file (might be unreadable encoding, use UTF-8)'],
        # 1-- / Syntax error
        [],
    ]

    @staticmethod
    def get_description(code: int) -> str:
        group, errid = divmod(code, 100)
        if group in CompilerConclusion.ids and errid in CompilerConclusion.ids[group]:
            return CompilerConclusion.ids[group][errid]
        else:
            return 'Unknown Code'

    def __init__(self, code: int):
        self.code = code
    def __repr__(self) -> str:
        return f'<CompCon:{self.code}>'
    def __str__(self) -> str:
        return f'<Compiler conclusion #{self.code}>'
    def full_conclusion(self) -> str:
        return f'<Compiler conclusion with ID: {self.code}\n' + CompilerConclusion.get_description(404) + '>'