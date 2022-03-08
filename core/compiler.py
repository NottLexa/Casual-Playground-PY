from typing import Union

LAST_COMPILER_VERSION = 1

class CompilerCursor:
    def __init__(self, codetxt: str = '', startline: int = 0, endline: int = None):
        startindex = 0
        for i in range(startline):
            startindex = codetxt.find('\n', startindex)+1

        endindex = codetxt.find('\n', startindex)
        if endline is not None:
            for i in range(endline):
                endindex = codetxt.find('\n', endindex+1)

        self.si = startindex
        self.ei = endindex
        self.txt = codetxt[startindex:endindex]

    def __repr__(self):
        return f'CompilerCursor[{self.si}:{self.ei}]'
    def __str__(self):
        return f'CompilerCursor[{self.si}:{self.ei}]: "{self.txt}"'
    def start(self):
        return self.si
    def end(self):
        return self.ei
    def string(self):
        return self.txt

class CompilerConclusion:
    ids = [
        # 0-- / Success conclusions
        list({
            0: 'Success',
            1: 'Success (warning, outdated version of mod)',
        }.values()),
        # 1-- / Format errors
        list({
            0: 'Not a .mod file',
            1: 'Empty file',
            2: 'Version of code is not stated in the start of .mod file (might be unreadable encoding, use UTF-8)',
            3: 'Unknown version of mod',
        }.values()),
        # 2-- / Syntax error
        list({

        }.values()),
    ]

    @staticmethod
    def get_description(code: int) -> str:
        group, errid = divmod(code, 100)
        if group in CompilerConclusion.ids and errid in CompilerConclusion.ids[group]:
            return CompilerConclusion.ids[group][errid]
        else:
            return 'Unknown Code'

    def __init__(self, conclusion_code: int):
        self.code = conclusion_code
    def __repr__(self) -> str:
        return f'<CompCon[{self.code}]>'
    def __str__(self) -> str:
        return f'<CompilerConclusion: {self.code}>'
    def full_conclusion(self) -> str:
        return f'< CompilerConclusion with ID {self.code}\n  ---\n  ' + CompilerConclusion.get_description(self.code) + ' >'
    def short_conclusion(self) -> str:
        return f'<CompilerConclusion with ID {self.code}: {CompilerConclusion.get_description(self.code)}>'

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

get_hinting = (list, CompilerConclusion, (CompilerCursor | None))

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

    if version == 1:
        ret = list(get_version1(code, l))
    else:
        return {}, CompilerConclusion(3), CompilerCursor(code, 0, 0)

    if ret[1] == CompilerConclusion(0) and version != LAST_COMPILER_VERSION:
        ret[1] = CompilerConclusion(1)
    return ret

def get_version1(code: str, start: int, end: int = None) -> get_hinting:
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

    return ret, CompilerConclusion(0), None