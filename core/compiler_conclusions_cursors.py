class CompilerCursor:
    def __init__(self, codetxt: str = '', index: int = 0):
        start = codetxt.rfind('\n', 0, index)
        end = codetxt.find('\n', index)

        self.si = start+1
        self.ei = end
        self.txt = codetxt[self.si:self.ei]

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
            0: 'Syntax error: no specified reason',
            1: 'Syntax error: unclosed brackets or quote marks',
            2: 'Syntax error: impossible usage of backslash in quote marks',
            3: 'Syntax error: unexpected symbol/expression',
            4: 'Syntax error: unclosed math operation',
            5: 'Syntax error: unidentifiable value'
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