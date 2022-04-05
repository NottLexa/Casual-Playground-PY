'''
NLE1 (NotLexaEngine 1) for Python 3.10+, Pygame 2.1+
Version: 2.0.0
License: CC BY-NC-SA 4.0

Version 2.0.0 replaced Entity as set of unlinked methods to Entity as metaclass and class for inheritance

Версия 2.0.0 заменила Entity как набор несвязанных методов на Entity как метакласс и класс для наследования
'''

import os
import math
import pygame


def sign(x):
    '''возвращает 1, если число положительное, -1 если число отрицательное, 0 если число равно 0.'''
    return -1 if x < 0 else int(x > 0)

def lengthdir_x(len, dir):
    '''координата x конца вектора с длиной len и углом dir.'''
    return len * math.cos(math.radians(dir))

def lengthdir_y(len, dir):
    '''координата x конца вектора с длиной len и углом dir.'''
    return len * -math.sin(math.radians(dir))


def interpolate(x, y, power: int = 1, side: int | bool = 0):
    '''Функция интерполяции.
       Или же поиска значения между x и y, при power = 1 равного средне-арифмитическому,
       но при power > 1 значение будет отступать от средне-арифметического пропорционально значению power
       к x или y в зависимости от side = 0 или 1 соответственно.

       Полезно для ежекадровых функций где объекту нужно изменять значение своей переменной с x до y с ускорением или торможением.
       Чем выше значение power, тем торможение или начальное ускорение будет мягче.

       Аргументы:
           x, y
               Значения, преимущественно числовые.
           power
               Степень рекурсии интерполяции.
               При power > 1, x или y (в завис. от side) заменится на interpolate(x,y,power-1,side).
           side
               Сторона (0/1). Важно когда power > 1. При side=0, функция вернет значение ближе к x нежели к y.'''
    power = max(power, 1)
    div = 2**power
    if side:
        return (x*1/div) + (y*(div-1)/div)
    else:
        return (x*(div-1)/div) + (y*1/div)
    # if power == 1:
    #     return (x+y)/2
    # else:
    #     if side:
    #         return (interpolate(x, y, power - 1, side) + y) / 2
    #     else:
    #         return (x + interpolate(x, y, power - 1, side)) / 2


def hypotenuse(a, b):
    '''Гипотенуза по катетам a и b.'''
    return (a**2 + b**2)**0.5


def point_distance(x1, y1, x2, y2):
    '''Расстояние между точками (x1;y1) и (x2;y2) (длина вектора)'''
    return hypotenuse(x2-x1, y2-y1)

def point_direction(x1, y1, x2, y2):
    '''Угол направления от точки (x1;y1) к точке (x2;y2) (угол между вектором и осью X)

       Пример (направление от точки A к точке B):

       |
       |
       |
       |
       |A#######B    - вернет 0 градусов

       |        B
       |      #
       |    #
       |  #
       |A________    - вернет 45 градусов

       |B
       |#
       |#
       |#
       |A________    - вернет 90 градусов'''
    x = x2-x1
    y = y2-y1
    return math.degrees(math.atan2(-y, x))


def speed_upf(units_per_second, fps):
    '''Возвращает скорость units per frame (т. е. едениц за кадр).
    Необходимо для ежекадровых функций объектов, которые отсчитывают время или двигают объекты.

       Аргументы на вход:
       units_per_second - сколько едениц должно быть в секунду
       fps              - сколько кадров в секунду'''
    return units_per_second/fps


def clamp(value: int, mn: int, mx: int) -> int:
    '''Возвращает значение, равное аргументу value или нижней или верхней грани (mn и mx соответственно), если value выходит за них.'''
    return min(mx, max(mn, value))


def gcd(a: int, b: int) -> int:
    '''Наибольший общий делитель.'''
    if a == 0 or b == 0:
        return a+b
    if a > b:
        return gcd(a%b, b)
    else:
        return gcd(a, b%a)


def pygame_init():
    '''Вызывает pygame.init().'''
    pygame.init()


def pygame_videoinfo():
    '''Возвращает _VidInfo путем вызова pygame.display.Info(). Необходимо для get_screensize(videinfo) в качестве аргумента.
       Работает только после вызова pygame.init().'''
    return pygame.display.Info()

def get_screensize(videoinfo) -> tuple[int, int]:
    '''Получить размер экрана формата (Ширина, Высота).
       В качестве аргумента нужно вставить _VidInfo, получаемый командой pygame.display.Info().
       pygame.display.Info() также можно получить командой pygame_videoinfo().'''
    return (videoinfo.current_w, videoinfo.current_h)


def load_image(path):
    if not os.path.isfile(path):
        raise RuntimeError
    img = pygame.image.load(path)
    return img


class MetaEntity(type):
    def __new__(cls, clsname, sup, attr):
        attr = attr.copy()
        attr['instances'] = list()
        return super(MetaEntity, cls).__new__(cls, clsname, sup, attr)

class Entity(metaclass=MetaEntity):
    '''Класс для создания классов для создания внутреигровых одинаковых, но уникальных объектов.
       Главная способность классов, наследовавших Entity - создавание объектов Instance.

       ВСЕ СОБЫТИЯ (в порядке их выполнения):
       create(target: Instance) - событие, выполняемое сразу же после создания. Не выполняется повторно.

       step_before(target: Instance) - событие, выполняемое каждый игровой кадр, но до event_step всех Instance.
       step(target: Instance)        - событие, выполняемое каждый игровой кадр.
       step_after(target: Instance)  - событие, выполняемое каждый игровой кадр, но после event_step всех Instance.

       draw_before(target: Instance, surface: pygame.Surface) - событие, выполняемое каждый игровой кадр,
                                                                но до event_draw всех Instance.
       draw(target: Instance, surface: pygame.Surface)        - событие, выполняемое каждый игровой кадр.
       draw_after(target: Instance, surface: pygame.Surface)  - событие, выполняемое каждый игровой кадр,
                                                                но после event_draw всех Instance.

       mouse_move(target: Instance, mousepos: tuple[int, int])                 - событие, выполняемое при перемещении
                                                                                 мыши
       mouse_down(target: Instance, mousepos: tuple[int, int], button_id: int) - событие, выполняемое при нажатии на
                                                                                 кнопку мыши
       mouse_up(target: Instance, mousepos: tuple[int, int], button_id: int)   - событие, выполняемое при отпускании
                                                                                 кнопки мыши

       keyboard_down(target: Instance, key: int) - событие, выполняемое при нажатии клавиши
       keyboard_up(target: Instance, key: int)   - событие, выполняемое при отпускании клавиши
    '''

    @staticmethod
    def create(target):
        pass

    @staticmethod
    def step_before(target):
        pass

    @staticmethod
    def step(target):
        pass

    @staticmethod
    def step_after(target):
        pass

    @staticmethod
    def draw_before(target, surface: pygame.Surface):
        pass

    @staticmethod
    def draw(target, surface: pygame.Surface):
        pass

    @staticmethod
    def draw_after(target, surface: pygame.Surface):
        pass

    @staticmethod
    def mouse_move(target, mousepos: tuple[int, int]):
        pass

    @staticmethod
    def mouse_down(target, mousepos: tuple[int, int], button_id: int):
        pass

    @staticmethod
    def mouse_up(target, mousepos: tuple[int, int], button_id: int):
        pass

    @staticmethod
    def keyboard_down(target, key: int):
        pass

    @staticmethod
    def keyboard_up(target, key: int):
        pass

    @staticmethod
    def room_start(target, room):
        pass

    @staticmethod
    def room_end(target, room):
        pass

    @classmethod
    def instance(cls):
        '''Создает новый Instance данного Entity, перенимающий с него все события.

        В качестве **specific (kw_args) можно задать специфические значения переменных, заданных в event_create.'''
        new_instance = Instance(entity = cls)
        cls.instances.append(new_instance)
        return new_instance

    @classmethod
    def destroy_instance(cls, ins):
        del cls.instances[cls.instances.index(ins)]


class Instance:
    def __init__(self, entity: Entity):
        self.entity = entity
        self.entity.create(self)


class Room:
    '''Класс комнат. Комнаты помогают управлять несколькими "игровыми экранами" и ежекадровыми функциями.
       На вход принимает список объектов Entity, Instance которых будут выполнять ежекадровые события
       при вызове метода do_step() или одиночные события event_room_stand и event_room_end при вызове
       методов start() и end() соответственно.'''
    def __init__(self, entities: list[type[Entity]] = None):
        if entities is None:
            self.entities = []
        else:
            self.entities = entities

    def do_step(self, surface_to_draw: pygame.Surface = None):
        step_methods = 'step_before', 'step', 'step_after'
        draw_methods = 'draw_before', 'draw', 'draw_after'

        for m in step_methods:
            for ent in self.entities:
                for ins in ent.instances:
                    getattr(ent, m)(ins)
        if surface_to_draw is not None:
            for m in draw_methods:
                for ent in self.entities:
                    for ins in ent.instances:
                        getattr(ent, m)(ins, surface_to_draw)

    def start(self):
        for ent in self.entities:
            for ins in ent.instances:
                ent.room_start(ins, self)

    def end(self):
        for ent in self.entities:
            for ins in ent.instances:
                ent.room_end(ins, self)

    def do_mouse_moved(self, mousepos):
        for ent in self.entities:
            for ins in ent.instances:
                ent.mouse_move(ins, mousepos)

    def do_mouse_pressed(self, mousepos, buttonid):
        for ent in self.entities:
            for ins in ent.instances:
                ent.mouse_down(ins, mousepos, buttonid)

    def do_mouse_released(self, mousepos, buttonid):
        for ent in self.entities:
            for ins in ent.instances:
                ent.mouse_up(ins, mousepos, buttonid)

    def do_kb_pressed(self, buttonid):
        for ent in self.entities:
            for ins in ent.instances:
                ent.keyboard_down(ins, buttonid)

    def do_kb_released(self, buttonid):
        for ent in self.entities:
            for ins in ent.instances:
                ent.keyboard_up(ins, buttonid)


class rooms:
    '''Здесь хранится действительная комната.
       Не создавать экземпляры класса - переменная current_room хранится у самого класса.
       Есть также функция rooms.change_current_room, позволяющая изменить переменную current_room
       с последовательным вызовом метода end для предыдущего current_room и start для нового.'''
    current_room = None
    @staticmethod
    def change_current_room(new_room: Room):
        if rooms.current_room is not None:
            rooms.current_room.end()
        rooms.current_room = new_room
        rooms.current_room.start()


class Screen:
    '''Класс окна. В нем есть холст (на который наносятся нарисованные объекты) и дисплей (то, что показывается).
       Есть возможность создания полноэкранного режима.

       fullscreen_mode - числовой аргумент от 0 до 2 включительно:
       | 0 - оконный режим
       | 1 - полноэкранный режим
       | 2 - смешанный режим (оконнный на весь экран)'''
    def __init__(self, canvas_size: tuple[int, int], realscreen_size: tuple[int, int], fullscreen_mode: int = 0, resizable_mode: bool = True):
        self.cs = self.cw, self.ch = canvas_size
        if fullscreen_mode == 2:
            self.ss = self.sw, self.sh = SCREENSIZE
        else:
            self.ss = self.sw, self.sh = realscreen_size
        self.canvas = pygame.Surface(self.cs)
        self.fm = clamp(fullscreen_mode, 0, 2)
        self.rm = bool(resizable_mode)
        if self.fm == 1:
            self.screen = pygame.display.set_mode(self.ss, pygame.FULLSCREEN)
        elif self.fm == 2:
            self.screen = pygame.display.set_mode(SCREENSIZE, pygame.NOFRAME)
        else:
            self.screen = pygame.display.set_mode(self.ss, (self.rm * pygame.RESIZABLE))

        self.cd = math.ceil(((self.cw**2)+(self.ch**2))**0.5)
        self.sd = math.ceil(((self.sw**2)+(self.sh**2))**0.5)

        self.cw2 = self.cw//2
        self.ch2 = self.ch//2
        self.cd2 = self.cd//2
        self.sw2 = self.sw//2
        self.sh2 = self.sh//2
        self.sd2 = self.sd//2

        self.scale_level = min(self.sw/self.cw, self.sh/self.ch)
        self.scaled_size = (self.cw * self.scale_level, self.ch * self.scale_level)
        delta_width = self.sw - self.scaled_size[0]
        delta_height = self.sh - self.scaled_size[1]
        self.canvas_offset = (delta_width//2, delta_height//2)

    def get_canvas(self) -> pygame.Surface:
        return self.canvas

    def get_screen(self) -> pygame.Surface:
        return self.screen

    def get_fullscreen(self) -> int:
        return self.fm

    def get_resizable(self) -> bool:
        return self.rm

    def get_canvas_size(self) -> tuple[int, int]:
        return self.cs

    def get_screen_size(self) -> tuple[int, int]:
        return self.ss

    def get_canvas_width(self) -> int:
        return self.cw

    def get_canvas_height(self) -> int:
        return self.ch

    def get_screen_width(self) -> int:
        return self.sw

    def get_screen_height(self) -> int:
        return self.sh

    def get_canvas_halfwidth(self) -> int:
        return self.cw2

    def get_canvas_halfheight(self) -> int:
        return self.ch2

    def get_screen_halfwidth(self) -> int:
        return self.sw2

    def get_screen_halfheight(self) -> int:
        return self.sh2

    def get_canvas_diagonal(self) -> int:
        return self.cd

    def get_canvas_halfdiagonal(self) -> int:
        return self.cd2

    def get_screen_diagonal(self) -> int:
        return self.sd

    def get_screen_halfdiagonal(self) -> int:
        return self.sd2

    def get_canvas_offset(self) -> tuple[int, int]:
        return self.canvas_offset

    def get_canvas_scale_level(self) -> float:
        return self.scale_level

    def update_screen(self, size: tuple[int, int] = None, fullscreen_mode: int = None, resizable_mode: bool = None):
        '''Обновить данные экрана. Значение None в аргументах означает сохранение предыдущего значения.'''
        if size is None:
            size = self.ss
        if fullscreen_mode is None:
            fullscreen_mode = self.fm
        if resizable_mode is None:
            resizable_mode = self.rm

        if self.fm == 2:
            self.ss = self.sw, self.sh = SCREENSIZE
        else:
            self.ss = self.sw, self.sh = size

        self.fm = clamp(fullscreen_mode, 0, 2)
        self.rm = bool(resizable_mode)
        if self.fm == 1:
            self.screen = pygame.display.set_mode(self.ss, pygame.FULLSCREEN)
        elif self.fm == 2:
            self.screen = pygame.display.set_mode(SCREENSIZE, pygame.NOFRAME)
        else:
            self.screen = pygame.display.set_mode(self.ss, (self.rm * pygame.RESIZABLE))

        self.cd = math.ceil(((self.cw ** 2) + (self.ch ** 2)) ** 0.5)
        self.sd = math.ceil(((self.sw ** 2) + (self.sh ** 2)) ** 0.5)

        self.cw2 = self.cw // 2
        self.ch2 = self.ch // 2
        self.cd2 = self.cd // 2
        self.sw2 = self.sw // 2
        self.sh2 = self.sh // 2
        self.sd2 = self.sd // 2

        self.scale_level = min(self.sw/self.cw, self.sh/self.ch)
        self.scaled_size = (self.cw * self.scale_level, self.ch * self.scale_level)
        delta_width = self.sw - self.scaled_size[0]
        delta_height = self.sh - self.scaled_size[1]
        self.canvas_offset = (delta_width//2, delta_height//2)

    def draw_screen(self):
        self.screen.fill('black')
        self.screen.blit(pygame.transform.scale(self.canvas, self.scaled_size), self.canvas_offset)

    def get_mousepos_on_canvas(self, origin_mousepos: tuple[int, int]) -> tuple[float, float]:
        mx, my = origin_mousepos
        ox, oy = self.canvas_offset
        return (mx - ox) / self.scale_level, (my - oy) / self.scale_level


def reciter(iter: dict, tab: int = 0, spacenum: int = 2, symbols='[]', rules: dict = None):
    iterables = rules.keys()
    spaces = ' ' * (spacenum*tab)
    spaces1 = spaces + (' '*spacenum)
    ret = []
    ret.append(spaces + symbols[0])
    for i in iter:
        if any(isinstance(i, r) for r in iterables):
            ret.append(recursive_iterable(i, tab+2, spacenum, rules))
        else:
            ret.append(spaces1 + repr(i))
        if hasattr(iter, '__getitem__') and i != iter[-1]:
            ret[-1] += ','
    ret.append(spaces + symbols[1])
    return '\n'.join(ret)


def reciter_with_keys(iter: dict, tab: int = 0, spacenum: int = 2, symbols='{}', rules: dict = None):
    iterables = rules.keys()
    spaces = ' '*(spacenum*tab)
    spaces1 = spaces + (' '*spacenum)
    spaces2 = spaces1 + (' '*spacenum)
    ret = []
    ret.append(spaces+symbols[0])
    enum = list(iter.items())
    for key, cont in enum:
        ret.append(spaces1+str(key)+':')
        if any(isinstance(cont, r) for r in iterables):
            ret.append(recursive_iterable(cont, tab+2, spacenum, rules))
        else:
            ret.append(spaces2+repr(cont))
        if (key, cont) != enum[-1]:
            ret[-1] += ','
    ret.append(spaces+symbols[1])
    return '\n'.join(ret)


def recursive_iterable(iter: dict | tuple | list, tab: int = 0, spacenum: int = 2, rules: dict = None):
    if rules is None:
        rules = {
            dict: (True, '{', '}'),
            tuple: (False, '(', ')'),
            list: (False, '[', ']'),
        }
    for rule in rules:
        if isinstance(iter, rule):
            if rules[rule][0]:
                return reciter_with_keys(iter, tab, spacenum, rules[rule][1:], rules)
            else:
                return reciter(iter, tab, spacenum, rules[rule][1:], rules)

if __name__ == '__main__':
    pygame_init()
    SCREENSIZE = get_screensize(pygame_videoinfo())
    print('TEST RUN')
    print(f'SCREENSIZE is: {SCREENSIZE[0]}, {SCREENSIZE[1]}')

    canvas_w = 200
    canvas_h = 100
    pixel_size = 2
    canvas_size = (canvas_w, canvas_h)
    screen_size = (canvas_w*pixel_size, canvas_h*pixel_size)
    s = Screen(canvas_size, screen_size, 0, True)

    running = 1
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = 0
            if e.type == pygame.VIDEORESIZE:
                s.update_screen((e.w, e.h))

        pygame.draw.rect(s.get_canvas(), 'yellow', (0,0, *canvas_size), 4)
        pygame.draw.line(s.canvas, 'white', (0,0), canvas_size, 2)
        s.draw_screen()

        pygame.display.flip()