class CodeBlock:
    def __init__(self, parts):
        self.parts = parts
    def exec(self):
        for p in self.parts:
            p.exec()