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
  Alexey Kozhanov                                                                      #8
                                                                               DVLP BUILD
''')

scale = 50
WIDTH, HEIGHT = 16*scale, 9*scale

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
print('', list(enumerate(idlist)))
print(objdata)
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

    txt = get_font('default').render(f'Speed: {2**target.cameraspeed}', False, 'white')
    surface.blit(txt, (surface.get_width() - txt.get_width() - 2,
                       surface.get_height() - txt.get_height() - 2))

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
#region [FIELD STANDARD UI]
def FieldSUI_create(target):
    target.show_step = 0.0
    target.show_menu = False
    target.show_all = True

def FieldSUI_step(target):
    target.show_step = engine.interpolate(target.show_step, int(target.show_menu), 3, 0)

    print(target.show_step, target.show_menu, target.show_all)
    if round(target.show_step, 5) == 0:
        target.show_step = 0
    elif round(target.show_step, 5) == 1:
        target.show_step = 1

def FieldSUI_draw(target, surface: pygame.Surface):
    if target.show_all:

        phase_offset = int(200*target.show_step)-200

        alphabg = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(alphabg, 'gray10', (4+phase_offset, 4, 128, surface.get_height() - 8), 0, 5)
        pygame.draw.rect(alphabg, 'gray50', (4+phase_offset, 4, 128, surface.get_height() - 8), 1, 5)

        alphabg.fill((255, 255, 255, 200), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(alphabg, (0, 0))

def FieldSUI_kb_pressed(target, key):
    if key == pygame.K_TAB:
        if pygame.key.get_mods() and pygame.KMOD_CTRL:
            target.show_all = not target.show_all
        else:
            target.show_menu = not target.show_menu

def FieldSUI_kb_released(target, key):
    pass

EntFieldSUI = engine.Entity(event_create=FieldSUI_create, event_step=FieldSUI_step, event_draw=FieldSUI_draw,
                            event_kb_pressed=FieldSUI_kb_pressed, event_kb_released=FieldSUI_kb_released)
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