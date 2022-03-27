from .compiler_core_functions import *
from .compiler_other_instruments import *
from . import compiler_code_blocks as ccb
from ... import compiler_string_constants as csc

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
    s_codepart = set(codepart)
    numeric = s_codepart.issubset(csc.s_digdot)
    if numeric and ('.' not in s_codepart):
        return ccb.Value(ccb.Global.FIXEDVAR, int(codepart)), CompilerConclusion(0), None
    elif numeric and (codepart.count('.') == 1):
        return ccb.Value(ccb.Global.FIXEDVAR, float(codepart)), CompilerConclusion(0), None
    else:
        namable = lambda x: (set(x).issubset(csc.s_nam)) and (x[0] not in csc.s_dig)
        name1 = codepart[1:]
        name2 = codepart[2:]
        if codepart[:2] == '__' and namable(name2): # techvar (read-only)
            return ccb.Value(ccb.Global.TECHVAR, name2), CompilerConclusion(0), None
        elif codepart[0] == '_' and namable(name1): # localvar
            return ccb.Value(ccb.Global.LOCALVAR, name1), CompilerConclusion(0), None
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
        elif codepart[0] in '"\'':
            st = cep.EOC_index[codepart[0]]
            l0, l1, write, concl, cur = cep.string_only_embedded(codepart, 0, st)
            if not correct_concl(concl): return ccb.Value(ccb.Global.EMPTY), concl, cur
            return ccb.Value(ccb.Global.FIXEDVAR, write, CompilerConclusion(0), None)
        else:
            return ccb.Value(ccb.Global.EMPTY), CompilerConclusion(301), None

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