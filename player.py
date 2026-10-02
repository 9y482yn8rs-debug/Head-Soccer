"""球员在地面上移动；方向同时用于跑动和下一次踢球。"""
import math
import pygame
from settings import (FIELD_LEFT, FIELD_RIGHT, FIELD_TOP, FIELD_BOTTOM,
                      PLAYER_SPEED, PLAYER_RADIUS, KICK_DURATION, KICK_COOLDOWN)
from field import project, depth_scale


class Player:
    def __init__(self, team, start_x, facing):
        self.team = team
        self.start_x = start_x
        self.start_facing = facing
        self.radius = PLAYER_RADIUS
        self.speed = PLAYER_SPEED
        self.reset()

    def reset(self):
        self.x = float(self.start_x)
        self.y = (FIELD_TOP + FIELD_BOTTOM) / 2
        self.vx = self.vy = 0.0
        self.aim = (float(self.start_facing), 0.0)
        self.kick_direction = self.aim
        self.facing = self.start_facing
        self.kick_time = self.cooldown = 0.0
        self.kick_hit = False
        self.animation_time = 0.0

    def aim_at(self, direction):
        dx, dy = direction
        length = math.hypot(dx, dy)
        if length:
            self.aim = (dx / length, dy / length)
            if dx:
                self.facing = 1 if dx > 0 else -1

    def kick(self, direction=None):
        if direction is not None:
            self.aim_at(direction)
        if self.cooldown <= 0:
            self.kick_direction = self.aim
            self.kick_time = KICK_DURATION
            self.cooldown = KICK_COOLDOWN
            self.kick_hit = False

    def clamp_to_field(self):
        self.x = max(FIELD_LEFT + self.radius, min(FIELD_RIGHT - self.radius, self.x))
        self.y = max(FIELD_TOP + self.radius, min(FIELD_BOTTOM - self.radius, self.y))

    def update(self, direction, dt):
        self.aim_at(direction)
        moving = bool(direction[0] or direction[1])
        self.vx = self.aim[0] * self.speed if moving else 0.0
        self.vy = self.aim[1] * self.speed if moving else 0.0
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.clamp_to_field()
        self.kick_time = max(0.0, self.kick_time - dt)
        self.cooldown = max(0.0, self.cooldown - dt)
        self.animation_time += dt

    def draw(self, screen, frames):
        action = 'idle'
        if self.kick_time > 0:
            action = 'kick'
        elif self.vx or self.vy:
            action = 'run_1' if int(self.animation_time / 0.12) % 2 == 0 else 'run_2'
        if self.facing == -1:
            action += '_left'
        scale = depth_scale(self.y)
        size = round(168 * scale)
        frame = pygame.transform.smoothscale(frames[action], (size, size))
        x, y = project(self.x, self.y)
        screen.blit(frame, (round(x - size / 2), round(y - size * 174 / 192)))
