import core.compiler_code_blocks as ccb

def definer(parts: list[str], whatisit_version: int):
    if whatisit_version == 1:
        whatisit = whatisit_version1
    else:
        whatisit = whatisit_version1
    if len(parts) == 3:
        if parts[1] == '=':
            valuew = whatisit(parts[0])
            valuer = whatisit(parts[2])
            return ccb.Block(ccb.Global.SETVAR, valuew, valuer)

def whatisit_version1(codepart):
    if codepart[0] == '_': # localvar
        return ccb.Value(ccb.Global.LOCALVAR, codepart[1:])