from ... import compiler_task_types as ctt

class CoreFuncs:
    @staticmethod
    def add(cell, a, b):
        '''Returns A + B.'''
        return a.read(cell) + b.read(cell)
    @staticmethod
    def sub(cell, a, b):
        '''Returns A - B.'''
        return a.read(cell) - b.read(cell)
    @staticmethod
    def mul(cell, a, b):
        '''Returns A * B.'''
        return a.read(cell) * b.read(cell)
    @staticmethod
    def div(cell, a, b):
        '''Returns A / B.'''
        return a.read(cell) / b.read(cell)
    @staticmethod
    def getcell(cell, x, y):
        '''Gets CellID of cell on board by coordinates X, Y.'''
        cell = cell.board[y.read(cell)][x.read(cell)]
        return cell.cellid
    @staticmethod
    def setcell(cell, x, y, cellid):
        '''Sends an order to change cell on board with coordinates X, Y to cell with given CellID.'''
        cell.tasks.append([ctt.SET_CELL, x.read(cell), y.read(cell), cellid.read(cell)])
    @staticmethod
    def eq(cell, a, b):
        '''Returns True if A equals B, False otherwise.'''
        return a.read(cell) == b.read(cell)
    @staticmethod
    def ne(cell, a, b):
        '''Returns True if A doesn't equals B, False otherwise.'''
        return a.read(cell) != b.read(cell)
    @staticmethod
    def ge(cell, a, b):
        '''Returns True if A greater/equals B, False otherwise.'''
        return a.read(cell) >= b.read(cell)
    @staticmethod
    def gt(cell, a, b):
        '''Returns True if A greater than B, False otherwise.'''
        return a.read(cell) > b.read(cell)
    @staticmethod
    def le(cell, a, b):
        '''Returns True if A less/equals B, False otherwise.'''
        return a.read(cell) <= b.read(cell)
    @staticmethod
    def lt(cell, a, b):
        '''Returns True if A less than B, False otherwise.'''
        return a.read(cell) < b.read(cell)
    @staticmethod
    def reply(cell, string):
        '''Sends a text reply to console logger.'''
        cell.reply(0, string.read(cell))