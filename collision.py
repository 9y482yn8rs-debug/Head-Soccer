"""地面碰撞：脚下圆形占地、面前踢球范围、边界和球门立柱。"""
import math
from settings import (FIELD_LEFT, FIELD_RIGHT, FIELD_TOP, FIELD_BOTTOM,
                      GOAL_MIN, GOAL_MAX, KICK_SPEED, KICK_REACH)


def try_kick(player, ball):
    if player.kick_time <= 0 or player.kick_hit:
        return False
    dx, dy = ball.x - player.x, ball.y - player.y
    distance = math.hypot(dx, dy)
    ax, ay = player.kick_direction
    # 以踢球瞬间锁定的方向为准，前方约 100 度扇形；不会踢到背后的球。
    if distance > KICK_REACH or (distance > 0 and (dx * ax + dy * ay) / distance < 0.64):
        return False
    ball.vx, ball.vy = ax * KICK_SPEED, ay * KICK_SPEED
    player.kick_hit = True
    return True


def collide_players(first, second):
    dx, dy = second.x - first.x, second.y - first.y
    distance = math.hypot(dx, dy)
    overlap = first.radius + second.radius - distance
    if overlap <= 0:
        return
    nx, ny = (dx / distance, dy / distance) if distance else (1.0, 0.0)
    # 分别推开；边缘一方无法退让时，余下距离交给另一方。
    for _ in range(3):
        distance = (second.x - first.x) * nx + (second.y - first.y) * ny
        correction = max(0.0, first.radius + second.radius - distance) / 2
        first.x -= nx * correction
        first.y -= ny * correction
        second.x += nx * correction
        second.y += ny * correction
        first.clamp_to_field()
        second.clamp_to_field()


def collide_player(player, ball):
    dx, dy = ball.x - player.x, ball.y - player.y
    distance = math.hypot(dx, dy)
    overlap = player.radius + ball.radius - distance
    if overlap <= 0:
        return
    nx, ny = (dx / distance, dy / distance) if distance else player.aim
    ball.x += nx * (overlap + 0.1)
    ball.y += ny * (overlap + 0.1)
    approach = (ball.vx - player.vx) * nx + (ball.vy - player.vy) * ny
    if approach < 0:
        ball.vx -= 1.15 * approach * nx
        ball.vy -= 1.15 * approach * ny
    ball.limit_speed()


def collide_walls(ball):
    if ball.y - ball.radius < FIELD_TOP:
        ball.y = FIELD_TOP + ball.radius
        ball.vy = abs(ball.vy) * 0.8
    if ball.y + ball.radius > FIELD_BOTTOM:
        ball.y = FIELD_BOTTOM - ball.radius
        ball.vy = -abs(ball.vy) * 0.8
    for line, inward in ((FIELD_LEFT, 1), (FIELD_RIGHT, -1)):
        # 只有整个球处于门口范围，才放行侧边界。
        in_mouth = GOAL_MIN + ball.radius <= ball.y <= GOAL_MAX - ball.radius
        if not in_mouth and (ball.x - line) * inward < ball.radius:
            ball.x = line + inward * ball.radius
            ball.vx = inward * abs(ball.vx) * 0.8
        # 门口端点也有碰撞，防止斜射贴柱穿过。
        for post_y in (GOAL_MIN, GOAL_MAX):
            dx, dy = ball.x - line, ball.y - post_y
            distance = math.hypot(dx, dy)
            if distance < ball.radius:
                nx, ny = (dx / distance, dy / distance) if distance else (inward, 0)
                ball.x = line + nx * (ball.radius + 0.1)
                ball.y = post_y + ny * (ball.radius + 0.1)
                speed = ball.vx * nx + ball.vy * ny
                if speed < 0:
                    ball.vx -= 1.8 * speed * nx
                    ball.vy -= 1.8 * speed * ny
