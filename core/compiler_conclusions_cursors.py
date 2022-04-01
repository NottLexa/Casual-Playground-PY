class CompilerCursor:
    def __init__(self, codetxt: str | None = None, *indexes: int):
        if isinstance(codetxt, str):
            if len(indexes) == 0:
                self.txt = codetxt
            else:
                if len(indexes) == 1:
                    self.sl = codetxt.rfind('\n', 0, indexes[0]) + 1
                    self.el = codetxt.find('\n', indexes[0])
                    self.sh = 0
                    self.eh = -1
                elif len(indexes) == 2:
                    self.sl = indexes[0]
                    self.el = indexes[1]
                    self.sh = 0
                    self.eh = -1
                elif len(indexes) == 3:
                    self.sl = indexes[0]
                    self.el = indexes[1]
                    self.sh = indexes[2]
                    self.eh = indexes[2]
                elif len(indexes) == 4:
                    self.sl = indexes[0]
                    self.el = indexes[1]
                    self.sh = indexes[2]
                    self.eh = indexes[3]
                self.txt = codetxt[self.sl:self.el]
        else: # if codetxt is None
            self.sl = 0
            self.el = -1
            self.sh = 0
            self.eh = -1
            self.txt = '<Not specified where>'

    def __repr__(self):
        return f'CompilerCursor[{self.sl}:{self.el}]'
    def __str__(self):
        return f'CompilerCursor[{self.sl}:{self.el}]: "{self.txt}"'
    def start(self):
        return self.sl
    def end(self):
        return self.el
    def string(self):
        return self.txt
    def highlight(self, sym: str = 'v'):
        return ((self.sl-self.sh)*' ')+((self.eh-self.sh+1)*sym)

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
            0: 'Syntax error: no specified reason',
            1: 'Syntax error: unclosed brackets or quote marks',
            2: 'Syntax error: impossible usage of backslash in quote marks',
            3: 'Syntax error: unexpected symbol/expression',
            4: 'Syntax error: unclosed math operation',
            5: 'Syntax error: undefinable code line',
            6: 'Syntax error: encountered higher tab where it mustn\'t be',
            7: 'Syntax error: unexpected ELSEIF statement (maybe you put something between IF and ELSEIF?)',
            8: 'Syntax error: unexpected ELSE statement (maybe you put something between IF and ELSE?)',
            9: 'Syntax error: unexpected ELSE statement (maybe you put ELSE twice?)',
        }.values()),
        # 3-- / Value error
        list({
            0: 'Value error: no specified reason',
            1: 'Value error: unidentifiable value',
            2: 'Value error: trying to write read-only variable',
            3: 'Value error: trying to read non-existent variable',
            4: 'Value error: put value is of incorrect type'
        }.values()),
        # 4-- / Runtime error
        list({
            0: 'Runtime error: no specified reason',
        }.values()),
    ]

    @staticmethod
    def get_description(code: int) -> str:
        group, errid = divmod(code, 100)
        if group < len(CompilerConclusion.ids) and errid < len(CompilerConclusion.ids[group]):
            return CompilerConclusion.ids[group][errid]
        else:
            return 'Unknown Code'

    def description(self) -> str:
        group, errid = divmod(self.code, 100)
        if group < len(CompilerConclusion.ids) and errid < len(CompilerConclusion.ids[group]):
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
    def __eq__(self, other):
        try:
            return self.code == other.code
        except AttributeError:
            return False
    def __ne__(self, other):
        try:
            return self.code != other.code
        except AttributeError:
            return False

get_hinting = (dict, CompilerConclusion, (CompilerCursor | None))

correct_concl = lambda concl: concl == CompilerConclusion(0)