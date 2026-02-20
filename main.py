import pygame
import random
import math
import sys
import json
import os
from collections import deque

# ============================================================================
# Инициализация и выбор устройства
# ============================================================================
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

def choose_device():
    temp_screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Выберите устройство")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 30)

    devices = [
        {"name": "Телефон", "base_width": 800, "type": "phone", "rect": None},
        {"name": "Планшет", "base_width": 1200, "type": "tablet", "rect": None},
        {"name": "Компьютер", "base_width": 1600, "type": "pc", "rect": None}
    ]

    choosing = True
    while choosing:
        temp_screen.fill((50, 50, 50))
        title = font.render("Выберите устройство", True, (255, 255, 255))
        temp_screen.blit(title, (400 - title.get_width()//2, 100))

        for i, dev in enumerate(devices):
            x = 200 + i * 200
            y = 250
            rect = pygame.Rect(x, y, 150, 150)
            pygame.draw.rect(temp_screen, (100, 100, 200), rect)
            pygame.draw.rect(temp_screen, (255, 255, 255), rect, 3)
            if i == 0:
                pygame.draw.rect(temp_screen, (50, 50, 50), (x+30, y+20, 90, 110))
                pygame.draw.rect(temp_screen, (200, 230, 255), (x+40, y+30, 70, 80))
                pygame.draw.circle(temp_screen, (150, 150, 150), (x+75, y+120), 8)
            elif i == 1:
                pygame.draw.rect(temp_screen, (70, 70, 70), (x+20, y+15, 110, 120))
                pygame.draw.rect(temp_screen, (220, 240, 255), (x+30, y+25, 90, 100))
                pygame.draw.circle(temp_screen, (180, 180, 180), (x+75, y+130), 5)
            else:
                pygame.draw.rect(temp_screen, (60, 60, 60), (x+20, y+15, 100, 80))
                pygame.draw.rect(temp_screen, (180, 210, 240), (x+25, y+20, 90, 60))
                pygame.draw.rect(temp_screen, (80, 80, 80), (x+55, y+95, 30, 10))
                pygame.draw.rect(temp_screen, (70, 70, 70), (x+125, y+30, 20, 60))
                pygame.draw.circle(temp_screen, (150, 150, 150), (x+135, y+50), 5)
                pygame.draw.rect(temp_screen, (90, 90, 90), (x+20, y+110, 100, 15))
                for k in range(5):
                    pygame.draw.rect(temp_screen, (150, 150, 150), (x+25 + k*15, y+113, 8, 8))
            name = small_font.render(dev["name"], True, (255, 255, 255))
            temp_screen.blit(name, (x+75 - name.get_width()//2, y+160))
            devices[i]["rect"] = rect

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = event.pos
                    for dev in devices:
                        if dev["rect"].collidepoint(pos):
                            return dev["base_width"], dev["type"]
    return 800, "phone"

BASE_WIDTH, DEVICE_TYPE = choose_device()
pygame.quit()
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Фруктовый Ниндзя 2.0")
clock = pygame.time.Clock()
FPS = 30

SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
SCALE = SCREEN_WIDTH / BASE_WIDTH

if DEVICE_TYPE == "tablet":
    FONT_SCALE = 1.3
elif DEVICE_TYPE == "pc":
    FONT_SCALE = 1.6
else:
    FONT_SCALE = 1.0

font_large = pygame.font.Font(None, int(100 * SCALE * FONT_SCALE))
font_medium = pygame.font.Font(None, int(70 * SCALE * FONT_SCALE))
font_small = pygame.font.Font(None, int(40 * SCALE * FONT_SCALE))

if DEVICE_TYPE == "phone":
    font_rules = pygame.font.Font(None, int(28 * SCALE * FONT_SCALE))
elif DEVICE_TYPE == "pc":
    font_rules = pygame.font.Font(None, int(28 * SCALE * FONT_SCALE))
else:
    font_rules = pygame.font.Font(None, int(32 * SCALE * FONT_SCALE))

# ============================================================================
# Звуковой менеджер
# ============================================================================
class SoundManager:
    def __init__(self):
        self.slice_sound = None
        self.button_sound = None
        self.music_playing = False
        self.load_sounds()

    def load_sounds(self):
        try:
            if os.path.exists("slice.wav"):
                self.slice_sound = pygame.mixer.Sound("slice.wav")
            if os.path.exists("button.wav"):
                self.button_sound = pygame.mixer.Sound("button.wav")
        except Exception as e:
            print("Ошибка загрузки звуков:", e)

    def play_slice(self):
        if self.slice_sound:
            self.slice_sound.play()

    def play_button(self):
        if self.button_sound:
            self.button_sound.play()

    def start_music(self):
        if not self.music_playing and os.path.exists("background_music.ogg"):
            try:
                pygame.mixer.music.load("background_music.ogg")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except Exception as e:
                print("Ошибка музыки:", e)

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False

sound_manager = SoundManager()

# ============================================================================
# Рекорды
# ============================================================================
HIGHSCORE_FILE = "highscores.json"
HIGHSCORE_BACKUP = "highscores_backup.json"

def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "classic" in data and "fast" in data:
                    return data
                else:
                    if os.path.exists(HIGHSCORE_BACKUP):
                        with open(HIGHSCORE_BACKUP, "r") as b:
                            return json.load(b)
        except:
            if os.path.exists(HIGHSCORE_BACKUP):
                try:
                    with open(HIGHSCORE_BACKUP, "r") as b:
                        return json.load(b)
                except:
                    pass
    return {"classic": 0, "fast": 0}

def save_highscores(scores):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(scores, f)
        with open(HIGHSCORE_BACKUP, "w") as b:
            json.dump(scores, b)
    except Exception as e:
        print(f"Ошибка сохранения рекордов: {e}")

# ============================================================================
# Сохранение разблокированных скинов
# ============================================================================
SKINS_FILE = "skins.json"

def load_unlocked_skins():
    """Загружает списки разблокированных скинов из файла."""
    if os.path.exists(SKINS_FILE):
        try:
            with open(SKINS_FILE, "r") as f:
                data = json.load(f)
                return data.get("backgrounds", []), data.get("knives", [])
        except:
            pass
    return [], []  # по умолчанию ничего не разблокировано (кроме базовых)

def save_unlocked_skins(unlocked_backgrounds, unlocked_knives):
    """Сохраняет списки разблокированных скинов в файл."""
    try:
        with open(SKINS_FILE, "w") as f:
            json.dump({
                "backgrounds": unlocked_backgrounds,
                "knives": unlocked_knives
            }, f)
    except Exception as e:
        print(f"Ошибка сохранения скинов: {e}")

# ============================================================================
# Цвета
# ============================================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
WOOD_COLOR = (160, 120, 80)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
CYAN = (0, 255, 255)
SKY_BLUE = (135, 206, 235)
SAND = (238, 203, 173)
ICE_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)
LAVA_RED = (255, 69, 0)
SNOW_WHITE = (240, 248, 255)
KIWI_GREEN = (106, 153, 78)
KIWI_BROWN = (101, 67, 33)
SUNSET_ORANGE = (255, 140, 0)
SUNSET_PINK = (255, 105, 180)
NIGHT_BLUE = (25, 25, 112)
MOON_YELLOW = (255, 255, 224)
PINK = (255, 192, 203)
SILVER = (192, 192, 192)
BEIGE = (245, 245, 220)

# ============================================================================
# Функции создания текстур фонов (с проверкой наложения)
# ============================================================================

def clamp_color(r, g, b):
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

def distance_between(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)

def create_wood_texture(width, height):
    surf = pygame.Surface((width, height))
    for y in range(height):
        r = WOOD_COLOR[0] - y // 20
        g = WOOD_COLOR[1] - y // 20
        b = WOOD_COLOR[2] - y // 20
        color = clamp_color(r, g, b)
        pygame.draw.line(surf, color, (0, y), (width, y))
    step = int(60 * SCALE)
    for y in range(0, height, step):
        pygame.draw.line(surf, BLACK, (0, y), (width, y), int(2 * SCALE))
    return surf

def create_forest_texture(width, height):
    surf = pygame.Surface((width, height))
    for y in range(height):
        r = 135 - y // 20
        g = 206 - y // 20
        b = 235
        color = clamp_color(r, g, b)
        pygame.draw.line(surf, color, (0, y), (width, y))
    for y in range(height // 2, height):
        r = 34
        g = 139
        b = 34
        color = clamp_color(r, g, b)
        pygame.draw.line(surf, color, (0, y), (width, y))
    trees = []
    for _ in range(12):
        attempts = 0
        placed = False
        while attempts < 50 and not placed:
            x = random.randint(int(80 * SCALE), width - int(80 * SCALE))
            y = height - int(200 * SCALE) + random.randint(-20, 20)
            ok = True
            for tx, ty in trees:
                if distance_between(x, y, tx, ty) < int(120 * SCALE):
                    ok = False
                    break
            if ok:
                trees.append((x, y))
                placed = True
            attempts += 1
        if placed:
            pygame.draw.rect(surf, (101, 67, 33), (x, y, int(20 * SCALE), int(200 * SCALE)))
            pygame.draw.circle(surf, (0, 100, 0), (x + int(10 * SCALE), y - int(20 * SCALE)), int(40 * SCALE))
    return surf

def create_beach_texture(width, height):
    surf = pygame.Surface((width, height))
    for y in range(int(200 * SCALE)):
        r = 135
        g = 206 - y // 10
        b = 235 - y // 20
        color = clamp_color(r, g, b)
        pygame.draw.line(surf, color, (0, y), (width, y))
    for y in range(int(200 * SCALE), height):
        r = 238 - y // 50
        g = 203 - y // 50
        b = 173 - y // 50
        color = clamp_color(r, g, b)
        pygame.draw.line(surf, color, (0, y), (width, y))
    pygame.draw.rect(surf, SKY_BLUE, (0, 0, width, int(200 * SCALE)))
    for x in range(0, width, int(40 * SCALE)):
        pygame.draw.arc(surf, WHITE, (x, int(150 * SCALE), int(60 * SCALE), int(40 * SCALE)), 0, math.pi, int(3 * SCALE))
    return surf

def create_mountain_texture(width, height):
    surf = pygame.Surface((width, height))
    for y in range(height):
        r = 200 - y // 10
        g = 200 - y // 10
        b = 255
        color = clamp_color(r, g, b)
        pygame.draw.line(surf, color, (0, y), (width, y))
    points = [(0, height), (int(200 * SCALE), int(300 * SCALE)), (int(400 * SCALE), int(500 * SCALE)),
              (int(600 * SCALE), int(200 * SCALE)), (int(800 * SCALE), int(400 * SCALE)),
              (int(1020 * SCALE), int(100 * SCALE)), (int(1020 * SCALE), height)]
    pygame.draw.polygon(surf, (139, 137, 137), points)
    pygame.draw.polygon(surf, (169, 169, 169), points, int(5 * SCALE))
    pygame.draw.polygon(surf, WHITE, [(int(150 * SCALE), int(320 * SCALE)), (int(200 * SCALE), int(280 * SCALE)),
                                      (int(250 * SCALE), int(320 * SCALE))])
    return surf

def create_space_texture(width, height):
    surf = pygame.Surface((width, height))
    for y in range(height):
        r = 25 + y // 50
        g = 25 + y // 50
        b = 112 + y // 20
        color = clamp_color(r, g, b)
        pygame.draw.line(surf, color, (0, y), (width, y))
    stars = []
    for _ in range(150):
        attempts = 0
        placed = False
        while attempts < 50 and not placed:
            x = random.randint(0, width)
            y = random.randint(0, height)
            ok = True
            for sx, sy in stars:
                if distance_between(x, y, sx, sy) < int(10 * SCALE):
                    ok = False
                    break
            if ok:
                stars.append((x, y))
                placed = True
            attempts += 1
        if placed:
            r = random.randint(1, int(3 * SCALE))
            brightness = random.randint(150, 255)
            pygame.draw.circle(surf, (brightness, brightness, brightness), (x, y), r)
    return surf

def create_desert_texture(width, height):
    surf = pygame.Surface((width, height))
    for y in range(height):
        r = 255 - y // 10
        g = 200 - y // 10
        b = 150 - y // 20
        color = clamp_color(r, g, b)
        pygame.draw.line(surf, color, (0, y), (width, y))
    for y in range(height // 2, height):
        r = 238 - y // 100
        g = 203 - y // 100
        b = 173 - y // 100
        color = clamp_color(r, g, b)
        pygame.draw.line(surf, color, (0, y), (width, y))
    cacti = []
    for _ in range(8):
        attempts = 0
        placed = False
        while attempts < 50 and not placed:
            x = random.randint(int(80 * SCALE), width - int(80 * SCALE))
            y = height - int(150 * SCALE) + random.randint(-20, 20)
            ok = True
            for cx, cy in cacti:
                if distance_between(x, y, cx, cy) < int(120 * SCALE):
                    ok = False
                    break
            if ok:
                cacti.append((x, y))
                placed = True
            attempts += 1
        if placed:
            pygame.draw.rect(surf, (0, 128, 0), (x, y, int(15 * SCALE), int(150 * SCALE)))
            pygame.draw.ellipse(surf, (0, 128, 0), (x - int(20 * SCALE), y - int(30 * SCALE), int(50 * SCALE), int(40 * SCALE)))
    return surf

def create_snow_texture(width, height):
    surf = pygame.Surface((width, height))
    for y in range(height):
        val = 200 + y // 20
        color = clamp_color(val, val, val)
        pygame.draw.line(surf, color, (0, y), (width, y))
    snowflakes = []
    for _ in range(100):
        attempts = 0
        placed = False
        while attempts < 50 and not placed:
            x = random.randint(0, width)
            y = random.randint(0, height)
            ok = True
            for sx, sy in snowflakes:
                if distance_between(x, y, sx, sy) < int(10 * SCALE):
                    ok = False
                    break
            if ok:
                snowflakes.append((x, y))
                placed = True
            attempts += 1
        if placed:
            r = random.randint(1, int(3 * SCALE))
            pygame.draw.circle(surf, WHITE, (x, y), r)
    return surf

def create_volcano_texture(width, height):
    surf = pygame.Surface((width, height))
    for y in range(height):
        val = 50 + y // 10
        color = clamp_color(val, val, val)
        pygame.draw.line(surf, color, (0, y), (width, y))
    points = [(0, height), (int(300 * SCALE), int(400 * SCALE)), (int(600 * SCALE), int(200 * SCALE)),
              (int(900 * SCALE), int(400 * SCALE)), (width, height)]
    pygame.draw.polygon(surf, (80, 80, 80), points)
    lava = []
    for _ in range(15):
        attempts = 0
        placed = False
        while attempts < 50 and not placed:
            x = random.randint(int(250 * SCALE), int(750 * SCALE))
            y = random.randint(int(300 * SCALE), int(550 * SCALE))
            ok = True
            for lx, ly in lava:
                if distance_between(x, y, lx, ly) < int(50 * SCALE):
                    ok = False
                    break
            if ok:
                lava.append((x, y))
                placed = True
            attempts += 1
        if placed:
            pygame.draw.circle(surf, LAVA_RED, (x, y), int(15 * SCALE))
    sparks = []
    for _ in range(20):
        attempts = 0
        placed = False
        while attempts < 50 and not placed:
            x = random.randint(int(250 * SCALE), int(750 * SCALE))
            y = random.randint(int(200 * SCALE), int(500 * SCALE))
            ok = True
            for spx, spy in sparks:
                if distance_between(x, y, spx, spy) < int(20 * SCALE):
                    ok = False
                    break
            if ok:
                sparks.append((x, y))
                placed = True
            attempts += 1
        if placed:
            pygame.draw.circle(surf, YELLOW, (x, y), int(3 * SCALE))
    return surf

def create_sunset_texture(width, height):
    surf = pygame.Surface((width, height))
    for y in range(height):
        r = SUNSET_ORANGE[0] - y // 20
        g = SUNSET_ORANGE[1] - y // 20
        b = SUNSET_PINK[2] + y // 30
        color = clamp_color(r, g, b)
        pygame.draw.line(surf, color, (0, y), (width, y))
    clouds = []
    for _ in range(8):
        attempts = 0
        placed = False
        while attempts < 50 and not placed:
            x = random.randint(int(100 * SCALE), width - int(100 * SCALE))
            y = random.randint(int(50 * SCALE), int(300 * SCALE))
            ok = True
            for cx, cy in clouds:
                if distance_between(x, y, cx, cy) < int(150 * SCALE):
                    ok = False
                    break
            if ok:
                clouds.append((x, y))
                placed = True
            attempts += 1
        if placed:
            pygame.draw.ellipse(surf, (255, 200, 200), (x, y, int(80 * SCALE), int(30 * SCALE)))
    return surf

def create_night_texture(width, height):
    surf = pygame.Surface((width, height))
    for y in range(height):
        r = NIGHT_BLUE[0] + y // 30
        g = NIGHT_BLUE[1] + y // 30
        b = NIGHT_BLUE[2] + y // 20
        color = clamp_color(r, g, b)
        pygame.draw.line(surf, color, (0, y), (width, y))
    pygame.draw.circle(surf, MOON_YELLOW, (int(800 * SCALE), int(200 * SCALE)), int(50 * SCALE))
    stars = []
    for _ in range(80):
        attempts = 0
        placed = False
        while attempts < 50 and not placed:
            x = random.randint(0, width)
            y = random.randint(0, height)
            if distance_between(x, y, int(800 * SCALE), int(200 * SCALE)) < int(100 * SCALE):
                continue
            ok = True
            for sx, sy in stars:
                if distance_between(x, y, sx, sy) < int(20 * SCALE):
                    ok = False
                    break
            if ok:
                stars.append((x, y))
                placed = True
            attempts += 1
        if placed:
            r = random.randint(1, int(2 * SCALE))
            pygame.draw.circle(surf, WHITE, (x, y), r)
    return surf

wood_bg = create_wood_texture(SCREEN_WIDTH, SCREEN_HEIGHT)
forest_bg = create_forest_texture(SCREEN_WIDTH, SCREEN_HEIGHT)
beach_bg = create_beach_texture(SCREEN_WIDTH, SCREEN_HEIGHT)
mountain_bg = create_mountain_texture(SCREEN_WIDTH, SCREEN_HEIGHT)
space_bg = create_space_texture(SCREEN_WIDTH, SCREEN_HEIGHT)
desert_bg = create_desert_texture(SCREEN_WIDTH, SCREEN_HEIGHT)
snow_bg = create_snow_texture(SCREEN_WIDTH, SCREEN_HEIGHT)
volcano_bg = create_volcano_texture(SCREEN_WIDTH, SCREEN_HEIGHT)
sunset_bg = create_sunset_texture(SCREEN_WIDTH, SCREEN_HEIGHT)
night_bg = create_night_texture(SCREEN_WIDTH, SCREEN_HEIGHT)

# ============================================================================
# Параллакс-слои
# ============================================================================
class ParallaxLayer:
    def __init__(self, speed, color, density):
        self.speed = speed * SCALE
        self.color = color
        self.particles = []
        for _ in range(density):
            self.particles.append([random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)])

    def update(self):
        for p in self.particles:
            p[0] += self.speed
            if p[0] > SCREEN_WIDTH:
                p[0] = 0
            elif p[0] < 0:
                p[0] = SCREEN_WIDTH

    def draw(self, surface):
        for p in self.particles:
            pygame.draw.circle(surface, self.color, (int(p[0]), int(p[1])), int(1 * SCALE))

# ============================================================================
# Классы скинов
# ============================================================================
class Skin:
    __slots__ = ('name', 'texture', 'locked')
    def __init__(self, name, texture, locked=True):
        self.name = name
        self.texture = texture
        self.locked = locked

class KnifeSkin:
    __slots__ = ('name', 'color', 'locked')
    def __init__(self, name, color, locked=True):
        self.name = name
        self.color = color
        self.locked = locked

# ============================================================================
# Класс фрукта/объекта
# ============================================================================
class Fruit:
    __slots__ = ('x', 'y', 'speed_x', 'speed_y', 'fruit_type', 'radius', 'sliced',
                 'sliced_pieces', 'gravity', 'color', 'rainbow_offset', 'scale')
    
    def __init__(self, x, y, speed_x, speed_y, fruit_type, scale):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.fruit_type = fruit_type
        self.scale = scale
        if fruit_type in ["skin_box", "knife_box"]:
            self.radius = int(40 * scale)
        else:
            self.radius = int(30 * scale)
        self.sliced = False
        self.sliced_pieces = []
        self.gravity = 0.25
        
        colors = {
            "apple": RED,
            "banana": YELLOW,
            "orange": ORANGE,
            "watermelon": GREEN,
            "kiwi": KIWI_GREEN,
            "bomb": BLACK,
            "skin_box": PURPLE,
            "knife_box": CYAN,
            "icy_banana": ICE_BLUE,
            "golden_banana": GOLD,
            "rainbow_banana": WHITE
        }
        self.color = colors.get(fruit_type, WHITE)
        self.rainbow_offset = random.randint(0, 360)
    
    def update(self):
        if not self.sliced:
            self.x += self.speed_x
            self.y += self.speed_y
            self.speed_y += self.gravity
        else:
            for piece in self.sliced_pieces[:]:
                piece["x"] += piece["speed_x"]
                piece["y"] += piece["speed_y"]
                piece["speed_y"] += self.gravity
                piece["life"] -= 1
                if piece["life"] <= 0:
                    self.sliced_pieces.remove(piece)
    
    def draw(self, surface):
        if not self.sliced:
            s = self.scale
            if self.fruit_type == "apple":
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
                pygame.draw.line(surface, BROWN, (self.x-5*s, self.y-self.radius), (self.x-10*s, self.y-self.radius-10*s), int(3*s))
                pygame.draw.polygon(surface, GREEN, [(self.x-12*s, self.y-self.radius-10*s), (self.x-20*s, self.y-self.radius-20*s), (self.x-5*s, self.y-self.radius-20*s)])
            elif self.fruit_type == "banana":
                rect = pygame.Rect(self.x-self.radius+10*s, self.y-self.radius+5*s, self.radius*2-20*s, self.radius-10*s)
                pygame.draw.ellipse(surface, self.color, rect)
                pygame.draw.ellipse(surface, BROWN, (self.x-15*s, self.y-15*s, 10*s, 10*s))
                pygame.draw.ellipse(surface, BROWN, (self.x+5*s, self.y-10*s, 10*s, 10*s))
            elif self.fruit_type == "orange":
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
                for _ in range(8):
                    dx = random.randint(-10,10) * s
                    dy = random.randint(-10,10) * s
                    if dx*dx + dy*dy < (self.radius-5*s)**2:
                        pygame.draw.circle(surface, (200,100,0), (int(self.x+dx), int(self.y+dy)), int(2*s))
            elif self.fruit_type == "watermelon":
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
                pygame.draw.arc(surface, DARK_GREEN, (self.x-20*s, self.y-20*s, 40*s, 40*s), 0, math.pi, int(3*s))
                pygame.draw.arc(surface, DARK_GREEN, (self.x-25*s, self.y-25*s, 50*s, 50*s), math.pi, 2*math.pi, int(3*s))
                pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius-10*s)
                for i in range(3):
                    pygame.draw.ellipse(surface, BLACK, (self.x-5*s + i*5*s, self.y-5*s, 5*s, 8*s))
            elif self.fruit_type == "kiwi":
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
                pygame.draw.circle(surface, (144, 238, 144), (int(self.x), int(self.y)), self.radius-5*s)
                for _ in range(5):
                    angle = random.uniform(0, 2*math.pi)
                    dx = math.cos(angle) * (self.radius-10*s)
                    dy = math.sin(angle) * (self.radius-10*s)
                    pygame.draw.circle(surface, KIWI_BROWN, (int(self.x+dx), int(self.y+dy)), int(3*s))
            elif self.fruit_type == "bomb":
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
                pygame.draw.line(surface, BROWN, (self.x+10*s, self.y-20*s), (self.x+20*s, self.y-30*s), int(3*s))
                for i in range(3):
                    x = self.x+20*s + random.randint(-5,5)*s
                    y = self.y-30*s + random.randint(-5,5)*s
                    pygame.draw.circle(surface, RED, (int(x), int(y)), int(2*s))
            elif self.fruit_type == "skin_box":
                rect = pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)
                pygame.draw.rect(surface, self.color, rect)
                pygame.draw.rect(surface, YELLOW, rect, int(4*s))
                font = pygame.font.Font(None, int(40 * self.scale))
                text = font.render("?", True, YELLOW)
                text_rect = text.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(text, text_rect)
            elif self.fruit_type == "knife_box":
                rect = pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)
                pygame.draw.rect(surface, self.color, rect)
                pygame.draw.rect(surface, WHITE, rect, int(4*s))
                font = pygame.font.Font(None, int(40 * self.scale))
                text = font.render("🔪", True, WHITE)
                text_rect = text.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(text, text_rect)
            elif self.fruit_type == "icy_banana":
                rect = pygame.Rect(self.x-self.radius+10*s, self.y-self.radius+5*s, self.radius*2-20*s, self.radius-10*s)
                pygame.draw.ellipse(surface, self.color, rect)
                for i in range(5):
                    x = self.x - 15*s + i*10*s
                    y = self.y - 25*s
                    pygame.draw.polygon(surface, WHITE, [(x, y), (x+5*s, y+15*s), (x-5*s, y+15*s)])
            elif self.fruit_type == "golden_banana":
                rect = pygame.Rect(self.x-self.radius+10*s, self.y-self.radius+5*s, self.radius*2-20*s, self.radius-10*s)
                pygame.draw.ellipse(surface, self.color, rect)
                for i in range(3):
                    angle = random.uniform(0, 2*math.pi)
                    dx = math.cos(angle) * 15 * s
                    dy = math.sin(angle) * 15 * s
                    pygame.draw.circle(surface, YELLOW, (int(self.x+dx), int(self.y+dy)), int(3*s))
            elif self.fruit_type == "rainbow_banana":
                hue = (pygame.time.get_ticks() // 10 + self.rainbow_offset) % 360
                color = pygame.Color(0)
                color.hsva = (hue, 100, 100, 100)
                rect = pygame.Rect(self.x-self.radius+10*s, self.y-self.radius+5*s, self.radius*2-20*s, self.radius-10*s)
                pygame.draw.ellipse(surface, color, rect)
                for i in range(2):
                    angle = random.uniform(0, 2*math.pi)
                    dx = math.cos(angle) * 20 * s
                    dy = math.sin(angle) * 20 * s
                    pygame.draw.circle(surface, WHITE, (int(self.x+dx), int(self.y+dy)), int(2*s))
            else:
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        else:
            for piece in self.sliced_pieces:
                pygame.draw.circle(surface, piece["color"], (int(piece["x"]), int(piece["y"])), int(piece["size"]))
    
    def slice(self):
        if not self.sliced:
            self.sliced = True
            s = self.scale
            for i in range(3):
                piece = {
                    "x": self.x,
                    "y": self.y,
                    "speed_x": random.uniform(-5, 5) * s,
                    "speed_y": random.uniform(-8, -4) * s,
                    "color": self.color,
                    "size": random.randint(5, 10) * s,
                    "life": 15
                }
                self.sliced_pieces.append(piece)
            if self.fruit_type == "bomb":
                return -1, "bomb"
            elif self.fruit_type == "golden_banana":
                return 100, "golden_banana"
            elif self.fruit_type == "rainbow_banana":
                return 0, "rainbow_banana"
            elif self.fruit_type in ["apple","banana","orange","watermelon","kiwi","icy_banana"]:
                return 10, self.fruit_type
            else:
                return 0, self.fruit_type
        return 0, None
    
    def is_off_screen(self):
        margin = int(50 * self.scale)
        return (self.y > SCREEN_HEIGHT + margin or 
                self.y < -margin * 4 or
                self.x < -margin or 
                self.x > SCREEN_WIDTH + margin)

# ============================================================================
# Основной класс игры
# ============================================================================
class Game:
    __slots__ = ('mode', 'score', 'lives', 'fruits', 'fruit_counter', 
                 'fruit_speed_factor', 'spawn_speed_factor',
                 'all_skins', 'current_skin_index', 'all_knife_skins', 'current_knife_index',
                 'speed_multiplier', 'running', 'game_over', 'paused',
                 'spawn_timer', 'touch_start', 'touch_active', 'touch_positions', 'trail_points',
                 'trail_timer', 'base_speed_y', 'base_speed_x', 'base_spawn_delay',
                 'skin_menu_tab', 'go_menu_rect', 'go_restart_rect',
                 'increment_speed', 'max_speed', 'freeze_timer', 'highscores',
                 'parallax_layers', 'rainbow_mode_timer', 'rainbow_speed_multiplier',
                 'scale', 'device_type')
    
    def __init__(self, scale, device_type):
        self.scale = scale
        self.device_type = device_type
        self.mode = None
        self.score = 0
        self.lives = 3
        self.fruits = []
        self.fruit_counter = 0
        
        self.fruit_speed_factor = 1.0
        self.spawn_speed_factor = 1.0
        
        # Загружаем разблокированные скины
        unlocked_backgrounds, unlocked_knives = load_unlocked_skins()
        
        # Создаём скины фона с учётом загруженных разблокированных
        self.all_skins = [
            Skin("Доски", wood_bg, False),  # базовый всегда разблокирован
            Skin("Лес", forest_bg, "Лес" not in unlocked_backgrounds),
            Skin("Пляж", beach_bg, "Пляж" not in unlocked_backgrounds),
            Skin("Горы", mountain_bg, "Горы" not in unlocked_backgrounds),
            Skin("Космос", space_bg, "Космос" not in unlocked_backgrounds),
            Skin("Пустыня", desert_bg, "Пустыня" not in unlocked_backgrounds),
            Skin("Снег", snow_bg, "Снег" not in unlocked_backgrounds),
            Skin("Вулкан", volcano_bg, "Вулкан" not in unlocked_backgrounds),
            Skin("Закат", sunset_bg, "Закат" not in unlocked_backgrounds),
            Skin("Ночь", night_bg, "Ночь" not in unlocked_backgrounds),
        ]
        self.current_skin_index = 0
        
        # Создаём скины ножа с учётом загруженных разблокированных
        self.all_knife_skins = [
            KnifeSkin("Белый", WHITE, False),  # базовый всегда разблокирован
            KnifeSkin("Радужный", None, "Радужный" not in unlocked_knives),
            KnifeSkin("Фиолетовый", PURPLE, "Фиолетовый" not in unlocked_knives),
            KnifeSkin("Красный", RED, "Красный" not in unlocked_knives),
            KnifeSkin("Зелёный", GREEN, "Зелёный" not in unlocked_knives),
            KnifeSkin("Голубой", CYAN, "Голубой" not in unlocked_knives),
            KnifeSkin("Оранжевый", ORANGE, "Оранжевый" not in unlocked_knives),
            KnifeSkin("Жёлтый", YELLOW, "Жёлтый" not in unlocked_knives),
            KnifeSkin("Розовый", PINK, "Розовый" not in unlocked_knives),
            KnifeSkin("Коричневый", BROWN, "Коричневый" not in unlocked_knives),
            KnifeSkin("Серебряный", SILVER, "Серебряный" not in unlocked_knives),
            KnifeSkin("Чёрный", BLACK, "Чёрный" not in unlocked_knives),
        ]
        self.current_knife_index = 0
        
        self.speed_multiplier = 1.0
        self.running = True
        self.game_over = False
        self.paused = False
        self.spawn_timer = 0
        
        self.touch_start = None
        self.touch_active = False
        self.touch_positions = []
        self.trail_points = deque(maxlen=8)
        self.trail_timer = 0
        
        self.base_speed_y = (-22, -20)
        self.base_speed_x = (-3, 3)
        self.base_spawn_delay = 60
        
        self.increment_speed = 0.03
        self.max_speed = 3.0
        
        self.skin_menu_tab = "background"
        self.go_menu_rect = None
        self.go_restart_rect = None
        
        self.freeze_timer = 0
        
        self.highscores = load_highscores()
        
        self.parallax_layers = [
            ParallaxLayer(1, LIGHT_GRAY, 50),
            ParallaxLayer(2, WHITE, 30)
        ]
        
        self.rainbow_mode_timer = 0
        self.rainbow_speed_multiplier = 3.1
        
        sound_manager.start_music()
    
    # ======== ПРАВИЛА ========
    def show_rules(self):
        rules_active = True
        
        if self.device_type == "phone":
            rules_lines = [
                "ПРАВИЛА:",
                "",
                "Ябл., Бан., Ап., Арб., Киви - 10 оч.",
                "Бомба - мгн. смерть",
                "Лед. банан - зам. 2 сек (редкий)",
                "Зол. банан - 100 оч (редкий)",
                "Радуж. банан - ультра 10 сек: только зол. бананы, без потерь (оч. редкий)",
                "Фиол. ящик - скин фона (особый)",
                "Гол. ящик - скин ножа (особый)",
                "",
                "Особый: каждые 7 фруктов - ящик",
                "Пропуск фрукта - потеря жизни (кроме ультра)",
                "Нажмите НАЗАД"
            ]
        elif self.device_type == "tablet":
            rules_lines = [
                "ПРАВИЛА ИГРЫ:",
                "",
                "Яблоко, Банан, Апельсин, Арбуз, Киви - 10 очков",
                "Бомба - мгновенная смерть",
                "Ледяной банан - заморозка ножа на 2 сек (редкий)",
                "Золотой банан - 100 очков (редкий)",
                "Радужный банан - ультра 10 сек: зол. бананы, без потерь (редкий)",
                "Фиолетовый ящик - скин фона (только особый реж.)",
                "Голубой ящик - скин ножа (только особый реж.)",
                "",
                "Особый режим: каждые 7 разрезанных фруктов - ящик со скином",
                "Пропуск фрукта - потеря жизни (кроме ультра)",
                "Нажмите НАЗАД"
            ]
        else:  # pc
            rules_lines = [
                "ПРАВИЛА ИГРЫ:",
                "",
                "Яблоко, Банан, Апельсин, Арбуз, Киви - 10 оч.",
                "Бомба - мгновенная смерть",
                "Ледяной банан - заморозка ножа на 2 сек (редкий)",
                "Золотой банан - 100 оч (редкий)",
                "Радужный банан - ультра 10 сек: только зол. бананы, без потерь (оч. редкий)",
                "Фиол. ящик - скин фона (только особый)",
                "Гол. ящик - скин ножа (только особый)",
                "",
                "Особый режим: каждые 7 фруктов - ящик со скином",
                "Пропуск фрукта - потеря жизни (кроме ультра)",
                "Нажмите НАЗАД"
            ]
        
        back_btn_rect = pygame.Rect(SCREEN_WIDTH//2 - int(150 * self.scale), SCREEN_HEIGHT - int(200 * self.scale), int(300 * self.scale), int(80 * self.scale))
        
        while rules_active:
            screen.blit(self.all_skins[self.current_skin_index].texture, (0, 0))
            
            x_offset = int(50 * self.scale)
            y = int(50 * self.scale)
            if self.device_type == "phone":
                line_spacing = int(32 * self.scale)
            elif self.device_type == "tablet":
                line_spacing = int(40 * self.scale)
            else:
                line_spacing = int(40 * self.scale)
            
            for line in rules_lines:
                text = font_rules.render(line, True, WHITE)
                screen.blit(text, (x_offset, y))
                y += line_spacing
            
            pygame.draw.rect(screen, YELLOW, back_btn_rect)
            pygame.draw.rect(screen, BLACK, back_btn_rect, int(3 * self.scale))
            back_text = font_medium.render("НАЗАД", True, BLACK)
            back_rect = back_text.get_rect(center=back_btn_rect.center)
            screen.blit(back_text, back_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pos = event.pos
                        if back_btn_rect.collidepoint(pos):
                            rules_active = False
            
            pygame.display.flip()
            clock.tick(FPS)
    
    # ======== ГЛАВНОЕ МЕНЮ ========
    def show_menu(self):
        menu_active = True
        
        if self.device_type == "tablet":
            extra_offset = int(250 * self.scale)
        elif self.device_type == "pc":
            extra_offset = int(500 * self.scale)
        else:
            extra_offset = 0
        
        base_y = SCREEN_HEIGHT // 3 - int(20 * self.scale) + extra_offset
        
        buttons = [
            {"text": "КЛАССИЧЕСКИЙ", "y": base_y + int(40 * self.scale), "mode": "classic"},
            {"text": "БЫСТРЫЙ", "y": base_y + int(140 * self.scale), "mode": "fast"},
            {"text": "ОСОБЫЙ", "y": base_y + int(240 * self.scale), "mode": "special"},
            {"text": "СКИНЫ", "y": base_y + int(340 * self.scale), "mode": "skins", "color": YELLOW},
            {"text": "ПРАВИЛА", "y": base_y + int(440 * self.scale), "mode": "rules", "color": CYAN},
            {"text": "ВЫХОД", "y": base_y + int(540 * self.scale), "mode": "exit", "color": RED},
        ]
        
        while menu_active:
            screen.blit(self.all_skins[self.current_skin_index].texture, (0, 0))
            
            title_y = int(50 * self.scale) + extra_offset // 2
            title = font_large.render("ФРУКТОВЫЙ", True, WHITE)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, title_y))
            
            if self.device_type in ["tablet", "pc"]:
                offset = int(120 * self.scale)
            else:
                offset = int(70 * self.scale)
            title2 = font_large.render("НИНДЗЯ 2.0", True, WHITE)
            screen.blit(title2, (SCREEN_WIDTH//2 - title2.get_width()//2, title_y + offset))
            
            rec_y = int(200 * self.scale) + extra_offset
            rec_classic = self.highscores.get("classic", 0)
            rec_fast = self.highscores.get("fast", 0)
            rec_text = font_small.render(f"Рекорд (Класс): {rec_classic}   Рекорд (Быстрый): {rec_fast}", True, WHITE)
            screen.blit(rec_text, (SCREEN_WIDTH//2 - rec_text.get_width()//2, rec_y))
            
            btn_rects = []
            for btn in buttons:
                color = btn.get("color", WHITE)
                surf = font_medium.render(btn["text"], True, color)
                rect = surf.get_rect(center=(SCREEN_WIDTH//2, btn["y"]))
                screen.blit(surf, rect)
                btn_rects.append((rect, btn["mode"]))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.touch_start = event.pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.touch_start:
                        pos = event.pos
                        for rect, mode in btn_rects:
                            if rect.collidepoint(pos):
                                sound_manager.play_button()
                                if mode == "exit":
                                    return False
                                elif mode == "skins":
                                    self.show_skin_menu()
                                elif mode == "rules":
                                    self.show_rules()
                                else:
                                    self.mode = mode
                                    if mode == "fast":
                                        self.speed_multiplier = 1.0
                                        self.increment_speed = 0.1
                                        self.lives = 5
                                    else:
                                        self.speed_multiplier = 1.0
                                        self.increment_speed = 0.03
                                        self.lives = 3
                                    self.fruit_counter = 0
                                    self.fruit_speed_factor = 1.0
                                    self.spawn_speed_factor = 1.0
                                    self.freeze_timer = 0
                                    self.rainbow_mode_timer = 0
                                    menu_active = False
                                break
                        self.touch_start = None
            
            pygame.display.flip()
            clock.tick(FPS)
        
        return True
    
    # ======== МЕНЮ СКИНОВ ========
    def show_skin_menu(self):
        skin_menu_active = True
        cols = 4
        rows = 3
        if self.device_type == "phone":
            item_width = int(180 * self.scale)
            item_height = int(180 * self.scale)
            margin = int(15 * self.scale)
        else:
            item_width = int(250 * self.scale)
            item_height = int(250 * self.scale)
            margin = int(30 * self.scale)

        total_width = cols * item_width + (cols - 1) * margin
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = int(250 * self.scale)

        bg_tab_rect = pygame.Rect(int(200 * self.scale), int(150 * self.scale), int(200 * self.scale), int(60 * self.scale))
        knife_tab_rect = pygame.Rect(int(450 * self.scale), int(150 * self.scale), int(200 * self.scale), int(60 * self.scale))
        back_btn_rect = pygame.Rect(int(50 * self.scale), SCREEN_HEIGHT - int(200 * self.scale), int(250 * self.scale), int(80 * self.scale))

        while skin_menu_active:
            screen.blit(self.all_skins[self.current_skin_index].texture, (0, 0))

            title = font_medium.render("ВЫБОР СКИНА", True, WHITE)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, int(80 * self.scale)))

            bg_color = YELLOW if self.skin_menu_tab == "background" else LIGHT_GRAY
            knife_color = YELLOW if self.skin_menu_tab == "knife" else LIGHT_GRAY
            pygame.draw.rect(screen, bg_color, bg_tab_rect)
            pygame.draw.rect(screen, BLACK, bg_tab_rect, int(3 * self.scale))
            bg_text = font_medium.render("ФОН", True, BLACK)
            screen.blit(bg_text, bg_text.get_rect(center=bg_tab_rect.center))

            pygame.draw.rect(screen, knife_color, knife_tab_rect)
            pygame.draw.rect(screen, BLACK, knife_tab_rect, int(3 * self.scale))
            knife_text = font_medium.render("НОЖ", True, BLACK)
            screen.blit(knife_text, knife_text.get_rect(center=knife_tab_rect.center))

            pygame.draw.rect(screen, YELLOW, back_btn_rect)
            pygame.draw.rect(screen, BLACK, back_btn_rect, int(4 * self.scale))
            back_text = font_large.render("← НАЗАД", True, BLACK)
            back_rect = back_text.get_rect(center=back_btn_rect.center)
            screen.blit(back_text, back_rect)

            items = self.all_skins if self.skin_menu_tab == "background" else self.all_knife_skins
            selected_index = self.current_skin_index if self.skin_menu_tab == "background" else self.current_knife_index

            for i, item in enumerate(items):
                row = i // cols
                col = i % cols
                x = start_x + col * (item_width + margin)
                y = start_y + row * (item_height + margin)
                rect = pygame.Rect(x, y, item_width, item_height)

                if self.skin_menu_tab == "background":
                    texture_scaled = pygame.transform.scale(item.texture, (item_width, item_height))
                    screen.blit(texture_scaled, rect.topleft)
                else:
                    if item.name == "Радужный" and not item.locked:
                        for j in range(6):
                            hue = (pygame.time.get_ticks() // 50 + j * 60) % 360
                            color = pygame.Color(0)
                            color.hsva = (hue, 100, 100, 100)
                            sub_rect = pygame.Rect(x + j * (item_width // 6), y, item_width // 6, item_height)
                            pygame.draw.rect(screen, color, sub_rect)
                    else:
                        color = item.color if item.color else WHITE
                        pygame.draw.rect(screen, color, rect)

                pygame.draw.rect(screen, BLACK, rect, int(3 * self.scale))

                if i == selected_index:
                    pygame.draw.rect(screen, YELLOW, rect, int(6 * self.scale))

                name_text = font_small.render(item.name, True, BLACK)
                screen.blit(name_text, (rect.centerx - name_text.get_width()//2, rect.bottom - int(30 * self.scale)))

                if item.locked:
                    overlay = pygame.Surface((item_width, item_height))
                    overlay.set_alpha(150)
                    overlay.fill(DARK_GRAY)
                    screen.blit(overlay, rect.topleft)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.touch_start = event.pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.touch_start:
                        pos = event.pos
                        if bg_tab_rect.collidepoint(pos) or knife_tab_rect.collidepoint(pos) or back_btn_rect.collidepoint(pos):
                            sound_manager.play_button()
                        if bg_tab_rect.collidepoint(pos):
                            self.skin_menu_tab = "background"
                        elif knife_tab_rect.collidepoint(pos):
                            self.skin_menu_tab = "knife"
                        elif back_btn_rect.collidepoint(pos):
                            skin_menu_active = False
                        else:
                            items = self.all_skins if self.skin_menu_tab == "background" else self.all_knife_skins
                            for i, item in enumerate(items):
                                row = i // cols
                                col = i % cols
                                x = start_x + col * (item_width + margin)
                                y = start_y + row * (item_height + margin)
                                rect = pygame.Rect(x, y, item_width, item_height)
                                if rect.collidepoint(pos) and not item.locked:
                                    if self.skin_menu_tab == "background":
                                        self.current_skin_index = i
                                        sound_manager.play_button()
                                    else:
                                        self.current_knife_index = i
                                        sound_manager.play_button()
                                    break
                        self.touch_start = None

            pygame.display.flip()
            clock.tick(FPS)
    
    # ======== СОЗДАНИЕ ОБЪЕКТОВ ========
    def spawn_object(self):
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
        
        current_delay = int(self.base_spawn_delay / self.spawn_speed_factor)
        if current_delay < 10:
            current_delay = 10
        
        if self.spawn_timer <= 0:
            if self.rainbow_mode_timer > 0:
                obj_type = "golden_banana"
            else:
                if self.mode == "special":
                    rand = random.random()
                    if rand < 0.4:
                        obj_type = "bomb"
                    elif rand < 0.7:
                        fruit_rand = random.random()
                        if fruit_rand < 0.10:
                            obj_type = "icy_banana"
                        else:
                            obj_type = random.choice(["apple", "banana", "orange", "watermelon", "kiwi"])
                    else:
                        obj_type = "kiwi"
                else:
                    rand = random.random()
                    if rand < 0.2:
                        obj_type = "bomb"
                    elif rand < 0.4:
                        obj_type = "kiwi"
                    else:
                        fruit_rand = random.random()
                        if fruit_rand < 0.10:
                            obj_type = "icy_banana"
                        elif fruit_rand < 0.11:
                            obj_type = "rainbow_banana"
                        elif fruit_rand < 0.16:
                            obj_type = "golden_banana"
                        else:
                            obj_type = random.choice(["apple", "banana", "orange", "watermelon"])
            
            if obj_type not in ["skin_box", "knife_box"]:
                self.fruit_speed_factor = min(self.fruit_speed_factor + self.increment_speed, self.max_speed)
                self.spawn_speed_factor = min(self.spawn_speed_factor + self.increment_speed, self.max_speed)
            
            # Определяем позицию и скорость в зависимости от множителя
            if self.fruit_speed_factor >= 2.5 and random.random() < 0.3:
                x = int(50 * self.scale)
                y = SCREEN_HEIGHT + int(50 * self.scale)
                speed_x = random.uniform(2, 4) * self.speed_multiplier * self.fruit_speed_factor
                speed_y = random.uniform(*self.base_speed_y) * self.speed_multiplier * self.fruit_speed_factor
            elif self.fruit_speed_factor >= 1.5 and random.random() < 0.3:
                x = SCREEN_WIDTH - int(50 * self.scale)
                y = SCREEN_HEIGHT + int(50 * self.scale)
                speed_x = -random.uniform(2, 4) * self.speed_multiplier * self.fruit_speed_factor
                speed_y = random.uniform(*self.base_speed_y) * self.speed_multiplier * self.fruit_speed_factor
            else:
                x = random.randint(int(80 * self.scale), SCREEN_WIDTH - int(80 * self.scale))
                y = SCREEN_HEIGHT + int(50 * self.scale)
                speed_x = random.uniform(*self.base_speed_x) * self.speed_multiplier * self.fruit_speed_factor
                speed_y = random.uniform(*self.base_speed_y) * self.speed_multiplier * self.fruit_speed_factor
            
            speed_mult = self.rainbow_speed_multiplier if self.rainbow_mode_timer > 0 else 1.0
            speed_y *= speed_mult
            speed_x *= speed_mult
            
            if self.device_type == "phone":
                fruit_scale = self.scale
            else:
                fruit_scale = self.scale * 1.5
            
            fruit = Fruit(x, y, speed_x, speed_y, obj_type, fruit_scale)
            self.fruits.append(fruit)
            
            self.spawn_timer = random.randint(current_delay, current_delay + 15)
        else:
            self.spawn_timer -= 1
    
    def spawn_chest_immediate(self):
        obj_type = random.choice(["skin_box", "knife_box"])
        x = random.randint(int(80 * self.scale), SCREEN_WIDTH - int(80 * self.scale))
        y = SCREEN_HEIGHT + int(50 * self.scale)
        speed_mult = self.rainbow_speed_multiplier if self.rainbow_mode_timer > 0 else 1.0
        speed_y = random.uniform(*self.base_speed_y) * self.speed_multiplier * self.fruit_speed_factor * speed_mult
        speed_x = random.uniform(*self.base_speed_x) * self.speed_multiplier * self.fruit_speed_factor * speed_mult
        
        if self.device_type == "phone":
            fruit_scale = self.scale
        else:
            fruit_scale = self.scale * 1.5
        
        chest = Fruit(x, y, speed_x, speed_y, obj_type, fruit_scale)
        self.fruits.append(chest)
    
    # ======== ОБРАБОТКА КАСАНИЙ ========
    def handle_touch_game(self):
        if self.freeze_timer > 0:
            return
        
        if self.touch_active and len(self.touch_positions) > 0:
            self.trail_points.append(self.touch_positions[-1])
            self.trail_timer = 10
            
            if len(self.touch_positions) >= 2:
                x1, y1 = self.touch_positions[-2]
                x2, y2 = self.touch_positions[-1]
                for fruit in self.fruits[:]:
                    if fruit.sliced:
                        continue
                    dist = self.point_to_line_distance(fruit.x, fruit.y, x1, y1, x2, y2)
                    if dist < fruit.radius + 8 * self.scale:
                        points, ftype = fruit.slice()
                        if points == -1:
                            self.game_over = True
                            return
                        else:
                            self.score += points
                            if ftype != "bomb":
                                sound_manager.play_slice()
                            
                            if ftype == "icy_banana":
                                self.freeze_timer = 2 * FPS
                            elif ftype == "rainbow_banana":
                                self.rainbow_mode_timer = 10 * FPS
                            
                            if ftype == "skin_box":
                                locked = [s for s in self.all_skins if s.locked]
                                if locked:
                                    chosen = random.choice(locked)
                                    chosen.locked = False
                                    self.show_message(f"Скин фона: {chosen.name}!")
                                    # Сохраняем разблокированные скины
                                    unlocked_bg = [s.name for s in self.all_skins if not s.locked]
                                    unlocked_kn = [k.name for k in self.all_knife_skins if not k.locked]
                                    save_unlocked_skins(unlocked_bg, unlocked_kn)
                            elif ftype == "knife_box":
                                locked = [k for k in self.all_knife_skins if k.locked]
                                if locked:
                                    chosen = random.choice(locked)
                                    chosen.locked = False
                                    self.show_message(f"Скин ножа: {chosen.name}!")
                                    # Сохраняем разблокированные скины
                                    unlocked_bg = [s.name for s in self.all_skins if not s.locked]
                                    unlocked_kn = [k.name for k in self.all_knife_skins if not k.locked]
                                    save_unlocked_skins(unlocked_bg, unlocked_kn)
                            
                            if self.mode == "special":
                                if ftype in ["apple","banana","orange","watermelon","kiwi","icy_banana","golden_banana"]:
                                    self.fruit_counter += 1
                                    if self.fruit_counter >= 7:
                                        self.fruit_counter = 0
                                        self.spawn_chest_immediate()
        else:
            if self.trail_timer > 0:
                self.trail_timer -= 1
            else:
                self.trail_points.clear()
    
    def point_to_line_distance(self, px, py, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        t = ((px - x1)*dx + (py - y1)*dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))
        proj_x = x1 + t*dx
        proj_y = y1 + t*dy
        return math.hypot(px - proj_x, py - proj_y)
    
    def show_message(self, text):
        msg_surf = font_medium.render(text, True, YELLOW)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(msg_surf, msg_rect)
        pygame.display.flip()
        pygame.time.wait(1500)
    
    # ======== ОБНОВЛЕНИЕ ========
    def update(self):
        if not self.game_over and not self.paused:
            if self.freeze_timer > 0:
                self.freeze_timer -= 1
            if self.rainbow_mode_timer > 0:
                self.rainbow_mode_timer -= 1
            
            self.spawn_object()
            self.handle_touch_game()
            
            for layer in self.parallax_layers:
                layer.update()
            
            if len(self.fruits) > 20:
                self.fruits = self.fruits[-20:]
            
            for fruit in self.fruits[:]:
                fruit.update()
                
                if fruit.sliced and len(fruit.sliced_pieces) == 0:
                    self.fruits.remove(fruit)
                    continue
                
                if fruit.is_off_screen():
                    if not fruit.sliced and fruit.fruit_type not in ["skin_box", "knife_box", "bomb", "icy_banana"]:
                        if self.rainbow_mode_timer <= 0:
                            self.lives -= 1
                            if self.lives <= 0:
                                self.game_over = True
                    self.fruits.remove(fruit)
    
    # ======== ОТРИСОВКА ЛИНИИ ========
    def draw_trail(self):
        if self.freeze_timer > 0:
            return
        if len(self.trail_points) < 2:
            return
        knife = self.all_knife_skins[self.current_knife_index]
        if knife.name == "Радужный" and not knife.locked:
            rainbow_offset = (pygame.time.get_ticks() // 50) % 360
            for i in range(len(self.trail_points)-1):
                hue = (rainbow_offset + i * 30) % 360
                color = pygame.Color(0)
                color.hsva = (hue, 100, 100, 100)
                start = self.trail_points[i]
                end = self.trail_points[i+1]
                pygame.draw.line(screen, color, start, end, int(12 * self.scale))
        else:
            color = knife.color if knife.color else WHITE
            points = list(self.trail_points)
            if len(points) >= 2:
                pygame.draw.lines(screen, color, False, points, int(12 * self.scale))
    
    # ======== ОТРИСОВКА ========
    def draw(self):
        skin = self.all_skins[self.current_skin_index]
        screen.blit(skin.texture, (0, 0))
        
        if skin.name in ["Космос", "Снег", "Ночь"]:
            for layer in self.parallax_layers:
                layer.draw(screen)
        
        for fruit in self.fruits:
            fruit.draw(screen)
        
        self.draw_trail()
        
        if self.mode != "special":
            score_text = font_small.render(f"Очки: {self.score}", True, WHITE)
            screen.blit(score_text, (int(20 * self.scale), int(20 * self.scale)))
        else:
            counter_text = font_small.render(f"До ящика: {7 - self.fruit_counter}", True, WHITE)
            screen.blit(counter_text, (int(20 * self.scale), int(20 * self.scale)))
        
        lives_text = font_small.render(f"Жизни: {self.lives}", True, WHITE)
        screen.blit(lives_text, (int(20 * self.scale), int(60 * self.scale)))
        
        if self.rainbow_mode_timer > 0:
            seconds = (self.rainbow_mode_timer // FPS) + 1
            rainbow_text = font_medium.render(f"РАДУГА: {seconds}", True, (255, 0, 255))
            screen.blit(rainbow_text, (SCREEN_WIDTH//2 - rainbow_text.get_width()//2, int(100 * self.scale)))
        
        mode_text = font_small.render(f"Режим: {self.mode}", True, WHITE)
        screen.blit(mode_text, (SCREEN_WIDTH - int(250 * self.scale), int(20 * self.scale)))
        
        skin_name = self.all_skins[self.current_skin_index].name
        skin_text = font_small.render(f"Фон: {skin_name}", True, WHITE)
        screen.blit(skin_text, (SCREEN_WIDTH//2 - int(50 * self.scale), int(20 * self.scale)))
        
        knife_name = self.all_knife_skins[self.current_knife_index].name
        knife_text = font_small.render(f"Нож: {knife_name}", True, WHITE)
        screen.blit(knife_text, (SCREEN_WIDTH//2 - int(50 * self.scale), int(60 * self.scale)))
        
        if self.freeze_timer > 0:
            freeze_text = font_medium.render("ЗАМОРОЗКА", True, ICE_BLUE)
            screen.blit(freeze_text, (SCREEN_WIDTH//2 - freeze_text.get_width()//2, SCREEN_HEIGHT//2))
        
        if self.paused:
            pause_text = font_medium.render("ПАУЗА", True, YELLOW)
            screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2))
        
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            go_text = font_large.render("ИГРА ОКОНЧЕНА", True, RED)
            go_text_rect = go_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - int(100 * self.scale)))
            screen.blit(go_text, go_text_rect)
            
            final_score = self.score
            if self.mode != "special":
                if self.mode == "classic" and final_score > self.highscores.get("classic", 0):
                    self.highscores["classic"] = final_score
                    save_highscores(self.highscores)
                elif self.mode == "fast" and final_score > self.highscores.get("fast", 0):
                    self.highscores["fast"] = final_score
                    save_highscores(self.highscores)
                score_final = font_large.render(f"{final_score}", True, WHITE)
            else:
                score_final = font_large.render("", True, WHITE)
            
            score_rect = score_final.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(score_final, score_rect)
            
            btn_y_offset = int(150 * self.scale)
            btn1 = font_medium.render("ГЛАВНОЕ МЕНЮ", True, YELLOW)
            btn1_rect = btn1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + btn_y_offset))
            screen.blit(btn1, btn1_rect)
            
            btn2 = font_medium.render("ИГРАТЬ СНОВА", True, GREEN)
            btn2_rect = btn2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + btn_y_offset + int(60 * self.scale)))
            screen.blit(btn2, btn2_rect)
            
            self.go_menu_rect = btn1_rect
            self.go_restart_rect = btn2_rect
        
        pygame.display.flip()
    
    # ======== ОБРАБОТКА СОБЫТИЙ ========
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.touch_active = True
                    self.touch_positions = [event.pos]
                    self.trail_points.append(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if self.touch_active:
                    self.touch_positions.append(event.pos)
                    if len(self.touch_positions) > 5:
                        self.touch_positions.pop(0)
                    self.trail_points.append(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.touch_active = False
                    self.touch_positions.clear()
                    if self.game_over:
                        pos = event.pos
                        if self.go_menu_rect and self.go_menu_rect.collidepoint(pos):
                            return "menu"
                        if self.go_restart_rect and self.go_restart_rect.collidepoint(pos):
                            return "restart"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_over:
                        return False
                    else:
                        self.paused = not self.paused
                elif event.key == pygame.K_SPACE and self.game_over:
                    return "restart"
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
        return True
    
    # ======== СБРОС ========
    def reset(self):
        self.score = 0
        if self.mode == "fast":
            self.lives = 5
        else:
            self.lives = 3
        self.fruits.clear()
        self.fruit_counter = 0
        self.fruit_speed_factor = 1.0
        self.spawn_speed_factor = 1.0
        self.spawn_timer = 0
        self.game_over = False
        self.paused = False
        self.touch_active = False
        self.touch_positions.clear()
        self.trail_points.clear()
        self.trail_timer = 0
        self.go_menu_rect = None
        self.go_restart_rect = None
        self.freeze_timer = 0
        self.rainbow_mode_timer = 0
    
    # ======== ЗАПУСК ========
    def run(self):
        if not self.show_menu():
            return
        
        running = True
        while running:
            result = self.handle_events()
            if result is False:
                running = False
            elif result == "menu":
                if not self.show_menu():
                    running = False
                else:
                    self.reset()
            elif result == "restart":
                self.reset()
            
            self.update()
            self.draw()
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game(SCALE, DEVICE_TYPE)
    game.run()
