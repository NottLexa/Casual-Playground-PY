from ... import compiler_task_types as ctt

class CoreFuncs:
    @staticmethod
    def add(data, a, b):
        return a.read(data) + b.read(data)
    @staticmethod
    def sub(data, a, b):
        return a.read(data) - b.read(data)
    @staticmethod
    def mul(data, a, b):
        return a.read(data) * b.read(data)
    @staticmethod
    def div(data, a, b):
        return a.read(data) / b.read(data)
    @staticmethod
    def getcell(data, x, y):
        cell = data.board[y.read(data)][x.read(data)]
        return cell.codeid
    @staticmethod
    def setcell(data, x, y, codeid):
        data.tasks.append([ctt.SET_CELL, x.read(data), y.read(data), codeid.read(data)])
    @staticmethod
    def eq(data, a, b):
        return a.read(data) == b.read(data)
    @staticmethod
    def ne(data, a, b):
        return a.read(data) != b.read(data)
    @staticmethod
    def ge(data, a, b):
        return a.read(data) >= b.read(data)
    @staticmethod
    def gt(data, a, b):
        return a.read(data) > b.read(data)
    @staticmethod
    def le(data, a, b):
        return a.read(data) <= b.read(data)
    @staticmethod
    def lt(data, a, b):
        return a.read(data) < b.read(data)