import ntpath
import os

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
  Alexey Kozhanov                                                                     #13
                                                                               DVLP BUILD
''')

scale = 50
WIDTH, HEIGHT = 16*scale, 9*scale
WIDTH2, HEIGHT2 = WIDTH//2, HEIGHT//2

screen = engine.Screen((WIDTH, HEIGHT), (WIDTH*2, HEIGHT*2), 0, True)
clock = pygame.time.Clock()
deltatime = 0

pygame.init()
#endregion

#region [LOADING FUNCTIONS]
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
                    moddata = comp.get(f.read())
                modname = m[:-4]
                moddata['author'] = author
                moddata['official'] = official
                mods[modname] = moddata
    return mods
#endregion

#region [SETTINGS]
loc = 'rus'
current_instrument = {'type':None}

idlist = []
objdata = {}
fontsize = 16
fonts = {}

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
print('', idlist, list(enumerate(idlist)))
print(objdata)

cell_fill_on_init = idlist.index('grass')
#endregion

#region [ENTITY]
#region [FIELD BOARD]
def FieldBoard_user_draw_board(target):
    bw, bh = target.board_width, target.board_height
    bordersize = round(target.viewscale/8)
    cellsize = target.viewscale
    surface = pygame.Surface((cellsize*bw+bordersize, cellsize*bh+bordersize), pygame.SRCALPHA)
    surface.fill(target.linecolor_infield)
    for ix in range(bw):
        for iy in range(bh):
            cx, cy = ix*cellsize, iy*cellsize
            celldata = objdata[idlist[target.board[iy][ix]]]
            pygame.draw.rect(surface, celldata['notexture'], (cx+bordersize, cy+bordersize,
                                                              target.viewscale-bordersize, target.viewscale-bordersize))

    return surface

def FieldBoard_center_view(target):
    target.viewx = (target.viewscale*target.board_width//2) - (WIDTH2)
    target.viewy = (target.viewscale*target.board_height//2) - (HEIGHT2)

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

    target.board = [[cell_fill_on_init]*target.board_width for _ in range(target.board_height)]

    target.surfaces = {'board': FieldBoard_user_draw_board(target)}

def FieldBoard_step(target):
    target.viewx += deltatime * 2**target.cameraspeed * (target.keys['right']-target.keys['left'])
    target.viewy += deltatime * 2**target.cameraspeed * (target.keys['down']-target.keys['up'])

    if target.keys['rmb']:
        if current_instrument['type'] == 'pencil':
            bordersize = round(target.viewscale/8)
            mx, my = screen.get_mousepos_on_canvas(pygame.mouse.get_pos())
            rx, ry = mx+target.viewx-bordersize, my+target.viewy-bordersize

            cx = rx//target.viewscale
            cy = ry//target.viewscale


            maxcx = target.board_width
            maxcy = target.board_height

            if 0 <= cx < maxcx and 0 <= cy < maxcy:
                if (rx%target.viewscale < (target.viewscale-bordersize) and
                    ry%target.viewscale < (target.viewscale-bordersize)):
                    target.board[int(cy)][int(cx)] = current_instrument['cell']
                    target.surfaces['board'] = FieldBoard_user_draw_board(target)

    #target.cameraspeed = engine.clamp(target.cameraspeed + 2*(target.keys['speedup']-target.keys['speeddown']), 0, 10)

def FieldBoard_draw(target, surface: pygame.Surface):
    bordersize = round(target.viewscale / 8)
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

EntFieldBoard = engine.Entity(event_create=FieldBoard_create, event_step=FieldBoard_step, event_draw=FieldBoard_draw,
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
fieldboard = EntFieldBoard.instance()

fieldsui = EntFieldSUI.instance()
#endregion

#region [ROOM]
room_mainmenu = engine.Room()

room_field = engine.Room([EntFieldBoard, EntFieldSUI])

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