"""入口：读取输入 → 更新运动 → 判断规则 → 绘制画面。

正常启动：python main.py
学生可先读 run() 中的主循环，再进入各个功能文件。
"""
import pygame
from settings import WIDTH, HEIGHT, FPS, MATCH_SECONDS, PHYSICS_STEPS, PLAYER_SPEED
from resources import load_resources
from player import Player
from ball import Ball
from ai import AIController
from ai_settings import AI_LEVELS
from collision import try_kick, collide_player, collide_players, collide_walls
from match import goal_scorer, remaining_time, winner
import ui


def reset_field(players, ball):
    for player in players:
        player.reset()
    ball.reset()


def update_physics(players, ball, directions, dt):
    """把一帧分成小步，减少快速足球穿过角色的机会。"""
    hit_position = None
    scorer = None
    step = dt / PHYSICS_STEPS
    for _ in range(PHYSICS_STEPS):
        for index, player in enumerate(players):
            player.update(directions[index], step)
        collide_players(players[0], players[1])
        ball.update(step)
        # 踢球先于轻推，避免脚边足球在判定前被推离。
        for player in players:
            if try_kick(player, ball):
                hit_position = (ball.x, ball.y)
            collide_player(player, ball)
        collide_walls(ball)
        scorer = goal_scorer(ball)
        if scorer is not None:
            break
    return scorer, hit_position


def read_directions(keys):
    return [
        (int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
         int(keys[pygame.K_s]) - int(keys[pygame.K_w])),
        (int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]),
         int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])),
    ]


def run(max_frames=None, screenshot=None, start_playing=False, mode="single", difficulty="easy"):
    """正常运行无须传参；可选参数供教师预览与自动检查。"""
    if mode not in ("single", "local") or difficulty not in AI_LEVELS:
        raise ValueError("Invalid game mode or difficulty")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("大头足球对战 · Python + Pygame")
    pictures, fonts = load_resources()
    pygame.display.set_icon(pictures["ball"])
    clock = pygame.time.Clock()
    players = [Player("red", 350, 1), Player("blue", 930, -1)]
    ball = Ball()
    controller = AIController(difficulty) if mode == "single" else None
    players[1].speed = PLAYER_SPEED * AI_LEVELS[difficulty]["speed_ratio"] if controller else PLAYER_SPEED
    red_score = 0
    blue_score = 0
    state = "start"
    if start_playing:
        state = "playing"
    start_time = pygame.time.get_ticks()
    goal_time = 0
    scoring_team = None
    hit_position = (0, 0)
    hit_time = 0.0
    pressed_button = None
    debug = False
    running = True
    frames = 0

    while running:
        dt = min(clock.tick(FPS) / 1000, 1 / 30)
        now = pygame.time.get_ticks()
        command = None
        kick_requests = set()

        # 1. 读取事件。踢球只在按下瞬间触发，方向在本帧读取后锁定。
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    command = "home"
                elif event.key == pygame.K_F1:
                    debug = not debug
                elif state == "start" and event.key == pygame.K_TAB:
                    command = "mode_local" if mode == "single" else "mode_single"
                elif state == "start" and mode == "single" and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    command = "difficulty_" + {pygame.K_1: "easy", pygame.K_2: "normal", pygame.K_3: "hard"}[event.key]
                elif state == "start" and event.key == pygame.K_SPACE:
                    command = "new_match"
                elif state == "finished" and event.key == pygame.K_r:
                    command = "new_match"
                elif state == "playing" and not getattr(event, "repeat", False):
                    if event.key == pygame.K_SPACE:
                        kick_requests.add(0)
                    elif event.key == pygame.K_RETURN and mode == "local":
                        kick_requests.add(1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "start":
                    pressed_button = ui.start_action_at(event.pos, mode)
                elif state == "finished":
                    if ui.AGAIN_BUTTON.collidepoint(event.pos):
                        pressed_button = "again"
                    elif ui.HOME_BUTTON.collidepoint(event.pos):
                        pressed_button = "home"
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if state == "start" and pressed_button:
                    if ui.start_action_at(event.pos, mode) == pressed_button:
                        command = "new_match" if pressed_button == "start" else pressed_button
                elif state == "finished":
                    if pressed_button == "again" and ui.AGAIN_BUTTON.collidepoint(event.pos):
                        command = "new_match"
                    elif pressed_button == "home" and ui.HOME_BUTTON.collidepoint(event.pos):
                        command = "home"
                pressed_button = None
            elif event.type == pygame.WINDOWFOCUSLOST:
                pressed_button = None

        if command and command.startswith("mode_"):
            mode = command.removeprefix("mode_")
        elif command and command.startswith("difficulty_"):
            difficulty = command.removeprefix("difficulty_")

        if command == "new_match":
            controller = AIController(difficulty) if mode == "single" else None
            players[1].speed = PLAYER_SPEED * AI_LEVELS[difficulty]["speed_ratio"] if controller else PLAYER_SPEED
            reset_field(players, ball)
            red_score = 0
            blue_score = 0
            start_time = now
            state = "playing"
            hit_time = 0
            pressed_button = None
        elif command == "home":
            reset_field(players, ball)
            if controller:
                controller.reset()
            state = "start"
            red_score = 0
            blue_score = 0
            hit_time = 0
            pressed_button = None

        # 2. 比赛使用真实时间。先到时结束，再接受新的进球。
        remaining = MATCH_SECONDS
        if state != "start":
            remaining = remaining_time(start_time, now)
        if state in ("playing", "goal") and remaining <= 0:
            state = "finished"
        hit_time = max(0.0, hit_time - dt)

        # 3. 更新运动和规则，首页与结束状态不更新物理。
        if state == "playing":
            directions = read_directions(pygame.key.get_pressed())
            if controller:
                directions[1], ai_kick = controller.update(players[1], ball, players[0], dt)
                if ai_kick is not None:
                    players[1].kick(ai_kick)
            for index in kick_requests:
                players[index].kick(directions[index])
            scorer, hit = update_physics(players, ball, directions, dt)
            if hit is not None:
                hit_position = hit
                hit_time = 0.14
            if scorer is not None:
                if scorer == "red":
                    red_score += 1
                else:
                    blue_score += 1
                scoring_team = scorer
                state = "goal"
                goal_time = now
        elif state == "goal" and now - goal_time >= 1000:
            reset_field(players, ball)
            if controller:
                controller.reset()
            state = "playing"
            hit_time = 0

        # 4. 绘制：场景 → 对象 → 比赛UI → 当前状态面板。
        ui.draw_field(screen, pictures, goals_in_front=(state == "start"))
        if state != "start":
            ui.draw_scene(screen, pictures, players, ball)
        ui.draw_hit(screen, hit_position, hit_time)
        if debug:
            ui.draw_debug(screen, players, ball)
        ui.draw_hud(screen, pictures, fonts, red_score, blue_score, remaining, mode, difficulty)
        mouse = pygame.mouse.get_pos()
        if state == "start":
            ui.draw_start(screen, pictures, fonts, mouse, pressed_button, mode, difficulty)
        elif state == "goal":
            ui.draw_goal(screen, fonts, scoring_team, (now - goal_time) / 1000)
        elif state == "finished":
            result = winner(red_score, blue_score)
            if mode == "single" and red_score != blue_score:
                result = "你赢了！" if red_score > blue_score else "电脑获胜！"
            ui.draw_result(screen, fonts, result, red_score, blue_score, mouse,
                           pressed_button is not None)
        pygame.display.flip()
        frames += 1
        if max_frames is not None and frames >= max_frames:
            running = False

    if screenshot is not None:
        pygame.image.save(screen, str(screenshot))
    pygame.quit()
    return {"state": state, "red_score": red_score, "blue_score": blue_score,
            "remaining": remaining, "frames": frames, "mode": mode, "difficulty": difficulty}


if __name__ == "__main__":
    run()
