VERSION 1

CELL "GOL: Dead cell" "A dead cell from John Conway's Game of Life."

NOTEXTURE 238 238 238

LOCALIZATION
    rus "ИЖ: Мёртвая клетка" "Мёртвая клетка из игры \"Жизнь\" Джона Конвея."

SCRIPT STEP
    _counter = 0
    _cx = -1
    WHILE (_cx <= 1)
        _cy = -1
        WHILE (_cy <= 1)
            IF :not(:and(_cx == 0, _cy == 0))
                IF (:getcell(:clamp(__X+_cx, 0, BOARDWIDTH-1), :clamp(__Y+_cy, 0, BOARDHEIGHT-1)) == #gameoflife_live)
                    _counter = _counter + 1
            _cy = _cy + 1
        _cx = _cx + 1
    IF :not(:or(_counter == 2, _counter == 3))
        :setcell(__X, __Y, #gameoflife_dead)