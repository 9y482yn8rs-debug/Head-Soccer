"""界面表现使用普通函数；计分与运动逻辑不放在这里。"""
import math
import pygame
from settings import (WIDTH, HEIGHT, FIELD_LEFT, FIELD_RIGHT,
                      GOAL_MIN, GOAL_MAX, KICK_REACH,
                      NAVY, RED, BLUE, YELLOW, CREAM, WHITE)
from field import project, depth_scale
from ai_settings import AI_LEVELS

START_BUTTON = pygame.Rect(465, 563, 350, 60)
MODE_BUTTONS = {"single": pygame.Rect(345, 231, 285, 46),
                "local": pygame.Rect(650, 231, 285, 46)}
DIFFICULTY_BUTTONS = {"easy": pygame.Rect(345, 295, 185, 40),
                      "normal": pygame.Rect(547, 295, 185, 40),
                      "hard": pygame.Rect(749, 295, 186, 40)}


def start_action_at(position, mode):
    for name, rect in MODE_BUTTONS.items():
        if rect.collidepoint(position):
            return "mode_" + name
    if mode == "single":
        for name, rect in DIFFICULTY_BUTTONS.items():
            if rect.collidepoint(position):
                return "difficulty_" + name
    if START_BUTTON.collidepoint(position):
        return "start"
    return None
AGAIN_BUTTON = pygame.Rect(465, 405, 350, 64)
HOME_BUTTON = pygame.Rect(465, 487, 350, 52)


def text(screen, fonts, words, size, color, center):
    image = fonts[size].render(words, True, color)
    screen.blit(image, image.get_rect(center=center))


def panel(screen, rect, color=CREAM, border=NAVY, radius=22):
    shadow = rect.move(0, 6)
    pygame.draw.rect(screen, NAVY, shadow, border_radius=radius)
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    pygame.draw.rect(screen, border, rect, width=3, border_radius=radius)


def button(screen, fonts, rect, label, mouse, pressed, primary=True):
    color = YELLOW if primary else WHITE
    if rect.collidepoint(mouse):
        color = (255, 229, 142) if primary else (226, 242, 255)
    visible = rect.copy()
    if pressed and rect.collidepoint(mouse):
        visible.y += 4
    panel(screen, visible, color, radius=18)
    text(screen, fonts, label, 26, NAVY, visible.center)


def ground_line(screen, color, points, width=2, closed=False):
    pygame.draw.lines(screen, color, closed, [project(x, y) for x, y in points], width)


def draw_field(screen, pictures, goals_in_front=False):
    screen.blit(pictures['pitch'], (0, 0))
    if goals_in_front:
        for side in ('left', 'right'):
            screen.blit(pictures['goal_fronts'][side], (0, 0))


def draw_shadows(screen, players, ball):
    shadow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for obj in [*players, ball]:
        x, y = project(obj.x, obj.y)
        scale = depth_scale(obj.y)
        radius = obj.radius * scale
        # 分层软边椭圆替代彩色脚底圈，让球员自然落在草地上。
        for index in range(8):
            spread = 1.48 - index * 0.10
            width = radius * 2 * spread
            height = radius * 0.57 * spread
            alpha = 8 + index * 6
            pygame.draw.ellipse(shadow, (28, 57, 24, alpha),
                                (x - width / 2 - 4 * scale, y - height / 2 + 2,
                                 width, height))
    screen.blit(shadow, (0, 0))


def aim_hint_alpha(player, ball):
    """靠近足球渐显；踢球动作中更清楚，远离球时不留常驻标记。"""
    if player.kick_time > 0:
        return 225
    distance = math.hypot(ball.x - player.x, ball.y - player.y)
    return round(165 * max(0.0, min(1.0, (170 - distance) / 100)))


def draw_direction(screen, player, ball):
    alpha = aim_hint_alpha(player, ball)
    if alpha == 0:
        return
    direction = player.kick_direction if player.kick_time > 0 else player.aim
    ax, ay = direction
    x, y = player.x, player.y
    # 无箭杆、无队色圆环；统一暖白色小尖角只传达瞄准信息。
    points = [project(x + ax * forward - ay * sideways,
                      y + ay * forward + ax * sideways)
              for forward, sideways in ((62, 0), (44, 8), (50, 0), (44, -8))]
    # 靠近屏幕边缘时整体挪回安全区域，不截断方向提示。
    shift_x = max(0, 8 - min(px for px, _ in points)) + min(0, WIDTH - 8 - max(px for px, _ in points))
    shift_y = max(0, 8 - min(py for _, py in points)) + min(0, HEIGHT - 8 - max(py for _, py in points))
    points = [(px + shift_x, py + shift_y) for px, py in points]
    min_x = min(p[0] for p in points) - 2
    min_y = min(p[1] for p in points) - 2
    width = max(p[0] for p in points) - min_x + 4
    height = max(p[1] for p in points) - min_y + 4
    hint = pygame.Surface((width, height), pygame.SRCALPHA)
    local = [(px - min_x, py - min_y) for px, py in points]
    pygame.draw.polygon(hint, (43, 72, 35, alpha // 2), [(px + 1, py + 1) for px, py in local])
    pygame.draw.polygon(hint, (255, 250, 220, alpha), local)
    screen.blit(hint, (min_x, min_y))


def draw_ball(screen, ball, picture):
    scale = depth_scale(ball.y)
    size = round(ball.radius * 2 * scale)
    picture = pygame.transform.smoothscale(picture, (size, size))
    rotated = pygame.transform.rotate(picture, ball.angle)
    x, y = project(ball.x, ball.y)
    screen.blit(rotated, rotated.get_rect(center=(x, round(y - ball.radius * scale))))


def draw_scene(screen, pictures, players, ball):
    draw_shadows(screen, players, ball)
    objects = [(player.y, 'player', player) for player in players]
    objects += [(ball.y, 'ball', ball), (GOAL_MAX, 'goal', 'left'), (GOAL_MAX, 'goal', 'right')]
    for _, kind, obj in sorted(objects, key=lambda item: item[0]):
        if kind == 'player':
            obj.draw(screen, pictures[obj.team])
            draw_direction(screen, obj, ball)
        elif kind == 'ball':
            draw_ball(screen, obj, pictures['ball'])
        else:
            screen.blit(pictures['goal_fronts'][obj], (0, 0))


def draw_hud(screen, pictures, fonts, red_score, blue_score, remaining, mode="local", difficulty="easy"):
    panel(screen, pygame.Rect(328, 20, 248, 78), RED)
    panel(screen, pygame.Rect(584, 20, 112, 78), NAVY)
    panel(screen, pygame.Rect(704, 20, 248, 78), BLUE)
    screen.blit(pictures["red_portrait"], (336, 27))
    screen.blit(pictures["blue_portrait"], (879, 27))
    text(screen, fonts, "玩家 1", 18, WHITE, (439, 41))
    text(screen, fonts, "红队", 20, WHITE, (439, 70))
    text(screen, fonts, str(red_score), 42, WHITE, (537, 58))
    text(screen, fonts, "电脑" if mode == "single" else "玩家 2", 18, WHITE, (841, 41))
    text(screen, fonts, AI_LEVELS[difficulty]["label"] if mode == "single" else "蓝队", 20, WHITE, (841, 70))
    text(screen, fonts, str(blue_score), 42, WHITE, (743, 58))
    seconds = math.ceil(remaining)
    clock_text = str(seconds // 60).zfill(2) + ":" + str(seconds % 60).zfill(2)
    color = YELLOW if seconds <= 10 else WHITE
    text(screen, fonts, clock_text, 30, color, (640, 51))
    text(screen, fonts, "剩余时间", 16, (191, 218, 238), (640, 80))
    text(screen, fonts, "HEAD SOCCER", 18, NAVY, (133, 40))
    text(screen, fonts, "单人对战 · " + AI_LEVELS[difficulty]["label"] if mode == "single" else "双人足球 · 友谊赛", 16, NAVY, (137, 65))
    text(screen, fonts, "Esc 首页 / F1 碰撞框", 16, NAVY, (1129, 47))


def shade(screen, alpha):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((12, 38, 64, alpha))
    screen.blit(overlay, (0, 0))


def choice_button(screen, fonts, rect, label, selected, hovered, pressed):
    visible = rect.move(0, 2 if pressed else 0)
    color = NAVY if selected else ((224, 239, 232) if hovered else (239, 243, 229))
    pygame.draw.rect(screen, color, visible, border_radius=12)
    pygame.draw.rect(screen, NAVY if selected else (186, 205, 188), visible, 2, border_radius=12)
    text(screen, fonts, label, 20, WHITE if selected else NAVY, visible.center)


def draw_start(screen, pictures, fonts, mouse, pressed, mode="single", difficulty="easy"):
    shade(screen, 45)
    for team, x in (("red", 55), ("blue", 935)):
        action = "idle" if team == "red" else "idle_left"
        hero = pygame.transform.smoothscale(pictures[team][action], (290, 290))
        screen.blit(hero, (x, 286))
    panel(screen, pygame.Rect(300, 115, 680, 580), CREAM, radius=30)
    text(screen, fonts, "大头足球对战", 42, NAVY, (640, 162))
    text(screen, fonts, "90 秒比赛 · 进球更多者获胜", 20, (80, 108, 125), (640, 203))
    for name, rect in MODE_BUTTONS.items():
        choice_button(screen, fonts, rect, "单人 VS 电脑" if name == "single" else "本地双人",
                      mode == name, rect.collidepoint(mouse), pressed == "mode_" + name)
    if mode == "single":
        for name, rect in DIFFICULTY_BUTTONS.items():
            label = AI_LEVELS[name]["label"] + (" / Hard" if name == "hard" else "")
            choice_button(screen, fonts, rect, label, difficulty == name,
                          rect.collidepoint(mouse), pressed == "difficulty_" + name)
        descriptions = {"easy": "慢反应、有停顿，适合第一次练习",
                        "normal": "会追球和回防，试试变向与斜射",
                        "hard": "反应更快，会预判球路和寻找射门空当"}
        text(screen, fonts, descriptions[difficulty], 18, (80, 108, 125), (640, 356))
    else:
        text(screen, fonts, "同一键盘，两位玩家来一场友谊赛", 20, (80, 108, 125), (640, 323))
        text(screen, fonts, "蓝队由玩家 2 控制，不使用电脑对手", 18, (80, 108, 125), (640, 356))
    pygame.draw.line(screen, (220, 227, 208), (345, 382), (935, 382), 2)
    text(screen, fonts, "规则介绍", 22, NAVY, (640, 409))
    text(screen, fonts, "红队 / 你   WASD 移动、瞄准    空格 踢球", 20, (178, 55, 69), (640, 442))
    blue_help = "蓝队 / 电脑   自动跑位与射门" if mode == "single" else "蓝队 / 玩家 2   方向键移动    Enter 踢球"
    text(screen, fonts, blue_help, 20, (35, 107, 170), (640, 473))
    text(screen, fonts, "双键斜跑；靠近球时淡色尖角提示射门方向。", 18, NAVY, (640, 508))
    text(screen, fonts, "接触球可带球；整球穿过门口得分。", 18, NAVY, (640, 535))
    button(screen, fonts, START_BUTTON, "开始比赛", mouse, pressed == "start")
    text(screen, fonts, "Tab 切换模式 · 1 / 2 / 3 选难度 · 空格开始", 16,
         (80, 108, 125), (640, 649))
    text(screen, fonts, "比赛中 Esc 返回首页，R 在结束后再来一局", 16,
         (80, 108, 125), (640, 675))


def draw_result(screen, fonts, result, red_score, blue_score, mouse, pressed):
    shade(screen, 155)
    panel(screen, pygame.Rect(370, 149, 540, 427), CREAM, radius=30)
    text(screen, fonts, "FULL TIME", 18, (92, 123, 142), (640, 186))
    text(screen, fonts, result, 42, NAVY, (640, 252))
    text(screen, fonts, str(red_score) + "  :  " + str(blue_score), 68, NAVY, (640, 335))
    button(screen, fonts, AGAIN_BUTTON, "再来一局   R", mouse, pressed)
    button(screen, fonts, HOME_BUTTON, "返回首页", mouse, pressed, False)


def draw_goal(screen, fonts, team, elapsed):
    color = RED if team == "red" else BLUE
    label = "红队进球！" if team == "red" else "蓝队进球！"
    image = fonts[56].render(label, True, WHITE)
    scale = 1 + 0.12 * max(0, 1 - elapsed / 0.3)
    image = pygame.transform.smoothscale(image, (round(image.get_width() * scale),
                                               round(image.get_height() * scale)))
    panel(screen, pygame.Rect(425, 201, 430, 105), color)
    screen.blit(image, image.get_rect(center=(640, 250)))
    for index in range(14):
        angle = index * math.tau / 14
        distance = 55 + elapsed * 145
        x = 640 + math.cos(angle) * distance * 1.7
        y = 254 + math.sin(angle) * distance * 0.65 + 45 * elapsed * elapsed
        pygame.draw.circle(screen, YELLOW if index % 2 else WHITE, (round(x), round(y)), 5)


def draw_hit(screen, position, time_left):
    if time_left <= 0:
        return
    x, y = project(*position)
    y -= 14
    radius = 27 + (0.14 - time_left) * 110
    for index in range(8):
        angle = index * math.tau / 8
        start = (x + math.cos(angle) * radius, y + math.sin(angle) * radius)
        end = (x + math.cos(angle) * (radius + 12), y + math.sin(angle) * (radius + 12))
        pygame.draw.line(screen, YELLOW, start, end, 4)


def draw_debug(screen, players, ball):
    for obj in [*players, ball]:
        points = [(obj.x + obj.radius * math.cos(i * math.tau / 40),
                   obj.y + obj.radius * math.sin(i * math.tau / 40)) for i in range(40)]
        ground_line(screen, YELLOW, points, 1, True)
    for player in players:
        ax, ay = player.kick_direction if player.kick_time > 0 else player.aim
        angle = math.atan2(ay, ax)
        arc = [(player.x, player.y)] + [
            (player.x + KICK_REACH * math.cos(angle - 0.87 + i * 1.74 / 20),
             player.y + KICK_REACH * math.sin(angle - 0.87 + i * 1.74 / 20))
            for i in range(21)]
        ground_line(screen, RED, arc, 1, True)
    for x in (FIELD_LEFT, FIELD_RIGHT):
        ground_line(screen, YELLOW, [(x, GOAL_MIN), (x, GOAL_MAX)], 3)
