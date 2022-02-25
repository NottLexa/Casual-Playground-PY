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

            write = split_args1(code, l, '\n')
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
                lang, name, desc = split_args1(code, l, '\n')
                ret['localization'][lang] = {'name': eval(name), 'desc': eval(desc)}

        l += 1

    return ret