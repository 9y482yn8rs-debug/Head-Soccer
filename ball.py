"""贴地滚动的足球：二维速度、摩擦减速，无跳跃与重力。"""
import math
from settings import (FIELD_LEFT, FIELD_RIGHT, FIELD_TOP, FIELD_BOTTOM,
                      BALL_RADIUS, BALL_MAX_SPEED, BALL_FRICTION)


class Ball:
    def __init__(self):
        self.radius = BALL_RADIUS
        self.reset()

    def reset(self):
        self.x = (FIELD_LEFT + FIELD_RIGHT) / 2
        self.y = (FIELD_TOP + FIELD_BOTTOM) / 2
        self.vx = self.vy = 0.0
        self.angle = 0.0

    def update(self, dt):
        self.limit_speed()
        # 指数衰减及其积分，避免不同帧率下滚动距离明显不同。
        decay = math.exp(-BALL_FRICTION * dt)
        travel = (1 - decay) / BALL_FRICTION
        self.x += self.vx * travel
        self.y += self.vy * travel
        speed = math.hypot(self.vx, self.vy)
        sign = -1 if self.vx < 0 or (self.vx == 0 and self.vy < 0) else 1
        self.angle = (self.angle - sign * speed * travel / self.radius * 180 / math.pi) % 360
        self.vx *= decay
        self.vy *= decay
        if math.hypot(self.vx, self.vy) < 6:
            self.vx = self.vy = 0.0

    def limit_speed(self):
        speed = math.hypot(self.vx, self.vy)
        if speed > BALL_MAX_SPEED:
            self.vx *= BALL_MAX_SPEED / speed
            self.vy *= BALL_MAX_SPEED / speed
