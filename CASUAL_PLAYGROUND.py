import ntpath
import os

import pygame
import math
#from core import nle as engine
#from core import compiler as cpc
import core.nle as engine
import core.compiler as comp
import core.compiler_code_blocks_types as ccbt
import core.compiler_task_types as ctt
from core.compiler_conclusions_cursors import *
from datetime import datetime

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
  Alexey Kozhanov                                                                     #20
                                                                               DVLP BUILD
''')

pygame.init()
vidinf = engine.get_screensize(engine.pygame_videoinfo())
print(vidinf)
WINDOW_WIDTH, WINDOW_HEIGHT = round(vidinf[0] * 3/4), round(vidinf[1] * 3/4)
scale = 50
WIDTH, HEIGHT = 16*scale, 9*scale
WIDTH2, HEIGHT2 = WIDTH//2, HEIGHT//2

screen = engine.Screen((WIDTH, HEIGHT), (WINDOW_WIDTH, WINDOW_HEIGHT), 0, True)
clock = pygame.time.Clock()
deltatime = 0
#endregion

#region [LOADING FUNCTIONS]
def timeformat(dt: datetime, type: int):
    date = f'{dt.day}.{dt.month}.{dt.year}'
    time = f'{dt.hour}:{dt.minute}:{dt.second}'
    ms = f'.{dt.microsecond}'
    match type:
        case 0:
            return date
        case 1:
            return date + ' ' + time
        case 2:
            return date + ' ' + time + ms
        case 3:
            return time
        case 4:
            return time + ms

def load_fonts(fontsfolder):
    fontsdict = {}
    for m in os.listdir(fontsfolder):
        path = ntpath.join(fontsfolder, m)
        if ntpath.isfile(path):
            if path[-4:] == '.ttf':
                fontsdict[m[:-4]] = pygame.font.Font(path, fontsize)
    return fontsdict

def load_modlist(modsfolder):
    filter_func = lambda x: ntpath.isdir(ntpath.join(modsfolder, x))
    filtered = filter(filter_func, os.listdir(modsfolder))
    return list(filtered)

def load_mod(modfolder, author, official):
    mods = {}
    for m in os.listdir(modfolder):
        path = ntpath.join(modfolder, m)
        if ntpath.isfile(path):
            if path[-4:] == '.mod':
                with open(path, 'r', encoding='utf8') as f:
                    moddata, concl, cur = comp.get(f.read())
                    if not correct_concl(concl):
                        #time = f'[{timeformat(datetime.now(), 1)}]'
                        logger.append([LoggerClass.ERROR,
                                       datetime.now(),
                                       f'Couldn\'t load {path}',
                                       f'CasualPlayground Compiler encountered an error: {concl.code}',
                                       concl.description()])
                        #print(f'{time} ')
                        continue
                modname = m[:-4]
                moddata['author'] = author
                moddata['official'] = official
                mods[modname] = moddata
    return mods
#endregion

#region [SETTINGS]
loc = 'rus'
current_instrument = {'type':None}

global_variables = [{'objdata':{},
                     'idlist':[]},
                    {}]
idlist = global_variables[0]['idlist']
objdata = global_variables[0]['objdata']
fontsize = 16
fonts = {}

class LoggerClass:
    types = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    DEBUG, INFO, WARNING, ERROR, CRITICAL = range(len(types))

logger = []
logger_i = 0

fullgamepath = os.getcwd()

font_debug = pygame.font.Font(None, fontsize)
fontsfolder = ntpath.join(fullgamepath, 'data', 'fonts')
fonts = load_fonts(fontsfolder)
def get_font(font):
    if font in fonts:
        return fonts[font]
    else:
        return font_debug

print(fonts)

corefolder = ntpath.join(fullgamepath, 'core', 'corecontent')
modsfolder = ntpath.join(fullgamepath, 'data', 'mods')

coremods = load_mod(corefolder, 'Casual Playground', 1)
idlist.extend(coremods)
objdata.update(coremods)

allmods = load_modlist(modsfolder)
for moddir in allmods:
    modpath = ntpath.join(modsfolder, moddir)
    mod = load_mod(modpath, moddir, 0)
    idlist.extend(mod)
    objdata.update(mod)

'''for m in os.listdir(corefolder):
    path = ntpath.join(corefolder, m)
    if ntpath.isfile(path):
        if path[-4:] == '.mod':
            with open(path, 'r', encoding='utf8') as f:
                moddata = comp.get(f.read())
            modname = m[:-4]
            moddata['author'] = 'Casual Playground'
            moddata['official'] = 1
            objdata[modname] = moddata
            idlist.append(modname)

for folder in os.listdir(modsfolder):
    currentmodfolder = ntpath.join(modsfolder, folder)
    for m in currentmodfolder:
        path = ntpath.join(currentmodfolder, m)
        if ntpath.isfile(path):
            if path[-4:] == '.mod':
                with open(path, 'r', encoding='utf8') as f:
                    moddata = comp.get(f.read())
                modname = m[:-4]
                moddata['author'] = folder
                moddata['official'] = 0
                objdata[modname] = moddata
                idlist.append(modname)'''
print(idlist, list(enumerate(idlist)))
print(engine.recursive_iterable(objdata, 0, 2, {dict: (True, '{', '}'),
                                                tuple: (False, '(', ')'),
                                                list: (False, '[', ']'),
                                                ccbt.BlockSequence: (False, '<BlockSeq', '>'),
                                                ccbt.Block: (False, '<Block', '>'),
                                                }))

cell_fill_on_init = objdata['grass']
cellbordersize = 0.125
#endregion

#region [ENTITY]
#region [GLOBAL CONSOLE]
def GlobalConsole_step(target):
    global logger, logger_i
    while logger_i < len(logger):
        log = logger[logger_i]
        type_string = LoggerClass.types[log[0]]
        time_string = timeformat(log[1], 2)
        prefix = f'[{type_string} {time_string}]' + ' '
        prefix_l = len(prefix)
        print(prefix + log[2])
        for line in log[3:]:
            print(' '*prefix_l + line)
        logger_i += 1

EntGlobalConsole = engine.Entity(event_step=GlobalConsole_step)
#endregion
#region [FIELD BOARD]
def FieldBoard_user_draw_board(target):
    bw, bh = target.board_width, target.board_height
    bordersize = round(target.viewscale*cellbordersize)
    cellsize = target.viewscale
    surface = pygame.Surface((cellsize*bw+bordersize, cellsize*bh+bordersize), pygame.SRCALPHA)
    surface.fill(target.linecolor_infield)
    for ix in range(bw):
        for iy in range(bh):
            cx, cy = ix*cellsize, iy*cellsize
            celldata = target.board[iy][ix].code
            pygame.draw.rect(surface, celldata['notexture'], (cx+bordersize, cy+bordersize,
                                                              target.viewscale-bordersize, target.viewscale-bordersize))

    return surface

def FieldBoard_center_view(target):
    target.viewx = (target.viewscale*target.board_width//2) - (WIDTH2)
    target.viewy = (target.viewscale*target.board_height//2) - (HEIGHT2)

def FieldBoard_board_step(target):
    for y in range(target.board_height):
        for x in range(target.board_width):
            target.board[y][x].step()

def FieldBoard_board_tasks(target):
    change_board = False
    for y in range(target.board_height):
        for x in range(target.board_width):
            tasks = target.board[y][x].tasks
            for tasktype, *args in tasks:
                if tasktype == ctt.SET_CELL:
                    _x, _y, _cellid = args
                    target.board[_y][_x] = comp.Cell({'X': _x, 'Y': _y}, _cellid, target.board, global_variables)
                    change_board = True
            target.board[y][x].tasks.clear()
    if change_board:
        target.surfaces['board'] = FieldBoard_user_draw_board(target)

def FieldBoard_create(target):
    target.board_width = 32
    target.board_height = 32

    target.viewscale = 16
    FieldBoard_center_view(target)

    target.keys = {'up': False,
                   'left': False,
                   'right': False,
                   'down': False,
                   'speedup':False,
                   'speeddown':False,
                   'rmb':False}

    target.cameraspeed = 6
    target.mincamspeed = 3
    target.maxcamspeed = 12

    target.linecolor_infield = 'gray10'
    target.linecolor_outfield = 'gray40'

    target.board = []
    for y in range(target.board_height):
        target.board.append([])
        for x in range(target.board_width):
            celldata = comp.Cell({'X': x, 'Y': y}, idlist.index('grass'), target.board, global_variables)
            target.board[-1].append(celldata)

    target.surfaces = {'board': FieldBoard_user_draw_board(target)}

    target.time = 0.0
    target.timepertick = 1.0

def FieldBoard_step(target):
    #tl_cell = target.board[0][0]
    #print(tl_cell.locals, tl_cell.tasks)

    target.viewx += deltatime * 2**target.cameraspeed * (target.keys['right']-target.keys['left'])
    target.viewy += deltatime * 2**target.cameraspeed * (target.keys['down']-target.keys['up'])

    if target.keys['rmb']:
        if current_instrument['type'] == 'pencil':
            bordersize = round(target.viewscale*cellbordersize)
            mx, my = screen.get_mousepos_on_canvas(pygame.mouse.get_pos())
            rx, ry = mx+target.viewx-bordersize, my+target.viewy-bordersize

            cx = rx//target.viewscale
            cy = ry//target.viewscale


            maxcx = target.board_width
            maxcy = target.board_height

            if 0 <= cx < maxcx and 0 <= cy < maxcy:
                if (rx%target.viewscale < (target.viewscale-bordersize) and
                    ry%target.viewscale < (target.viewscale-bordersize)):
                    cellid = current_instrument['cell']
                    target.board[int(cy)][int(cx)] = comp.Cell({'X':int(cx), 'Y':int(cy)}, cellid, target.board, global_variables)
                    target.surfaces['board'] = FieldBoard_user_draw_board(target)

    #target.cameraspeed = engine.clamp(target.cameraspeed + 2*(target.keys['speedup']-target.keys['speeddown']), 0, 10)

    target.time += deltatime
    if target.time > target.timepertick:
        FieldBoard_board_step(target)
        # target.time = 0 # moved to FieldBoard_after_step

def FieldBoard_step_after(target):
    if target.time > target.timepertick:
        FieldBoard_board_tasks(target)
        target.time = 0

def FieldBoard_draw(target, surface: pygame.Surface):
    bordersize = round(target.viewscale*cellbordersize)
    cellsize = target.viewscale
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
                pygame.draw.rect(surface, target.linecolor_outfield, (linex, 0, bordersize, starty))
            if (HEIGHT > endy):
                pygame.draw.rect(surface, target.linecolor_outfield, (linex, endy+bordersize, bordersize, HEIGHT-endy))
        else:
            pygame.draw.rect(surface, target.linecolor_outfield, (linex, 0, bordersize, HEIGHT))

    for iy in range(-1, ly):
        liney = oy+(iy*cellsize)
        startx = engine.clamp(0, -target.viewx, -target.viewx+(cellsize*target.board_width))
        endx = engine.clamp(WIDTH, -target.viewx, -target.viewx+(cellsize*target.board_width))
        if not (liney+target.viewy < 0 or liney+target.viewy > (cellsize*target.board_height)): # в пределах поля
            if (startx-2 > 0):
                pygame.draw.rect(surface, target.linecolor_outfield, (0, liney, startx, bordersize))
            if (WIDTH > endx):
                pygame.draw.rect(surface, target.linecolor_outfield, (endx+bordersize, liney, WIDTH-endx, bordersize))
        else:
            pygame.draw.rect(surface, target.linecolor_outfield, (0, liney, WIDTH, bordersize))

    txt = get_font('default').render(f'Speed: {2**target.cameraspeed}', False, 'white')
    surface.blit(txt, (surface.get_width() - txt.get_width() - 2,
                       surface.get_height() - txt.get_height() - 2))

    if current_instrument['type'] == 'pencil':
        txt = get_font('default').render(f'Pencil: {idlist[current_instrument["cell"]]}', False, 'white')

        surface.blit(txt, (surface.get_width() - txt.get_width() - 2,
                           surface.get_height() - txt.get_height() - 2 - fontsize-2))

    #for ix in range(0, WIDTH, 16+1):
    #    for iy in range(0, HEIGHT, 16+1):
    #        surface.set_at((int(-target.viewx%cellsize)+ix, int(-target.viewy%cellsize)+iy), 'red')

    #surface.set_at((int(-target.viewx), int(-target.viewy)), 'aqua')

def FieldBoard_kb_pressed(target, key):
    setkey = True
    if key in (pygame.K_UP, pygame.K_w):
        target.keys['up'] = setkey
    if key in (pygame.K_LEFT, pygame.K_a):
        target.keys['left'] = setkey
    if key in (pygame.K_RIGHT, pygame.K_d):
        target.keys['right'] = setkey
    if key in (pygame.K_DOWN, pygame.K_s):
        target.keys['down'] = setkey
    if key == pygame.K_q:
        target.cameraspeed = engine.clamp(target.cameraspeed-1, target.mincamspeed, target.maxcamspeed)
    if key == pygame.K_e:
        target.cameraspeed = engine.clamp(target.cameraspeed+1, target.mincamspeed, target.maxcamspeed)

def FieldBoard_kb_released(target, key):
    setkey = False
    if key in (pygame.K_UP, pygame.K_w):
        target.keys['up'] = setkey
    elif key in (pygame.K_LEFT, pygame.K_a):
        target.keys['left'] = setkey
    elif key in (pygame.K_RIGHT, pygame.K_d):
        target.keys['right'] = setkey
    elif key in (pygame.K_DOWN, pygame.K_s):
        target.keys['down'] = setkey

def FieldBoard_mouse_pressed(target, mousepos, buttonid):
    setkey = True
    if buttonid == 3: # Use instrument
        target.keys['rmb'] = setkey
    elif buttonid == 4: # Scroll up
        oldvs = target.viewscale
        target.viewscale = engine.clamp(target.viewscale-engine.clamp(int(0.2*target.viewscale), 1, 64), 2, 64)
        newvs = target.viewscale

        target.viewx = (target.viewx+(WIDTH2))*newvs/oldvs - (WIDTH2)
        target.viewy = (target.viewy+(HEIGHT2))*newvs/oldvs - (HEIGHT2)

        target.surfaces['board'] = FieldBoard_user_draw_board(target)
    elif buttonid == 5: # Scroll down
        oldvs = target.viewscale
        target.viewscale = engine.clamp(target.viewscale+engine.clamp(int(0.2*target.viewscale), 1, 64), 2, 64)
        newvs = target.viewscale

        target.viewx = (target.viewx+(WIDTH2))*newvs/oldvs - (WIDTH2)
        target.viewy = (target.viewy+(HEIGHT2))*newvs/oldvs - (HEIGHT2)

        target.surfaces['board'] = FieldBoard_user_draw_board(target)

def FieldBoard_mouse_released(target, mousepos, buttonid):
    setkey = False
    if buttonid == 3:  # Use instrument
        target.keys['rmb'] = setkey

EntFieldBoard = engine.Entity(event_create=FieldBoard_create, event_step=FieldBoard_step,
                              event_step_after=FieldBoard_step_after, event_draw=FieldBoard_draw,
                              event_kb_pressed=FieldBoard_kb_pressed, event_kb_released=FieldBoard_kb_released,
                              event_mouse_pressed=FieldBoard_mouse_pressed,
                              event_mouse_released=FieldBoard_mouse_released)
#endregion
#region [FIELD STANDARD UI]
def FieldSUI_create(target):
    target.show_step = 0.0
    target.show_menu = False
    target.show_all = True
    target.cellmenu_width = 256

def FieldSUI_step(target):
    target.show_step = engine.interpolate(target.show_step, int(target.show_menu), 3, 0)

    if round(target.show_step, 5) == 0:
        target.show_step = 0
    elif round(target.show_step, 5) == 1:
        target.show_step = 1

def FieldSUI_draw(target, surface: pygame.Surface):
    if target.show_all:

        measure = int(target.cellmenu_width*1.5)
        phase_offset = int(measure*target.show_step)-measure

        alphabg = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(alphabg, 'gray10', (4+phase_offset, 4, target.cellmenu_width, surface.get_height() - 8), 0, 5)
        pygame.draw.rect(alphabg, 'gray50', (4+phase_offset, 4, target.cellmenu_width, surface.get_height() - 8), 1, 5)

        alphabg.fill((255, 255, 255, 200), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(alphabg, (0, 0))

        inoneline = (target.cellmenu_width-4)//(32+8)
        ci = -1
        for o in idlist:
            obj = objdata[o]
            if obj['type'] == 'CELL':
                ci += 1
                cx, cy = 4+4+(32+8)*(ci%inoneline), 4+4+(32+8)*(ci//inoneline)
                pygame.draw.rect(surface, obj['notexture'], (cx+phase_offset, cy, 32, 32))

def FieldSUI_kb_pressed(target, key):
    if key == pygame.K_TAB:
        if pygame.key.get_mods() & pygame.KMOD_CTRL:
            target.show_all = not target.show_all
        else:
            target.show_menu = not target.show_menu

def FieldSUI_kb_released(target, key):
    pass

def FieldSUI_mouse_pressed(target, mousepos, buttonid):
    if target.show_all:
        global current_instrument
        if buttonid == 1:
            phase_offset = int(200 * target.show_step) - 200
            inoneline = (target.cellmenu_width - 4) // (32 + 8)
            mx, my = mousepos
            mx -= 4+4+phase_offset
            my -= 4+4
            cx = mx//(32+8)
            cy = my//(32+8)
            maxcx = min(len(idlist)-1, (len(idlist)-1)%inoneline)
            maxcy = math.ceil((len(idlist)-1)/inoneline)

            if 0 <= cx <= maxcx and 0 <= cy <= maxcy:
                if (mx%(32+8)) < 16 and (my%(32+8)) < 32:
                    cellid = int(cy*inoneline+cx)
                    current_instrument = {'type':'pencil', 'cell':cellid}


EntFieldSUI = engine.Entity(event_create=FieldSUI_create, event_step=FieldSUI_step, event_draw=FieldSUI_draw,
                            event_kb_pressed=FieldSUI_kb_pressed, event_kb_released=FieldSUI_kb_released,
                            event_mouse_pressed=FieldSUI_mouse_pressed)
#endregion
#endregion

#region [INSTANCE]
globalconsole = EntGlobalConsole.instance()

fieldboard = EntFieldBoard.instance()
fieldsui = EntFieldSUI.instance()
#endregion

#region [ROOM]
room_mainmenu = engine.Room([EntGlobalConsole])

room_field = engine.Room([EntGlobalConsole, EntFieldBoard, EntFieldSUI])

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