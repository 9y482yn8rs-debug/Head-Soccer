"""教师预览工具：无窗口导出当前界面与纵深示意。"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# 仅此工具使用虚拟显示，正常 main.py 仍打开游戏窗口。
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from main import run
from player import Player
from ball import Ball
from resources import load_resources
from settings import WIDTH, HEIGHT, FIELD_BOTTOM, PLAYER_RADIUS, FIELD_RIGHT, GOAL_MAX
import ui


def preview():
    output = ROOT / 'docs' / 'previews'
    output.mkdir(parents=True, exist_ok=True)
    run(max_frames=2, screenshot=output / 'start.png')
    run(max_frames=2, start_playing=True, screenshot=output / 'game.png')
    run(max_frames=1, mode='local', screenshot=output / 'start-local.png')
    run(max_frames=1, difficulty='hard', screenshot=output / 'start-hard.png')
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pictures, fonts = load_resources()
    players = [Player('red', 580, 1), Player('blue', 605, -1)]
    players[0].y = 185
    players[1].y = 325
    players[0].aim_at((1, 1))
    players[1].aim_at((-1, -1))
    ball = Ball()
    ball.x, ball.y = 680, 295
    ui.draw_field(screen, pictures)
    ui.draw_scene(screen, pictures, players, ball)
    ui.draw_debug(screen, players, ball)
    ui.draw_hud(screen, pictures, fonts, 0, 0, 90)
    pygame.image.save(screen, str(output / 'depth.png'))
    # 非调试画面检查：近球方向提示、球门分层和边缘可见性。
    samples = [
        ('aim.png', [(560, 330), (750, 390)], (620, 330), [(1, 0), (-1, -1)]),
        ('goal.png', [(FIELD_RIGHT - 35, GOAL_MAX - 80), (FIELD_RIGHT - 90, GOAL_MAX + 75)],
         (FIELD_RIGHT - 10, GOAL_MAX - 30), [(1, 0), (0, -1)]),
        ('edge.png', [(580, FIELD_BOTTOM - PLAYER_RADIUS), (735, FIELD_BOTTOM - PLAYER_RADIUS)],
         (640, FIELD_BOTTOM - 18), [(0, 1), (-1, 1)]),
    ]
    for filename, positions, ball_position, directions in samples:
        for player, position, direction in zip(players, positions, directions):
            player.x, player.y = position
            player.aim_at(direction)
        ball.x, ball.y = ball_position
        ui.draw_field(screen, pictures)
        ui.draw_scene(screen, pictures, players, ball)
        ui.draw_hud(screen, pictures, fonts, 0, 0, 90)
        pygame.image.save(screen, str(output / filename))
    pygame.quit()
    print('预览已保存：', output)


if __name__ == '__main__':
    preview()
