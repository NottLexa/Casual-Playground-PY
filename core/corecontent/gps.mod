VERSION 1

CELL "GPS" "Writes down its coordinates."

NOTEXTURE 51 102 0

LOCALIZATION
    rus "GPS" "Записывает свои координаты."

SCRIPT CREATE
    _x = 0
    _y = 0

SCRIPT STEP
    _x = __X
    _y = __Y