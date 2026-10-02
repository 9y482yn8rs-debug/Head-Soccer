"""静态场景制作：加载时绘制并缓存场线、草地条纹及分层球门。"""
import math
import pygame
from field import project, project_height
from settings import (WIDTH, HEIGHT, FIELD_LEFT, FIELD_RIGHT, FIELD_TOP,
                      FIELD_BOTTOM, GOAL_MIN, GOAL_MAX)

AA = 2


def _point(point):
    return tuple(round(value * AA) for value in point)


def _ground(points):
    return [_point(project(x, y)) for x, y in points]


def _tube(surface, start, end, width=5):
    """细暗边、白色管身和高光，避免球门看起来像黑色平板。"""
    a, b = _point(start), _point(end)
    for color, size in (((64, 92, 101, 235), width + 2),
                        ((210, 225, 226, 255), width),
                        ((255, 255, 245, 255), max(1, width - 2))):
        pygame.draw.line(surface, color, a, b, round(size * AA))
        radius = max(1, round(size * AA / 2))
        pygame.draw.circle(surface, color, a, radius)
        pygame.draw.circle(surface, color, b, radius)


def _mix(a, b, fraction):
    return (a[0] + (b[0] - a[0]) * fraction,
            a[1] + (b[1] - a[1]) * fraction)


def _net(surface, corners, columns, rows):
    """四边形网面；透明底让草地和球仍可透过球网看见。"""
    a, b, c, d = corners
    pygame.draw.polygon(surface, (230, 245, 237, 18), [_point(p) for p in corners])
    for i in range(columns + 1):
        t = i / columns
        pygame.draw.line(surface, (241, 250, 241, 150),
                         _point(_mix(a, b, t)), _point(_mix(d, c, t)), AA)
    for i in range(rows + 1):
        t = i / rows
        pygame.draw.line(surface, (241, 250, 241, 150),
                         _point(_mix(a, d, t)), _point(_mix(b, c, t)), AA)


def goal_geometry(side):
    x = FIELD_LEFT if side == 'left' else FIELD_RIGHT
    back_x = x + (-62 if side == 'left' else 62)
    return {
        'far': project_height(x, GOAL_MIN, 0),
        'near': project_height(x, GOAL_MAX, 0),
        'top_far': project_height(x, GOAL_MIN, 90),
        'top_near': project_height(x, GOAL_MAX, 90),
        'back_far': project_height(back_x, GOAL_MIN, 0),
        'back_near': project_height(back_x, GOAL_MAX, 0),
        'back_top_far': project_height(back_x, GOAL_MIN, 58),
        'back_top_near': project_height(back_x, GOAL_MAX, 58),
    }


def _goal_layers(side):
    back = pygame.Surface((WIDTH * AA, HEIGHT * AA), pygame.SRCALPHA)
    front = pygame.Surface(back.get_size(), pygame.SRCALPHA)
    p = goal_geometry(side)
    _net(back, [p['back_far'], p['back_near'], p['back_top_near'], p['back_top_far']], 17, 7)
    _net(back, [p['top_far'], p['top_near'], p['back_top_near'], p['back_top_far']], 17, 5)
    _net(back, [p['far'], p['back_far'], p['back_top_far'], p['top_far']], 5, 9)
    for a, b in (('back_far', 'back_near'), ('back_far', 'back_top_far'),
                 ('back_near', 'back_top_near'), ('back_top_far', 'back_top_near'),
                 ('back_far', 'far'), ('back_top_far', 'top_far')):
        _tube(back, p[a], p[b], 2)
    _tube(back, p['far'], p['top_far'], 5)
    _net(front, [p['near'], p['back_near'], p['back_top_near'], p['top_near']], 5, 9)
    for a, b in (('back_near', 'near'), ('back_top_near', 'top_near')):
        _tube(front, p[a], p[b], 2)
    _tube(front, p['top_far'], p['top_near'], 6)
    _tube(front, p['near'], p['top_near'], 6)
    return (pygame.transform.smoothscale(back, (WIDTH, HEIGHT)),
            pygame.transform.smoothscale(front, (WIDTH, HEIGHT)))


def build_scenery(background):
    """昂贵的纹理/网格绘制只执行一次；比赛每帧只贴缓存层。"""
    pitch = background.copy()
    bands = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for index in range(10):
        x1 = FIELD_LEFT + (FIELD_RIGHT - FIELD_LEFT) * index / 10
        x2 = FIELD_LEFT + (FIELD_RIGHT - FIELD_LEFT) * (index + 1) / 10
        color = (32, 86, 30, 33) if index % 2 else (247, 255, 177, 12)
        pygame.draw.polygon(bands, color, [project(x1, FIELD_TOP), project(x2, FIELD_TOP),
                            project(x2, FIELD_BOTTOM), project(x1, FIELD_BOTTOM)])
    pitch.blit(bands, (0, 0))
    markings = pygame.Surface((WIDTH * AA, HEIGHT * AA), pygame.SRCALPHA)
    color = (255, 252, 225, 230)

    def line(points, closed=False, width=2.4):
        pygame.draw.lines(markings, color, closed, _ground(points), round(width * AA))

    mid_x = (FIELD_LEFT + FIELD_RIGHT) / 2
    mid_y = (FIELD_TOP + FIELD_BOTTOM) / 2
    line([(FIELD_LEFT, FIELD_TOP), (FIELD_RIGHT, FIELD_TOP),
          (FIELD_RIGHT, FIELD_BOTTOM), (FIELD_LEFT, FIELD_BOTTOM)], True)
    line([(mid_x, FIELD_TOP), (mid_x, FIELD_BOTTOM)])
    line([(mid_x + 92 * math.cos(i * math.tau / 96),
           mid_y + 92 * math.sin(i * math.tau / 96)) for i in range(96)], True)
    pygame.draw.circle(markings, color, _point(project(mid_x, mid_y)), 3 * AA)
    for x, inward in ((FIELD_LEFT, 1), (FIELD_RIGHT, -1)):
        line([(x, GOAL_MIN - 46), (x + inward * 128, GOAL_MIN - 46),
              (x + inward * 128, GOAL_MAX + 46), (x, GOAL_MAX + 46)])
        pygame.draw.circle(markings, color, _point(project(x + inward * 90, mid_y)), 2 * AA)
    for x, sx in ((FIELD_LEFT, 1), (FIELD_RIGHT, -1)):
        for y, sy in ((FIELD_TOP, 1), (FIELD_BOTTOM, -1)):
            line([(x + sx * 22 * math.cos(i * math.pi / 40),
                   y + sy * 22 * math.sin(i * math.pi / 40)) for i in range(21)], width=1.8)
    pitch.blit(pygame.transform.smoothscale(markings, (WIDTH, HEIGHT)), (0, 0))
    shadows = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for side in ('left', 'right'):
        p = goal_geometry(side)
        near, far = p['near'], p['far']
        pygame.draw.polygon(shadows, (32, 67, 26, 30),
                            [far, near, (near[0] - 32, near[1] + 20), (far[0] - 32, far[1] + 20)])
        for i in range(14):
            t = i / 13
            start = _mix(far, near, t)
            pygame.draw.line(shadows, (33, 65, 28, 22), start,
                             (start[0] - 32, start[1] + 20), 1)
    pitch.blit(shadows, (0, 0))
    fronts = {}
    for side in ('left', 'right'):
        back, front = _goal_layers(side)
        pitch.blit(back, (0, 0))
        fronts[side] = front
    return pitch.convert(), fronts
