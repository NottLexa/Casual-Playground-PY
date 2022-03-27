from .compiler_core_functions import *
from .compiler_other_instruments import *
from . import compiler_code_blocks as ccb

MO = MATHOPERATORS = ['+-', '*/']
SET_MO = set(''.join(MO))

def complex_determinant(codeparts: list[str]) -> (ccb.Value, CompilerConclusion, (CompilerCursor | None)):
    joined = ''.join(codeparts)
    if any(m in joined for m in SET_MO): #any(x in SET_MO for x in codeparts): # math
        inp = []
        for part in codeparts:
            write, concl, cur = split_args3(part, *SET_MO)
            if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
            inp.extend(write)
        return math_resolver(inp)

def simple_determinant(codepart: str) -> (ccb.Value, CompilerConclusion, (CompilerCursor | None)):
    if codepart[0] == '_': # localvar
        return ccb.Value(ccb.Global.LOCALVAR, codepart[1:]), CompilerConclusion(0), None
    elif codepart[0] == ':': # function
        l0, l1, w, concl, cur = cep.string_embedded_brackets(codepart, 1, '()')
        if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
        getargs, concl, cur = split_args3(codepart[l0+1:l1-1], ',')
        if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
        args = []
        for v in getargs[::2]:
            _, sv, concl, cur = split_args2(v, 0)
            if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
            nv, concl, cur = value_determinant(sv)
            if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
            args.append(nv)
        return ccb.Value(ccb.Global.FUNC, codepart[1:l0], CoreFuncs, args), CompilerConclusion(0), None
    elif codepart.isdigit():
        return ccb.Value(ccb.Global.FIXEDVAR, int(codepart)), CompilerConclusion(0), None
    elif codepart.replace('.', '', 1).isdigit():
        return ccb.Value(ccb.Global.FIXEDVAR, float(codepart)), CompilerConclusion(0), None
    elif codepart[0] in '"\'':
        st = cep.EOC_index[codepart[0]]
        l0, l1, write, concl, cur = cep.string_only_embedded(codepart, 0, st)
        if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
        return ccb.Value(ccb.Global.FIXEDVAR, write, CompilerConclusion(0), None)
    else:
        return ccb.Value(ccb.Global.EMPTY), CompilerConclusion(205), None

def value_determinant(codeparts: list[str]) -> (ccb.Value, CompilerConclusion, (CompilerCursor | None)):
    if len(codeparts) == 1:
        return simple_determinant(codeparts[0])
    else:
        return complex_determinant(codeparts)

def math_resolver(allparts: list[str]) -> (ccb.Value, CompilerConclusion, (CompilerCursor | None)):
    for mop in MO:
        for mos in mop:
            try:
                l = allparts.index(mos)
                vd1, concl, cur = value_determinant(allparts[:l])
                if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
                vd2, concl, cur = value_determinant(allparts[l+1:])
                if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
                args = [vd1, vd2]
                return ccb.Value(ccb.Global.FUNC, {'+':'add', '-':'sub', '*':'mul', '/':'div'}[mos], CoreFuncs, args), CompilerConclusion(0), None
            except ValueError:
                continue