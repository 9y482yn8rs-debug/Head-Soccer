"""比赛规则：地面球完整穿过门口才进球，计时与胜负保持独立。"""
from settings import FIELD_LEFT, FIELD_RIGHT, GOAL_MIN, GOAL_MAX, MATCH_SECONDS


def goal_scorer(ball):
    if not GOAL_MIN + ball.radius <= ball.y <= GOAL_MAX - ball.radius:
        return None
    if ball.x + ball.radius < FIELD_LEFT:
        return 'blue'
    if ball.x - ball.radius > FIELD_RIGHT:
        return 'red'
    return None


def winner(red_score, blue_score):
    if red_score > blue_score:
        return '红队获胜！'
    if blue_score > red_score:
        return '蓝队获胜！'
    return '精彩平局！'


def remaining_time(start_time, now):
    return max(0.0, MATCH_SECONDS - (now - start_time) / 1000)
