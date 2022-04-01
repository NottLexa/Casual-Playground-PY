from .compiler_value_determinants import *

def definer(parts: list[str]) -> (ccb.Block, CompilerConclusion, (CompilerCursor | None)):
    if len(parts) == 1:
        parts = parts[0]
        if (ind := parts.find('=')) != -1: # SETVAR
            return definer_setvar([parts[:ind], parts[ind:ind+1], parts[ind+1:]])
        elif parts[0] == ':': # RUNFUNC
            return definer_runfunc(parts)
        else:
            return ccb.Block(ccb.Global.UNKNOWNBLOCK), CompilerConclusion(205), CompilerCursor(None)
    else:
        if '=' == parts[1]: # SETVAR
            return definer_setvar(parts)
        else:
            return ccb.Block(ccb.Global.UNKNOWNBLOCK), CompilerConclusion(205), CompilerCursor(None)

def definer_setvar(parts: list[str]) -> (ccb.Block, CompilerConclusion, (CompilerCursor | None)):
    w, concl, cur = value_determinant(parts[0:1])
    if not correct_concl(concl): return ccb.Block(ccb.Global.UNKNOWNBLOCK), concl, cur
    r, concl, cur = value_determinant(parts[2:])
    if not correct_concl(concl): return ccb.Block(ccb.Global.UNKNOWNBLOCK), concl, cur
    return ccb.Block(ccb.Global.SETVAR, w, r), CompilerConclusion(0), CompilerCursor(None)

def definer_runfunc(string: str) -> (ccb.Block, CompilerConclusion, (CompilerCursor | None)):
    func, concl, cur = simple_determinant(string)
    if not correct_concl(concl): return ccb.Block(ccb.Global.UNKNOWNBLOCK), concl, cur
    return ccb.Block(ccb.Global.RUNFUNC, func), CompilerConclusion(0), CompilerCursor(None)