import math
import random
import sys
import pygame

# Sparta Arena - Windows PC Edition
# Controls: WASD/Arrow keys move, SPACE attack, LEFT SHIFT block, Q potion, ESC pause.

pygame.init()
pygame.display.set_caption("SPARTA ARENA - PC EDITION")
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 24, bold=True)
SMALL = pygame.font.SysFont("arial", 17)
MED = pygame.font.SysFont("arial", 32, bold=True)
BIG = pygame.font.SysFont("arial", 58, bold=True)

WHITE = (245, 239, 220)
GOLD = (242, 183, 56)
RED = (214, 66, 58)
DARK = (22, 25, 35)
PANEL = (25, 29, 42)
GREEN = (69, 192, 115)

CHARACTERS = [
    {"name": "LEONIDAS", "color": (196, 67, 52), "hp": 125, "damage": 25, "speed": 4.0, "desc": "Dengeli ve guclu"},
    {"name": "ATHENA", "color": (75, 151, 220), "hp": 100, "damage": 20, "speed": 5.0, "desc": "Hizli savasci"},
    {"name": "MAXIMUS", "color": (218, 160, 54), "hp": 150, "damage": 28, "speed": 3.4, "desc": "Yuksek can"},
    {"name": "HERCULES", "color": (142, 93, 188), "hp": 115, "damage": 32, "speed": 3.7, "desc": "Agir saldiri"},
]
MAPS = [
    {"name": "ANTIK ROMA", "ground": (145, 115, 76), "line": (185, 151, 104), "accent": (221, 193, 139)},
    {"name": "KADIM COL", "ground": (194, 157, 91), "line": (218, 182, 117), "accent": (242, 215, 152)},
    {"name": "KARLI KALE", "ground": (100, 128, 151), "line": (143, 171, 191), "accent": (218, 232, 240)},
    {"name": "KARANLIK ORMAN", "ground": (50, 88, 64), "line": (71, 112, 81), "accent": (132, 163, 103)},
]

state = "menu"
mode_index = 0  # 0 Classic, 1 Hot Potato
char_index = 0
map_index = 0
paused = False
player = None
enemies = []
particles = []
score = 0
wave = 1
time_left = 90.0
bomb_holder = None
bomb_timer = 7.0
message = ""
message_timer = 0.0
attack_cd = 0.0
potion_cd = 0.0
shake = 0.0


def text(surf, value, font, color, pos, center=True):
    im = font.render(str(value), True, color)
    r = im.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    surf.blit(im, r)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def say(value, duration=1.7):
    global message, message_timer
    message, message_timer = value, duration


class Fighter:
    def __init__(self, x, y, name, color, hp, damage, speed, is_player=False):
        self.x, self.y = float(x), float(y)
        self.name, self.color = name, color
        self.max_hp = hp
        self.hp = hp
        self.damage = damage
        self.speed = speed
        self.is_player = is_player
        self.radius = 20 if not is_player else 23
        self.face = (0, -1)
        self.attack_cd = random.uniform(0.15, 0.6)
        self.stun = 0.0
        self.blocking = False
        self.alive = True
        self.flash = 0.0
        self.potion_count = 2 if is_player else 0
        self.ai_phase = random.random() * 7

    def draw(self, surf):
        if not self.alive:
            return
        x, y = int(self.x), int(self.y)
        pygame.draw.ellipse(surf, (20, 20, 20), (x-self.radius, y+self.radius-3, self.radius*2, 11))
        body = (100, 200, 235) if self.flash > 0 else self.color
        pygame.draw.circle(surf, body, (x, y), self.radius)
        pygame.draw.circle(surf, (244, 219, 175), (x, y-5), int(self.radius*0.57))
        # Helmet crest
        pygame.draw.arc(surf, (238, 191, 75), (x-self.radius//2, y-self.radius, self.radius, self.radius), math.pi, math.tau, 4)
        # Facing marker
        fx, fy = self.face
        pygame.draw.circle(surf, DARK, (int(x+fx*8), int(y-5+fy*8)), 3)
        if self.blocking:
            pygame.draw.circle(surf, (100, 205, 255), (x, y), self.radius+7, 3)
        if self is bomb_holder:
            pygame.draw.circle(surf, (255, 222, 45), (x, y-self.radius-14), 9)
            pygame.draw.circle(surf, (255, 80, 40), (x, y-self.radius-14), 13, 2)
        # health bar
        bw = 54 if self.is_player else 44
        bh = 6
        ratio = clamp(self.hp / max(1, self.max_hp), 0, 1)
        pygame.draw.rect(surf, (42, 34, 34), (x-bw//2, y-self.radius-15, bw, bh), border_radius=3)
        pygame.draw.rect(surf, GREEN if ratio > .35 else RED, (x-bw//2, y-self.radius-15, int(bw*ratio), bh), border_radius=3)
        if self.is_player:
            text(surf, self.name, SMALL, WHITE, (x, y+self.radius+15))

    def hit(self, amount, source=None):
        global score, bomb_holder
        if not self.alive:
            return
        actual = amount * (0.28 if self.blocking else 1.0)
        self.hp -= actual
        self.flash = 0.12
        if source is not None:
            dx, dy = self.x-source.x, self.y-source.y
            d = max(1, math.hypot(dx, dy))
            self.x += dx/d*13
            self.y += dy/d*13
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            if self.is_player:
                say("SAVASCI DUSTU!", 3)
            else:
                score += 100
                burst(self.x, self.y, self.color, 14)
                if state == "game" and mode_index == 1 and bomb_holder is self:
                    alive = [e for e in enemies if e.alive]
                    if player and player.alive:
                        alive.append(player)
                    bomb_holder = random.choice(alive) if alive else None


def burst(x, y, color, count=8):
    for _ in range(count):
        a = random.random()*math.tau
        sp = random.uniform(1, 4)
        particles.append([x, y, math.cos(a)*sp, math.sin(a)*sp, random.uniform(.25, .65), color])


def new_enemy(i):
    edge = random.randrange(4)
    if edge == 0: x, y = random.randint(90, WIDTH-90), 105
    elif edge == 1: x, y = WIDTH-95, random.randint(110, HEIGHT-90)
    elif edge == 2: x, y = random.randint(90, WIDTH-90), HEIGHT-95
    else: x, y = 95, random.randint(110, HEIGHT-90)
    types = [
        ("GLADYATOR", (187, 75, 62), 66+wave*5, 11+wave, 2.0+min(wave*.04, .8)),
        ("MUHAFIZ", (75, 107, 155), 92+wave*6, 14+wave, 1.55+min(wave*.03, .7)),
        ("AKINCI", (147, 117, 65), 54+wave*4, 9+wave, 2.4+min(wave*.04, .8)),
    ]
    n, c, hp, damage, sp = random.choice(types)
    return Fighter(x, y, f"{n} {i+1}", c, hp, damage, sp)


def start_game():
    global player, enemies, score, wave, time_left, bomb_holder, bomb_timer
    global paused, particles, attack_cd, potion_cd, shake
    ch = CHARACTERS[char_index]
    player = Fighter(WIDTH/2, HEIGHT/2, ch["name"], ch["color"], ch["hp"], ch["damage"], ch["speed"], True)
    score, wave, time_left = 0, 1, 90.0
    enemies = [new_enemy(i) for i in range(4 if mode_index == 0 else 3)]
    particles = []
    paused = False
    attack_cd = potion_cd = shake = 0.0
    bomb_timer = 7.0
    candidates = enemies + [player]
    bomb_holder = random.choice(candidates) if mode_index == 1 else None
    say("SAVAS BASLADI!", 1.8)


def draw_arena(surf):
    m = MAPS[map_index]
    surf.fill(m["ground"])
    # stylized tiled ground
    for x in range(0, WIDTH, 64):
        pygame.draw.line(surf, m["line"], (x, 82), (x, HEIGHT), 1)
    for y in range(82, HEIGHT, 64):
        pygame.draw.line(surf, m["line"], (0, y), (WIDTH, y), 1)
    # arena rings
    pygame.draw.ellipse(surf, m["accent"], (WIDTH//2-325, HEIGHT//2-270, 650, 520), 6)
    pygame.draw.ellipse(surf, m["accent"], (WIDTH//2-285, HEIGHT//2-230, 570, 440), 2)
    # stone pillars around corners
    for x, y in [(70, 115), (WIDTH-70, 115), (70, HEIGHT-55), (WIDTH-70, HEIGHT-55)]:
        pygame.draw.rect(surf, (81, 73, 61), (x-19, y-14, 38, 28), border_radius=4)
        pygame.draw.rect(surf, m["accent"], (x-15, y-12, 30, 24), 2, border_radius=4)
    pygame.draw.rect(surf, (35, 29, 28), (0, 0, WIDTH, 82))
    text(surf, "SPARTA ARENA", MED, GOLD, (WIDTH//2, 27))
    text(surf, f"HARITA: {m['name']}", SMALL, WHITE, (WIDTH//2, 60))


def player_attack():
    global attack_cd, shake, bomb_holder, bomb_timer
    if not player or not player.alive or attack_cd > 0:
        return
    attack_cd = 0.42
    fx, fy = player.face
    hx, hy = player.x + fx*35, player.y + fy*35
    pygame.draw.circle(screen, GOLD, (int(hx), int(hy)), 27, 3)
    targets = [e for e in enemies if e.alive and dist(player, e) < 79]
    if mode_index == 1 and bomb_holder is player:
        # While carrying the bomb, a successful strike passes it away.
        targets = sorted(targets, key=lambda e: dist(player, e))
        if targets:
            bomb_holder = targets[0]
            bomb_timer = 7.0
            say("BOMBA RAKIBE GECTI!", 1.2)
            targets[0].hit(player.damage, player)
            return
    if targets:
        target = min(targets, key=lambda e: dist(player, e))
        target.hit(player.damage, player)
        burst(target.x, target.y, GOLD, 5)
        shake = 0.08
        if mode_index == 1 and bomb_holder is target:
            bomb_holder = player
            bomb_timer = 7.0
            say("BOMBA SANA GECTI!", 1.4)
    else:
        say("ISABET YOK", .35)


def move_actor(actor, dx, dy, dt):
    if dx or dy:
        length = max(1, math.hypot(dx, dy))
        dx, dy = dx/length, dy/length
        actor.face = (dx, dy)
        actor.x += dx*actor.speed*60*dt
        actor.y += dy*actor.speed*60*dt
    actor.x = clamp(actor.x, 42, WIDTH-42)
    actor.y = clamp(actor.y, 102, HEIGHT-40)


def game_update(dt, keys):
    global attack_cd, potion_cd, time_left, wave, enemies, bomb_holder, bomb_timer
    global state, message_timer, shake
    if not player:
        return
    if player.alive:
        dx = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
        player.blocking = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        move_actor(player, dx, dy, dt)
        if keys[pygame.K_SPACE]:
            player_attack()
        if keys[pygame.K_q] and potion_cd <= 0 and player.potion_count > 0 and player.hp < player.max_hp:
            player.hp = min(player.max_hp, player.hp+38)
            player.potion_count -= 1
            potion_cd = 0.35
            burst(player.x, player.y, GREEN, 12)
            say("IKSIR KULLANILDI", 1.0)
    attack_cd = max(0, attack_cd-dt)
    potion_cd = max(0, potion_cd-dt)
    for e in enemies:
        if not e.alive:
            continue
        e.flash = max(0, e.flash-dt)
        e.attack_cd = max(0, e.attack_cd-dt)
        e.stun = max(0, e.stun-dt)
        if e.stun > 0:
            continue
        # enemies chase the player; hot-potato carrier becomes more aggressive
        target = player
        if not player.alive:
            target = None
        if target is None:
            continue
        dx, dy = target.x-e.x, target.y-e.y
        d = max(1, math.hypot(dx, dy))
        if mode_index == 1 and bomb_holder is e:
            e.speed = min(3.1, e.speed + 0.001)
        if d > 44:
            move_actor(e, dx/d, dy/d, dt)
        else:
            e.face = (dx/d, dy/d)
            if e.attack_cd <= 0:
                e.attack_cd = random.uniform(.8, 1.25)
                if player.alive:
                    player.hit(e.damage, e)
                    if mode_index == 1 and bomb_holder is e:
                        bomb_holder = player
                        bomb_timer = 7.0
                        say("BOMBA SANA GECTI!", 1.0)
    # timed modes
    if mode_index == 1:
        time_left -= dt
        bomb_timer -= dt
        if bomb_timer <= 0:
            if bomb_holder is player and player.alive:
                player.hit(30, None)
                say("BOMBA PATLADI! -30 CAN", 1.2)
                alive = [e for e in enemies if e.alive]
                bomb_holder = random.choice(alive) if alive else player
            elif bomb_holder and bomb_holder.alive:
                bomb_holder.hit(40, None)
                say("BOMBA PATLADI!", 1.0)
                alive = [e for e in enemies if e.alive]
                bomb_holder = random.choice(alive + ([player] if player.alive else [])) if alive or player.alive else None
            bomb_timer = 7.0
        if time_left <= 0 and player.alive:
            state = "win"
            say("ZAFER! 90 SANIYE HAYATTA KALDIN", 4)
    else:
        if player.alive and not any(e.alive for e in enemies):
            wave += 1
            player.hp = min(player.max_hp, player.hp+20)
            player.potion_count = min(3, player.potion_count+1)
            enemies = [new_enemy(i) for i in range(min(3+wave, 10))]
            say(f"DALGA {wave}! +20 CAN, +1 IKSIR", 2)
    if player and not player.alive:
        state = "over"
    if mode_index == 1 and not player.alive:
        state = "over"
    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= dt
        if p[4] <= 0:
            particles.remove(p)
    if message_timer > 0:
        message_timer -= dt
    shake = max(0, shake-dt)


def draw_hud(surf):
    if not player:
        return
    # player stats panel
    pygame.draw.rect(surf, (23, 27, 35), (18, 96, 255, 94), border_radius=12)
    text(surf, f"{player.name}  |  SKOR {score}", SMALL, WHITE, (30, 106), center=False)
    pygame.draw.rect(surf, (60, 44, 44), (30, 134, 220, 17), border_radius=6)
    frac = clamp(player.hp/player.max_hp, 0, 1)
    pygame.draw.rect(surf, GREEN if frac > .35 else RED, (30, 134, int(220*frac), 17), border_radius=6)
    text(surf, f"CAN {int(player.hp)}/{player.max_hp}", SMALL, WHITE, (140, 142))
    text(surf, f"IKSIR: {player.potion_count}  [Q]", SMALL, (135, 225, 154), (30, 159), center=False)
    text(surf, "WASD/OK: HAREKET   SPACE: SALDIRI   SHIFT: BLOK", SMALL, WHITE, (WIDTH//2, HEIGHT-19))
    if mode_index == 0:
        text(surf, f"DALGA {wave}", FONT, GOLD, (WIDTH-100, 115))
        text(surf, f"DUSMAN: {sum(e.alive for e in enemies)}", SMALL, WHITE, (WIDTH-100, 146))
    else:
        text(surf, f"SURE {max(0,int(time_left))}s", MED, GOLD, (WIDTH-112, 112))
        text(surf, f"BOMBA: {max(0,int(bomb_timer))}s", FONT, RED, (WIDTH-112, 151))


def draw_menu():
    screen.fill((18, 22, 33))
    # decorative arena rings
    for rad in (160, 220, 280):
        pygame.draw.circle(screen, (44, 49, 62), (WIDTH//2, 240), rad, 2)
    text(screen, "SPARTA", BIG, GOLD, (WIDTH//2, 150))
    text(screen, "ARENA", BIG, WHITE, (WIDTH//2, 210))
    text(screen, "PC EDITION", MED, (149, 174, 196), (WIDTH//2, 267))
    opts = ["KLASIK ARENA - DALGALARI TEMIZLE", "SICAK PATATES - BOMBADAN KACIN"]
    for i, item in enumerate(opts):
        col = GOLD if i == mode_index else (190, 196, 208)
        mark = "> " if i == mode_index else "  "
        text(screen, mark+item, FONT, col, (WIDTH//2, 380+i*48))
    text(screen, "YUKARI / ASAGI: MOD SEC    ENTER: DEVAM", SMALL, WHITE, (WIDTH//2, 500))
    text(screen, "Tamamen klavye ile oynanir. Harici gorsel dosyasi gerekmez.", SMALL, (170, 180, 190), (WIDTH//2, 546))
    text(screen, "SPARTA WORLD", SMALL, GOLD, (WIDTH//2, HEIGHT-35))


def draw_select(title, index, items, subtitle):
    screen.fill((19, 24, 35))
    text(screen, "SPARTA ARENA", MED, GOLD, (WIDTH//2, 95))
    text(screen, title, BIG, WHITE, (WIDTH//2, 180))
    item = items[index]
    pygame.draw.rect(screen, (36, 43, 57), (WIDTH//2-240, 250, 480, 205), border_radius=20)
    if title == "SAVASCI SEC":
        pygame.draw.circle(screen, item["color"], (WIDTH//2, 314), 39)
        pygame.draw.circle(screen, (245, 217, 176), (WIDTH//2, 306), 22)
        text(screen, item["name"], MED, GOLD, (WIDTH//2, 380))
        text(screen, f"CAN {item['hp']}   HASAR {item['damage']}   HIZ {item['speed']}", SMALL, WHITE, (WIDTH//2, 418))
        text(screen, item["desc"], SMALL, (186, 199, 215), (WIDTH//2, 443))
    else:
        pygame.draw.rect(screen, item["ground"], (WIDTH//2-170, 275, 340, 110), border_radius=8)
        for xx in range(WIDTH//2-160, WIDTH//2+160, 32):
            pygame.draw.line(screen, item["line"], (xx, 280), (xx, 380), 1)
        pygame.draw.ellipse(screen, item["accent"], (WIDTH//2-95, 290, 190, 75), 3)
        text(screen, item["name"], MED, WHITE, (WIDTH//2, 415))
    text(screen, subtitle, FONT, GOLD, (WIDTH//2, 510))
    text(screen, "SOL / SAG OK: SECENEK   ENTER: ONAYLA   ESC: GERI", SMALL, WHITE, (WIDTH//2, 565))


def draw_end(title, subtitle):
    screen.fill((18, 22, 31))
    text(screen, title, BIG, GOLD if state == "win" else RED, (WIDTH//2, 230))
    text(screen, subtitle, MED, WHITE, (WIDTH//2, 310))
    text(screen, f"TOPLAM SKOR: {score}", FONT, GOLD, (WIDTH//2, 375))
    text(screen, "ENTER: YENIDEN OYNA     M: ANA MENU", FONT, WHITE, (WIDTH//2, 460))


def main():
    global screen, state, mode_index, char_index, map_index, paused, player, enemies
    running = True
    while running:
        dt = min(clock.tick(60)/1000.0, 0.04)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Preserve fixed game canvas scaling
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        mode_index = (mode_index-1) % 2
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        mode_index = (mode_index+1) % 2
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = "character"
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif state == "character":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        char_index = (char_index-1) % len(CHARACTERS)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        char_index = (char_index+1) % len(CHARACTERS)
                    elif event.key == pygame.K_RETURN:
                        state = "map"
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"
                elif state == "map":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        map_index = (map_index-1) % len(MAPS)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        map_index = (map_index+1) % len(MAPS)
                    elif event.key == pygame.K_RETURN:
                        start_game()
                        state = "game"
                    elif event.key == pygame.K_ESCAPE:
                        state = "character"
                elif state == "game":
                    if event.key == pygame.K_ESCAPE:
                        paused = not paused
                    elif paused and event.key == pygame.K_RETURN:
                        paused = False
                    elif paused and event.key == pygame.K_m:
                        state, paused = "menu", False
                    elif not paused and event.key == pygame.K_q:
                        # Actual potion use occurs in the update loop.
                        pass
                elif state in ("over", "win"):
                    if event.key == pygame.K_RETURN:
                        start_game()
                        state = "game"
                    elif event.key == pygame.K_m:
                        state = "menu"
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        keys = pygame.key.get_pressed()
        if state == "game" and not paused:
            game_update(dt, keys)

        if state == "menu":
            draw_menu()
        elif state == "character":
            draw_select("SAVASCI SEC", char_index, CHARACTERS, "HER SAVASCI FARKLI OZELLIGE SAHIP")
        elif state == "map":
            draw_select("HARITA SEC", map_index, MAPS, "ARENA ATMOSFERINI SEC")
        elif state == "game":
            draw_arena(screen)
            for p in particles:
                pygame.draw.circle(screen, p[5], (int(p[0]), int(p[1])), max(1, int(4*p[4])))
            for e in enemies:
                e.draw(screen)
            if player:
                player.draw(screen)
            draw_hud(screen)
            if message_timer > 0:
                pygame.draw.rect(screen, (24, 28, 37), (WIDTH//2-240, 87, 480, 42), border_radius=9)
                text(screen, message, FONT, GOLD, (WIDTH//2, 108))
            if paused:
                shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                shade.fill((0, 0, 0, 175))
                screen.blit(shade, (0, 0))
                text(screen, "DURAKLATILDI", BIG, GOLD, (WIDTH//2, 280))
                text(screen, "ENTER: DEVAM     M: ANA MENU     ESC: DEVAM", FONT, WHITE, (WIDTH//2, 370))
        elif state == "over":
            draw_end("OYUN BITTI", "Sparta savascisi bu turu kaybetti.")
        elif state == "win":
            draw_end("ZAFER!", "Sparta Arenasi senin!")

        # render fixed canvas into the current resizable window
        target = pygame.display.get_surface()
        if target.get_size() != (WIDTH, HEIGHT):
            scaled = pygame.transform.smoothscale(screen, target.get_size())
            target.fill((0, 0, 0))
            target.blit(scaled, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
