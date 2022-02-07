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

def get(code: str):
    ret = {'version': 0,
           'type': 'CELL',
           'name': 'Cell',
           'desc': 'No description given.',
           'notexture': [255, 255, 255],
           'localization': {},
           'script': {'create': '',
                      'step': ''}}

    l = 0
    wstart = 0
    while l < len(code):
        if code[l:l+7] == 'VERSION':
            l += 7
            while code[l] == ' ':
                l += 1
            write = ''
            while code[l] != '\n':
                write += code[l]
                l += 1
            ret['version'] = int(write)

        elif code[l:l+4] == 'CELL':
            l += 4
            ret['type'] = 'CELL'
            write_to = False
            while code[l] != '\n':
                while code[l] != '"':
                    l += 1
                i0, i1, string = first_string(code, l)
                l = i1
                if not write_to:
                    ret['name'] = string
                    write_to = True
                else:
                    ret['desc'] = string

        elif code[l:l+9] == 'NOTEXTURE':
            l += 9
            write = ''
            writeind = 0
            while code[l] != '\n':
                if code[l] == ' ':
                    if write != '':
                        ret['notexture'][writeind] = int(float(write))
                        writeind += 1
                        write = ''
                else:
                    write += code[l]
                l += 1
            if write != '':
                ret['notexture'][writeind] = int(float(write))

        if code[l:l+12] == 'LOCALIZATION':
            l += 12
            while code[l] != '\n':
                l += 1
            l += 1
            while code[l:l+4] == '    ':
                l += 4
                lang = ''
                name = ''
                desc = ''
                while code[l] != ' ':
                    lang += code[l]
                    l += 1
                l += 1
                writeto = False
                while l < len(code) and code[l] != '\n':
                    while code[l] != '"':
                        l += 1
                    i0, i1, string = first_string(code, l)
                    l = i1
                    if not writeto:
                        name = string
                        writeto = True
                    else:
                        desc = string
                ret['localization'][lang] = {'name': name, 'desc': desc}


        l += 1

    return ret