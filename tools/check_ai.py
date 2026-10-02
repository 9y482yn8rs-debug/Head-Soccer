"""无窗口的固定场景回归；用于验证行为，不代表真人胜率。"""
import sys
import json
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ai import AIController
from ai_settings import AI_LEVELS
from player import Player
from ball import Ball
from main import update_physics, reset_field
from settings import PLAYER_SPEED


def scenario(level, name, seconds=35):
    players = [Player('red', 350, 1), Player('blue', 930, -1)]
    players[0].y = 70
    ball = Ball()
    if name == 'upper':
        ball.x, ball.y = 660, 45
    elif name == 'lower':
        ball.x, ball.y = 660, 575
    elif name == 'wrong_side':
        players[1].x = 450
    elif name == 'blocked':
        players[0].y = 310
    elif name == 'incoming':
        ball.x, ball.y, ball.vx = 780, 340, 650
        players[1].x, players[1].y = 1080, 210
    ai = AIController(level)
    players[1].speed = PLAYER_SPEED * AI_LEVELS[level]['speed_ratio']
    states = Counter()
    kicks = 0
    for frame in range(round(seconds * 60)):
        move, kick = ai.update(players[1], ball, players[0], 1 / 60)
        if kick:
            players[1].kick(kick)
            kicks += 1
        scorer, _ = update_physics(players, ball, [(0, 0), move], 1 / 60)
        states[ai.state] += 1
        if scorer:
            return dict(level=level, scenario=name, scorer=scorer,
                        seconds=round((frame+1)/60, 2), kicks=kicks)
    return dict(level=level, scenario=name, scorer=None, seconds=seconds, kicks=kicks,
                player=[round(players[1].x),round(players[1].y)],
                ball=[round(ball.x),round(ball.y)], states=dict(states))


if __name__ == '__main__':
    results=[scenario(level, name) for level in AI_LEVELS
             for name in ('center', 'upper', 'lower', 'wrong_side', 'blocked', 'incoming')]
    print(json.dumps(results, ensure_ascii=False, indent=2))
