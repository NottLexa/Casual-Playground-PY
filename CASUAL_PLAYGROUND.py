import ntpath
import os
import time

import pygame
import math
#from core import nle as engine
#from core import compiler as cpc
import core.nle as engine
import core.compiler as comp
from core.compiler import LoggerClass
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
  Alexey Kozhanov                                                                     #27
                                                                               DVLP BUILD
''')

pygame.init()
vidinf = engine.get_screensize(engine.pygame_videoinfo())
print(vidinf)
WINDOW_WIDTH, WINDOW_HEIGHT = round(vidinf[0] * 3/4), round(vidinf[1] * 3/4)
scale = 100
WIDTH, HEIGHT = 16*scale, 9*scale
WIDTH2, HEIGHT2 = WIDTH//2, HEIGHT//2

screen = engine.Screen((WIDTH, HEIGHT), (WINDOW_WIDTH, WINDOW_HEIGHT), 0, True)
clock = pygame.time.Clock()
deltatime = 0
#endregion

#region [LOADING FUNCTIONS]
def timeformat(dt: datetime, type: int):
    date = f'{dt.day:02}.{dt.month:02}.{dt.year}'
    time = f'{dt.hour:02}:{dt.minute:02}:{dt.second:02}'
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

def cut_string(string: str, upto: int):
    if len(string) <= upto:
        return string
    else:
        return string[:upto-3] + '...'

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

def load_mod(modfolder, origin, official):
    mods = {}
    for m in os.listdir(modfolder):
        path = ntpath.join(modfolder, m)
        if ntpath.isfile(path):
            if path[-4:].lower() == '.mod':
                with open(path, 'r', encoding='utf8') as f:
                    moddata, concl, cur = comp.get(f.read())
                    if not correct_concl(concl):
                        #time = f'[{timeformat(datetime.now(), 1)}]'
                        logger.append([LoggerClass.ERROR,
                                       datetime.now(),
                                       f'Couldn\'t load {path}',
                                       f'CasualPlayground Compiler encountered an error: {concl.code}',
                                       concl.description(),
                                       cur.highlight(),
                                       cur.string()])
                        #print(f'{time} ')
                        continue
                modname = m[:-4]
                moddata['origin'] = origin
                moddata['official'] = official
                imgpath = path[:-4]+'.png'
                if ntpath.isfile(imgpath):
                    moddata['texture'] = pygame.image.load(imgpath)
                if official:
                    mods[modname] = moddata
                else:
                    mods[f'{origin}/{modname}'] = moddata
    return mods
#endregion

#region [SETTINGS]
loc = 'rus'
current_instrument = {'type':None}

global_variables = [{'objdata':{},
                     'idlist':[],
                     'logger':[],
                     'board_width':10,
                     'board_height':10},
                    {}]
idlist = global_variables[0]['idlist']
objdata = global_variables[0]['objdata']
logger = global_variables[0]['logger']
fontsize = scale*2
fontsize_bigger  = int(32*fontsize/scale)
fontsize_big     = int(24*fontsize/scale)
fontsize_default = int(16*fontsize/scale)
fontsize_small   = int(12*fontsize/scale)
fontsize_smaller = int(8*fontsize/scale)
fonts = {}

fullgamepath = os.getcwd()

font_debug = pygame.font.Font(None, fontsize)
fontsfolder = ntpath.join(fullgamepath, 'data', 'fonts')
fonts = load_fonts(fontsfolder)
def get_font(font) -> pygame.font.Font:
    if font in fonts:
        return fonts[font]
    else:
        return font_debug

def render_font(font: pygame.font.Font | str, size: int,
                text: str | bytes, antialias: bool, color, background = None) -> pygame.Surface:
    if isinstance(font, str):
        font = get_font(font)
    ret = font.render(text, antialias, color, background)
    ratio = size/fontsize
    if antialias:
        return pygame.transform.smoothscale(ret, (ret.get_width()*ratio, ret.get_height()*ratio))
    else:
        return pygame.transform.scale(ret, (ret.get_width()*ratio, ret.get_height()*ratio))

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
                                                ccbt.Gate: (False, '<Gate', '>'),
                                                ccbt.While: (False, '<While', '>')
                                                }))

cell_fill_on_init = objdata['grass']
cellbordersize = 0.125
#endregion

#region [ENTITY]
#region [GLOBAL CONSOLE]
def GlobalConsole_create(target):
    target.logger_i = 0

def GlobalConsole_step(target):
    global logger
    while target.logger_i < len(logger):
        log = logger[target.logger_i]
        type_string = LoggerClass.types[log[0]]
        time_string = timeformat(log[1], 1)
        prefix = f'[{type_string} {time_string}]' + ' '
        prefix_l = len(prefix)
        print(prefix + log[2])
        for line in log[3:]:
            print(' '*prefix_l + line)
        target.logger_i += 1

def GlobalConsole_draw_after(target, surface: pygame.Surface):
    txt = render_font('default', fontsize_default, f'{round(1/deltatime) if deltatime != 0 else 0} FPS', False, 'white')
    surface.blit(txt, (surface.get_width()-txt.get_width()-8, 8))

EntGlobalConsole = engine.Entity(event_create=GlobalConsole_create, event_step=GlobalConsole_step,
                                 event_draw_after=GlobalConsole_draw_after)
#endregion
#region [FIELD BOARD]
def FieldBoard_user_draw_board(target):
    bw, bh = target.board_width, target.board_height
    bordersize = round(target.viewscale*cellbordersize)
    cellsize = target.viewscale+bordersize
    surface = pygame.Surface((cellsize*bw+bordersize, cellsize*bh+bordersize), pygame.SRCALPHA)
    surface.fill(target.linecolor_infield)
    for ix in range(bw):
        for iy in range(bh):
            cx, cy = (ix*cellsize)+bordersize, (iy*cellsize)+bordersize
            celldata = target.board[iy][ix].code
            if 'texture' in celldata:
                txtr = pygame.transform.scale(celldata['texture'],
                                              (target.viewscale, target.viewscale))
                surface.blit(txtr, (cx, cy))
            else:
                pygame.draw.rect(surface, celldata['notexture'], (cx, cy,
                                                              target.viewscale, target.viewscale))

    return surface

def FieldBoard_center_view(target):
    target.viewx = (target.viewscale*target.board_width//2) - (WIDTH2)
    target.viewy = (target.viewscale*target.board_height//2) - (HEIGHT2)

def FieldBoard_zoom_out(target, mul):
    oldvs = target.viewscale
    target.viewscale = engine.clamp(target.viewscale - engine.clamp(int(0.2 * mul * target.viewscale), 1, 64), 2, 64)
    newvs = target.viewscale

    target.viewx = (target.viewx + (WIDTH2)) * newvs / oldvs - (WIDTH2)
    target.viewy = (target.viewy + (HEIGHT2)) * newvs / oldvs - (HEIGHT2)

    target.surfaces['board'] = FieldBoard_user_draw_board(target)

def FieldBoard_zoom_in(target, mul):
    oldvs = target.viewscale
    target.viewscale = engine.clamp(target.viewscale + engine.clamp(int(0.2 * mul * target.viewscale), 1, 64), 2, 64)
    newvs = target.viewscale

    target.viewx = (target.viewx + (WIDTH2)) * newvs / oldvs - (WIDTH2)
    target.viewy = (target.viewy + (HEIGHT2)) * newvs / oldvs - (HEIGHT2)

    target.surfaces['board'] = FieldBoard_user_draw_board(target)

def FieldBoard_do_instrument(target):
    bordersize = round(target.viewscale * cellbordersize)
    cellsize = bordersize + target.viewscale
    mx, my = screen.get_mousepos_on_canvas(pygame.mouse.get_pos())
    rx, ry = mx + target.viewx - bordersize, my + target.viewy - bordersize
    cx, cy = rx//cellsize, ry//cellsize
    maxcx, maxcy = target.board_width, target.board_height
    if target.keys['rmb']:
        if current_instrument['type'] == 'pencil':
            scale = current_instrument['scale']-1
            if current_instrument['penciltype']: # round
                pass
            else: # square
                if (rx % cellsize < (target.viewscale) and
                        ry % cellsize < (target.viewscale)):
                    for ix in range(int(cx)-scale, int(cx)+scale+1):
                        for iy in range(int(cy)-scale, int(cy)+scale+1):
                            if 0 <= ix < maxcx and 0 <= iy < maxcy:
                                cellid = current_instrument['cell']
                                target.board[iy][ix] = comp.Cell({'X': ix, 'Y': iy}, cellid, target.board,
                                                                           global_variables)
                                target.surfaces['board'] = FieldBoard_user_draw_board(target)

def FieldBoard_board_step(target):
    start = time.time()
    for y in range(target.board_height):
        for x in range(target.board_width):
            target.board[y][x].step()
    target.time_elapsed = time.time()-start

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

    global global_variables
    global_variables[0]['board_width'] = target.board_width
    global_variables[0]['board_height'] = target.board_height

    target.viewscale = 16
    FieldBoard_center_view(target)

    target.keys = {'up': False,
                   'left': False,
                   'right': False,
                   'down': False,
                   'speedup':False,
                   'speeddown':False,
                   'rmb':False,
                   'plus':False,
                   'minus':False,}

    target.cameraspeed = round(math.log2((2**9)*scale/100)) #round(9*scale/100)
    target.mincamspeed = round(math.log2((2**6)*scale/100)) #round(6*scale/100)
    target.maxcamspeed = round(math.log2((2**14)*scale/100)) #round(14*scale/100)
    target.hsp = 0
    target.vsp = 0
    target.acceleration = 8
    target.zoomspeed = 1

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
    target.tpt_power = 28
    target.get_tpt = lambda n: ((10**(n//9))*(n%9) if n%9 != 0 else 10**((n//9)-1)*9) / 1000
    target.tpt_min, target.tpt_max = 1, 60
    target.timepertick = 1.0
    target.time_paused = False
    target.time_elapsed = 0.0

def FieldBoard_step(target):
    #tl_cell = target.board[0][0]
    #print(tl_cell.locals, tl_cell.tasks)

    if target.keys['plus']:
        FieldBoard_zoom_in(target, target.zoomspeed*deltatime)
    if target.keys['minus']:
        FieldBoard_zoom_out(target, target.zoomspeed*deltatime)

    limitspeed = 2**target.cameraspeed
    acc = limitspeed*target.acceleration

    hmov = target.keys['right'] - target.keys['left']
    vmov = target.keys['down'] - target.keys['up']

    if hmov != 0:
        target.hsp = engine.clamp(target.hsp + deltatime*acc*hmov, -limitspeed, limitspeed)
    else:
        target.hsp = engine.clamp(target.hsp - deltatime*engine.sign(target.hsp)*acc,
                                  min(target.hsp, 0), max(0, target.hsp))
    if vmov != 0:
        target.vsp = engine.clamp(target.vsp + deltatime*acc*vmov, -limitspeed, limitspeed)
    else:
        target.vsp = engine.clamp(target.vsp - deltatime*engine.sign(target.vsp)*acc,
                                  min(target.vsp, 0), max(0, target.vsp))

    target.viewx += deltatime * target.hsp
    target.viewy += deltatime * target.vsp

    FieldBoard_do_instrument(target)

    #target.cameraspeed = engine.clamp(target.cameraspeed + 2*(target.keys['speedup']-target.keys['speeddown']), 0, 10)

    if not target.time_paused:
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
    cellsize = target.viewscale+bordersize
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

    # speed
    txt = render_font('default', fontsize_default, f'Max speed: {2**target.cameraspeed}', False, 'white')
    surface.blit(txt, (surface.get_width() - txt.get_width() - 2,
                       surface.get_height() - txt.get_height() - 2))
    txt = render_font('default', fontsize_default, f'hsp: {round(target.hsp)} / vsp: {round(target.vsp)}',
                      False, 'white')
    surface.blit(txt, (surface.get_width() - txt.get_width() - 2,
                       surface.get_height() - txt.get_height() - 2 - (fontsize_default-2)))

    # time per tick
    txt = render_font('default', fontsize_default,
                      f'{target.timepertick}s '+('| Paused' if target.time_paused else ''), False, 'white')
    surface.blit(txt, (5, -5 + surface.get_height() - fontsize_default))

    # time elapsed
    clr = 'white' if target.time_elapsed <= target.timepertick else pygame.Color(17*14, 17, 17)
    txt = render_font('default', fontsize_small,
                      f'{round(target.time_elapsed, 5)} s',
                      False, clr)
    surface.blit(txt, (5, -10 + surface.get_height() - fontsize_default - 2*fontsize_small))
    txt = render_font('default', fontsize_small,
                      f'{round(target.time_elapsed / (target.board_width * target.board_height), 5)} s/cell',
                      False, clr)
    surface.blit(txt, (5, -10 + surface.get_height() - fontsize_default - fontsize_small))

    # instrument
    if current_instrument['type'] == 'pencil':
        string = f'Pencil[{current_instrument["scale"]}] | {idlist[current_instrument["cell"]]} ' \
                 f'| {"Round" if current_instrument["penciltype"] else "Square"}'
        txt = render_font('default', fontsize_default, string, False, 'white')

        surface.blit(txt, (surface.get_width() - txt.get_width() - 2,
                           surface.get_height() - txt.get_height() - 2 - 2*(fontsize_default-2)))

    #for ix in range(0, WIDTH, 16+1):
    #    for iy in range(0, HEIGHT, 16+1):
    #        surface.set_at((int(-target.viewx%cellsize)+ix, int(-target.viewy%cellsize)+iy), 'red')

    #surface.set_at((int(-target.viewx), int(-target.viewy)), 'aqua')

def FieldBoard_kb_pressed(target, key):
    setkey = True
    if key in (pygame.K_UP, pygame.K_w):
        target.keys['up'] = setkey
    elif key in (pygame.K_LEFT, pygame.K_a):
        target.keys['left'] = setkey
    elif key in (pygame.K_RIGHT, pygame.K_d):
        target.keys['right'] = setkey
    elif key in (pygame.K_DOWN, pygame.K_s):
        target.keys['down'] = setkey
    elif key == pygame.K_EQUALS:
        target.keys['plus'] = setkey
    elif key == pygame.K_MINUS:
        target.keys['minus'] = setkey
    elif key == pygame.K_q:
        target.cameraspeed = engine.clamp(target.cameraspeed-1, target.mincamspeed, target.maxcamspeed)
    elif key == pygame.K_e:
        target.cameraspeed = engine.clamp(target.cameraspeed+1, target.mincamspeed, target.maxcamspeed)
    elif key == pygame.K_c:
        FieldBoard_center_view(target)
        target.hsp = target.vsp = 0
    elif key == pygame.K_f:
        target.time_paused = not target.time_paused
    elif key == pygame.K_r:
        target.tpt_power = max(target.tpt_min, target.tpt_power-1)
        target.timepertick = target.get_tpt(target.tpt_power)
    elif key == pygame.K_t:
        target.tpt_power = min(target.tpt_max, target.tpt_power+1)
        target.timepertick = target.get_tpt(target.tpt_power)

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
    elif key == pygame.K_EQUALS:
        target.keys['plus'] = setkey
    elif key == pygame.K_MINUS:
        target.keys['minus'] = setkey

def FieldBoard_mouse_pressed(target, mousepos, buttonid):
    global current_instrument
    setkey = True
    if buttonid == 3: # Use instrument
        target.keys['rmb'] = setkey
    elif buttonid == 4: # Scroll up
        if pygame.key.get_mods() & pygame.KMOD_SHIFT: current_instrument['scale'] += 1
        else: FieldBoard_zoom_in(target, 1)
    elif buttonid == 5: # Scroll down
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            current_instrument['scale'] = max(current_instrument['scale']-1, 1)
        else: FieldBoard_zoom_out(target, 1)

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
    target.cellmenu_width = 512*scale/100
    target.window_spacing = 8*scale/100
    target.display_scale = 80*scale/100
    target.element_border = target.display_scale/4

def FieldSUI_step(target):
    target.show_step = engine.interpolate(target.show_step, int(target.show_menu), 3, 0)

    if round(target.show_step, 5) == 0:
        target.show_step = 0
    elif round(target.show_step, 5) == 1:
        target.show_step = 1

def FieldSUI_draw(target, surface: pygame.Surface):
    if target.show_all:
        ds = target.display_scale
        eb = target.element_border
        ws = target.window_spacing

        measure = int(target.cellmenu_width*1.5)
        phase_offset = int(measure*target.show_step)-measure

        alphabg = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(alphabg, 'gray10', (ws+phase_offset, ws, target.cellmenu_width, surface.get_height() - 2*ws), 0, 5)
        pygame.draw.rect(alphabg, 'gray50', (ws+phase_offset, ws, target.cellmenu_width, surface.get_height() - 2*ws), 1, 5)

        alphabg.fill((255, 255, 255, 200), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(alphabg, (0, 0))
        inoneline = (target.cellmenu_width-ws)//(ds+eb)
        ci = -1
        for o in idlist:
            obj = objdata[o]
            if obj['type'] == 'CELL':
                ci += 1
                cx, cy = ws+eb+(ds+eb)*(ci%inoneline), ws+eb+(ds+eb+fontsize_smaller)*(ci//inoneline)
                pygame.draw.rect(surface, obj['notexture'], (cx+phase_offset, cy, ds, ds))
                txt = render_font('default', fontsize_smaller, cut_string(obj['name'], 9), True, 'white')
                surface.blit(txt, (cx+(ds/2)+phase_offset-(txt.get_width()//2), cy+ds+(eb/2)))

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
        ds = target.display_scale
        eb = target.element_border
        ws = target.window_spacing
        global current_instrument
        if buttonid == 1:
            phase_offset = int(200 * target.show_step) - 200
            inoneline = (target.cellmenu_width-ws)//(ds+eb)
            mx, my = mousepos
            detectwidth, detectheight = ds+eb, ds+fontsize_smaller+(1.5*eb)
            ci = (mx-eb)//detectwidth + ((my-eb)//detectheight)*inoneline
            cx, cy = ws+eb+(ds+eb)*(ci%inoneline), ws+eb+(ds+eb+fontsize_smaller)*(ci//inoneline)
            if (cx <= mx <= cx+detectwidth-eb) and (cy <= my <= cy+detectheight-eb):
                current_instrument = {'type': 'pencil', 'cell': int(ci), 'penciltype': False, 'scale': 1}


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