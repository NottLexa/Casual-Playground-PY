import pygame
import math
#from core import nle as engine
#from core import compiler as cpc
import core.nle as engine
import core.compiler as comp

#region [ИНИЦИАЛИЗАЦИЯ]

print('''

 _____                       _    ______ _                                             _ 
/  __ \\                     | |   | ___ \\ |                                           | |
| /  \\/ __ _ ___ _   _  __ _| |   | |_/ / | __ _ _   _  __ _ _ __ ___  _   _ _ __   __| |
| |    / _` / __| | | |/ _` | |   |  __/| |/ _` | | | |/ _` | '__/ _ \\| | | | '_ \\ / _` |
| \\__/\\ (_| \\__ \\ |_| | (_| | |   | |   | | (_| | |_| | (_| | | | (_) | |_| | | | | (_| |
 \\____/\\__,_|___/\\__,_|\\__,_|_|   \\_|   |_|\\__,_|\\__, |\\__, |_|  \\___/ \\__,_|_| |_|\\__,_|
                                                  __/ | __/ |                            
                                                 |___/ |___/                             
by:                                                                            version:
  Alexey Kozhanov                                                                      #3
                                                                               DVLP BUILD
''')

scale = 30
WIDTH, HEIGHT = 16*scale, 9*scale

screen = engine.Screen((WIDTH, HEIGHT), (WIDTH*2, HEIGHT*2), 0, True)
clock = pygame.time.Clock()
deltatime = 0
#endregion

#region [SETTINGS]
objdata = {}
with open('core/corecontent/grass.mod', encoding='utf8') as g:
    objdata['grass'] = comp.get(g.read())
idlist = ['grass']
print(objdata[idlist[0]])
board_width = 32
board_height = 32
linecolor_infield = 'gray10'
linecolor_outfield = 'gray40'
#endregion

#region [ENTITY]
#region [FIELD BOARD]
def FieldBoard_create(target):
    target.viewx = 0
    target.viewy = 0
    target.viewscale = 16
    target.keys = {'up': False,
                   'left': False,
                   'right': False,
                   'down': False}
    target.cameraspeed = 64
    target.board = [[0]*board_width for _ in range(board_height)]

def FieldBoard_step(target):
    target.viewx += deltatime * target.cameraspeed * (target.keys['right']-target.keys['left'])
    target.viewy += deltatime * target.cameraspeed * (target.keys['down']-target.keys['up'])

def FieldBoard_draw(target, surface: pygame.Surface):
    cellsize = target.viewscale+1
    sx, ox = divmod(-target.viewx, cellsize)
    sx = int(sx)
    lx = math.ceil(WIDTH/cellsize)
    sy, oy = divmod(-target.viewy, cellsize)
    sy = int(sy)
    ly = math.ceil(HEIGHT/cellsize)
    for ix in range(-1, lx):
        for iy in range(-1, ly):
            cellx = ox+(ix*cellsize)
            celly = oy+(iy*cellsize)
            if not (cellx+target.viewx < -1 or celly+target.viewy < -1
                 or cellx+target.viewx+cellsize > (cellsize*board_width)
                 or celly+target.viewy+cellsize > (cellsize*board_height)): # в пределах поля
                boardx, boardy = sx+ix, sy+iy
                celldata = objdata[idlist[target.board[boardy][boardx]]]
                pygame.draw.rect(surface, celldata['notexture'], (cellx, celly, target.viewscale, target.viewscale))

    for ix in range(-1, lx):
        linex = ox+(ix*cellsize)
        starty = engine.clamp(0, -target.viewy, -target.viewy+(cellsize*board_height))
        endy = engine.clamp(HEIGHT, -target.viewy, -target.viewy+(cellsize*board_height))
        if not (linex+target.viewx < 0 or linex+target.viewx > (cellsize*board_width)): # в пределах поля
            pygame.draw.line(surface, linecolor_infield, (linex-1, starty-1), (linex-1, endy-1))
            if (starty-2 > 0):
                pygame.draw.line(surface, linecolor_outfield, (linex-1, 0), (linex-1, starty-2))
            if (HEIGHT > endy):
                pygame.draw.line(surface, linecolor_outfield, (linex-1, endy), (linex-1, HEIGHT))
        else:
            pygame.draw.line(surface, linecolor_outfield, (linex-1, 0), (linex-1, HEIGHT-1))

    for iy in range(-1, ly):
        liney = oy+(iy*cellsize)
        startx = engine.clamp(0, -target.viewx, -target.viewx+(cellsize*board_width))
        endx = engine.clamp(WIDTH, -target.viewx, -target.viewx+(cellsize*board_width))
        if not (liney+target.viewy < 0 or liney+target.viewy > (cellsize*board_height)): # в пределах поля
            pygame.draw.line(surface, linecolor_infield, (startx-1, liney-1), (endx-1, liney-1))
            if (startx-2 > 0):
                pygame.draw.line(surface, linecolor_outfield, (0, liney-1), (startx-2, liney-1))
            if (WIDTH > endx):
                pygame.draw.line(surface, linecolor_outfield, (endx, liney-1), (WIDTH, liney-1))
        else:
            pygame.draw.line(surface, linecolor_outfield, (0, liney-1), (WIDTH-1, liney-1))

def FieldBoard_kb_pressed(target, buttonid):
    setkey = True
    if buttonid in (pygame.K_UP, pygame.K_w):
        target.keys['up'] = setkey
    if buttonid in (pygame.K_LEFT, pygame.K_a):
        target.keys['left'] = setkey
    if buttonid in (pygame.K_RIGHT, pygame.K_d):
        target.keys['right'] = setkey
    if buttonid in (pygame.K_DOWN, pygame.K_s):
        target.keys['down'] = setkey

def FieldBoard_kb_released(target, buttonid):
    setkey = False
    if buttonid in (pygame.K_UP, pygame.K_w):
        target.keys['up'] = setkey
    if buttonid in (pygame.K_LEFT, pygame.K_a):
        target.keys['left'] = setkey
    if buttonid in (pygame.K_RIGHT, pygame.K_d):
        target.keys['right'] = setkey
    if buttonid in (pygame.K_DOWN, pygame.K_s):
        target.keys['down'] = setkey

EntFieldBoard = engine.Entity(event_create=FieldBoard_create, event_step=FieldBoard_step, event_draw=FieldBoard_draw,
                              event_kb_pressed=FieldBoard_kb_pressed, event_kb_released=FieldBoard_kb_released)
#endregion
#endregion

#region [INSTANCE]
field = EntFieldBoard.instance()
#endregion

#region [ROOM]
room_mainmenu = engine.Room()

room_field = engine.Room([EntFieldBoard])

engine.rooms.change_current_room(room_field)
#endregion

#region [LOOP]
game_running = True
while game_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # выход
            game_running = False
        elif event.type == pygame.VIDEORESIZE:  # изменение размера экрана
            screen.update_screen((event.w, event.h))
        elif event.type == pygame.MOUSEMOTION:
            engine.rooms.current_room.do_mouse_moved(screen.get_mousepos_on_canvas(event.pos))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            engine.rooms.current_room.do_mouse_pressed(screen.get_mousepos_on_canvas(event.pos), event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            engine.rooms.current_room.do_mouse_released(screen.get_mousepos_on_canvas(event.pos), event.button)
        elif event.type == pygame.KEYDOWN:
            engine.rooms.current_room.do_kb_pressed(event.key)
        elif event.type == pygame.KEYUP:
            engine.rooms.current_room.do_kb_released(event.key)

    screen.get_canvas().fill('black')
    engine.rooms.current_room.do_step(screen.get_canvas())
    screen.draw_screen()
    pygame.display.flip()
    deltatime = clock.tick()/1000
#endregion