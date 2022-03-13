# Casual Playground Compiler - version 1
#
# Hello world!

from core.compiler_other_instruments import *
import core.compiler_code_blocks as ccb
import core.compiler_line_definer as cld

def chapter_cell(code: str, startl: int):
    l = startl
    ret = {}
    if code[l:l+4] == 'CELL':
        l += 4
        ret['type'] = 'CELL'

        write = split_args1(code, l, '\n')
        print(write)
        if type(write) is CompilerConclusion:
            return 0, {}, write, None
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

        l, write = split_args2(code, l)
        if type(write) is CompilerConclusion:
            return 0, {}, write, None
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
            l, write = split_args2(code, l)
            if type(write) is CompilerConclusion:
                return 0, {}, write, None
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
        while code[l] != ' ':
            write += code[l]
        script_type = write.lower()
        while code[l] != '\n':
            l += 1
        l += 1
        l, ret_script[script_type] = read_code(code, l, tab=1, version=version)
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
    code_sequence = ccb.BlockSentence()
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
            l, upper_tab = read_code(code, l-spaces, tab+1, version)
            if type(code_sequence[-1]) is ccb.While:
                code_sequence[-1].block = upper_tab
        else:
            block, l = read_line(code, l-spaces, version, tab)
            code_sequence.add(block)
    return l+1, code_sequence

def read_line(code: str, startl: int, version: int, tab: int = 0):
    end = len(code)
    l = startl
    brackets = {'r': 0, # round
                's': 0, # square
                'c': 0, # curly
                'q': 0, # quotemarks
                't': False} # quotemarks type (False - ", True - ')
    cond = lambda l: cond1(l) and cond2(l)
    cond1 = lambda l: l < end
    cond2 = lambda l: cond2a() and cond2b(l)
    cond2a = lambda: brackets['r'] == brackets['s'] == brackets['c'] == brackets['q'] == 0
    cond2b = lambda l: code[l] == '\n'

    l, write = split_args2(code, l)
    block = cld.definer(write, version)
    return block, l