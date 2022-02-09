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
  Alexey Kozhanov                                                                      #5
                                                                               DVLP BUILD
''')

scale = 30
WIDTH, HEIGHT = 16*scale, 9*scale

screen = engine.Screen((WIDTH, HEIGHT), (WIDTH*2, HEIGHT*2), 0, True)
clock = pygame.time.Clock()
deltatime = 0

pygame.init()
#endregion

#region [SETTINGS]
font_debug = pygame.font.SysFont('calibri', 10)
objdata = {}
with open('core/corecontent/grass.mod', encoding='utf8') as g:
    objdata['grass'] = comp.get(g.read())
idlist = ['grass']
print(objdata[idlist[0]])
#endregion

#region [ENTITY]
#region [FIELD BOARD]
def FieldBoard_user_draw_board(target):
    bw, bh = target.board_width, target.board_height
    cellsize = target.viewscale + 1
    surface = pygame.Surface((cellsize*bw+1, cellsize*bh+1), pygame.SRCALPHA)
    surface.fill(target.linecolor_infield)
    for ix in range(bw):
        for iy in range(bh):
            cx, cy = ix*cellsize, iy*cellsize
            celldata = objdata[idlist[target.board[iy][ix]]]
            pygame.draw.rect(surface, celldata['notexture'], (cx+1, cy+1, target.viewscale, target.viewscale))

    return surface

def FieldBoard_create(target):
    target.viewx = 0
    target.viewy = 0
    target.viewscale = 16
    target.keys = {'up': False,
                   'left': False,
                   'right': False,
                   'down': False,
                   'speedup':False,
                   'speeddown':False}
    target.cameraspeed = 6
    target.mincamspeed = 3
    target.maxcamspeed = 12
    target.board_width = 32
    target.board_height = 32
    target.linecolor_infield = 'gray10'
    target.linecolor_outfield = 'gray40'
    target.board = [[0]*target.board_width for _ in range(target.board_height)]

    target.surfaces = {'board': FieldBoard_user_draw_board(target)}

def FieldBoard_step(target):
    target.viewx += deltatime * 2**target.cameraspeed * (target.keys['right']-target.keys['left'])
    target.viewy += deltatime * 2**target.cameraspeed * (target.keys['down']-target.keys['up'])

    #target.cameraspeed = engine.clamp(target.cameraspeed + 2*(target.keys['speedup']-target.keys['speeddown']), 0, 10)

def FieldBoard_draw(target, surface: pygame.Surface):
    cellsize = target.viewscale+1
    ox = -target.viewx%cellsize
    oy = -target.viewy%cellsize
    lx = math.ceil(WIDTH/cellsize)
    ly = math.ceil(HEIGHT/cellsize)

    if target.viewx > 0:
        realx = -target.viewx-1
    else:
        realx = -target.viewx
    if target.viewy > 0:
        realy = -target.viewy-1
    else:
        realy = -target.viewy
    surface.blit(target.surfaces['board'], (realx, realy))

    for ix in range(-1, lx):
        linex = ox+(ix*cellsize)
        starty = engine.clamp(0, -target.viewy, -target.viewy+(cellsize*target.board_height))
        endy = engine.clamp(HEIGHT, -target.viewy, -target.viewy+(cellsize*target.board_height))
        if not (linex+target.viewx < 0 or linex+target.viewx > (cellsize*target.board_width)): # в пределах поля
            if (starty-2 > 0):
                pygame.draw.line(surface, target.linecolor_outfield, (linex, 1), (linex, starty-1))
            if (HEIGHT > endy):
                pygame.draw.line(surface, target.linecolor_outfield, (linex, endy+1), (linex, HEIGHT+1))
        else:
            pygame.draw.line(surface, target.linecolor_outfield, (linex, 1), (linex, HEIGHT))

    for iy in range(-1, ly):
        liney = oy+(iy*cellsize)
        startx = engine.clamp(0, -target.viewx, -target.viewx+(cellsize*target.board_width))
        endx = engine.clamp(WIDTH, -target.viewx, -target.viewx+(cellsize*target.board_width))
        if not (liney+target.viewy < 0 or liney+target.viewy > (cellsize*target.board_height)): # в пределах поля
            if (startx-2 > 0):
                pygame.draw.line(surface, target.linecolor_outfield, (1, liney), (startx-1, liney))
            if (WIDTH > endx):
                pygame.draw.line(surface, target.linecolor_outfield, (endx+1, liney), (WIDTH+1, liney))
        else:
            pygame.draw.line(surface, target.linecolor_outfield, (1, liney), (WIDTH, liney))

    txt = font_debug.render(f'Speed: {2**target.cameraspeed}', False, 'white')
    surface.blit(txt, (surface.get_width() - txt.get_width() - 2,
                       surface.get_height() - txt.get_height() - 2))

    #for ix in range(0, WIDTH, 16+1):
    #    for iy in range(0, HEIGHT, 16+1):
    #        surface.set_at((int(-target.viewx%cellsize)+ix, int(-target.viewy%cellsize)+iy), 'red')

    #surface.set_at((int(-target.viewx), int(-target.viewy)), 'aqua')

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
    if buttonid == pygame.K_q:
        target.cameraspeed = engine.clamp(target.cameraspeed-1, target.mincamspeed, target.maxcamspeed)
    if buttonid == pygame.K_e:
        target.cameraspeed = engine.clamp(target.cameraspeed+1, target.mincamspeed, target.maxcamspeed)

def FieldBoard_kb_released(target, buttonid):
    setkey = False
    if buttonid in (pygame.K_UP, pygame.K_w):
        target.keys['up'] = setkey
    elif buttonid in (pygame.K_LEFT, pygame.K_a):
        target.keys['left'] = setkey
    elif buttonid in (pygame.K_RIGHT, pygame.K_d):
        target.keys['right'] = setkey
    elif buttonid in (pygame.K_DOWN, pygame.K_s):
        target.keys['down'] = setkey

def FieldBoard_mouse_pressed(target, mousepos, buttonid):
    if buttonid == 4:
        target.viewscale = engine.clamp(target.viewscale-1, 2, 64)
        target.surfaces['board'] = FieldBoard_user_draw_board(target)
    elif buttonid == 5:
        target.viewscale = engine.clamp(target.viewscale+1, 2, 64)
        target.surfaces['board'] = FieldBoard_user_draw_board(target)

EntFieldBoard = engine.Entity(event_create=FieldBoard_create, event_step=FieldBoard_step, event_draw=FieldBoard_draw,
                              event_kb_pressed=FieldBoard_kb_pressed, event_kb_released=FieldBoard_kb_released,
                              event_mouse_pressed=FieldBoard_mouse_pressed)
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