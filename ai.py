"""规则型电脑对手：只输出移动和踢球意图，不修改球的位置或速度。"""
import math
from ai_settings import AI_LEVELS
from settings import (FIELD_LEFT, FIELD_RIGHT, FIELD_TOP, FIELD_BOTTOM,
                      GOAL_MIN, GOAL_MAX, KICK_REACH, PLAYER_RADIUS)


def should_defend(team, ball):
    """教学入口：球在己方半场并朝己方球门运动，才需要主动回防。"""
    middle = (FIELD_LEFT + FIELD_RIGHT) / 2
    if team == "blue":
        return ball.x > middle and ball.vx > 80
    return ball.x < middle and ball.vx < -80


def direction_to(x, y, target, tolerance=7):
    """使用和键盘一样的八方向；接近目标就停，避免原地来回抖动。"""
    dx, dy = target[0] - x, target[1] - y
    if math.hypot(dx, dy) <= tolerance:
        return (0, 0)
    angle = round(math.atan2(dy, dx) / (math.pi / 4))
    return ((1, 0), (1, 1), (0, 1), (-1, 1),
            (-1, 0), (-1, -1), (0, -1), (1, -1))[angle % 8]


def clamp_target(x, y):
    return (max(FIELD_LEFT + PLAYER_RADIUS, min(FIELD_RIGHT - PLAYER_RADIUS, x)),
            max(FIELD_TOP + PLAYER_RADIUS, min(FIELD_BOTTOM - PLAYER_RADIUS, y)))


def shot_is_blocked(ball, opponent, direction, goal_x):
    dx, dy = direction
    length = math.hypot(dx, dy)
    nx, ny = dx / length, dy / length
    rx, ry = opponent.x - ball.x, opponent.y - ball.y
    along = rx * nx + ry * ny
    distance_to_goal = abs(goal_x - ball.x) * length
    across = abs(rx * ny - ry * nx)
    return 0 < along < distance_to_goal and across < opponent.radius + ball.radius + 12


def choose_shot(team, ball, opponent, options):
    """选择能到达门口的八方向射门；困难档同时考虑对手挡住的线路。"""
    sign = -1 if team == "blue" else 1
    goal_x = FIELD_LEFT if team == "blue" else FIELD_RIGHT
    candidates = [(sign, 0)]
    if options["diagonal"]:
        candidates += [(sign, -1), (sign, 1)]
    for direction in candidates:
        dx, dy = direction
        goal_y = ball.y + (goal_x - ball.x) * dy / dx
        if not GOAL_MIN + ball.radius + 8 <= goal_y <= GOAL_MAX - ball.radius - 8:
            continue
        if options["avoid_blocker"] and shot_is_blocked(ball, opponent, direction, goal_x):
            continue
        return direction
    return None


class AIController:
    def __init__(self, difficulty="easy"):
        if difficulty not in AI_LEVELS:
            raise ValueError("Unknown AI difficulty: " + difficulty)
        self.difficulty = difficulty
        self.options = AI_LEVELS[difficulty].copy()
        self.reset()

    def reset(self):
        self.think_left = 0.0
        self.kick_left = 0.0
        self.target = None
        self.state = "wait"
        self.elapsed = 0.0
        self.lane = 1
        self.shots = 0

    def update(self, player, ball, opponent, dt):
        self.elapsed += dt
        self.think_left = max(0.0, self.think_left - dt)
        self.kick_left = max(0.0, self.kick_left - dt)
        kick = None
        # 简单档有明显思考停顿，给初学者留下绕行和射门的时间。
        if self.difficulty == "easy" and self.elapsed % 4.0 > 2.9:
            self.state = "wait"
            return (0, 0), None
        if self.think_left <= 0:
            self.think_left = self.options["reaction"]
            kick = self._think(player, ball, opponent)
        move = direction_to(player.x, player.y, self.target) if self.target else (0, 0)
        return move, kick

    def _think(self, player, ball, opponent):
        sign = -1 if player.team == "blue" else 1
        own_x = FIELD_RIGHT if player.team == "blue" else FIELD_LEFT
        distance = math.hypot(ball.x - player.x, ball.y - player.y)
        shot = choose_shot(player.team, ball, opponent, self.options)
        # 简单/中等允许犯几次同样的错误，之后换路线，避免无限顶着对手射门。
        goal_x = FIELD_LEFT if player.team == "blue" else FIELD_RIGHT
        retry_limit = 5 if self.difficulty == "easy" else 3
        if shot and self.shots >= retry_limit and shot_is_blocked(ball, opponent, shot, goal_x):
            shot = None
        # 贴住上下边线时，用同样的踢球规则借墙反弹，把球送回场内。
        edge_margin = PLAYER_RADIUS + ball.radius + 12
        if ball.y < FIELD_TOP + edge_margin:
            shot = (0, -1)
        elif ball.y > FIELD_BOTTOM - edge_margin:
            shot = (0, 1)
        # AI 也必须靠近球、站在合适一侧，并等待正常冷却。
        if shot and distance <= KICK_REACH - 5 and distance > 0:
            dx, dy = shot
            alignment = ((ball.x - player.x) * dx + (ball.y - player.y) * dy) / (distance * math.hypot(dx, dy))
            if alignment >= 0.72 and player.cooldown <= 0 and self.kick_left <= 0:
                self.kick_left = self.options["kick_interval"]
                self.shots += 1
                self.state = "shoot"
                self.target = (player.x, player.y)
                return shot

        if self.options["defend"] and should_defend(player.team, ball) and distance > KICK_REACH - 10:
            guard_x = own_x + sign * 55
            travel = max(0.0, min(0.7, (guard_x - ball.x) / ball.vx))
            guard_y = ball.y + ball.vy * travel
            guard_y = max(GOAL_MIN + 24, min(GOAL_MAX - 24, guard_y))
            self.target = clamp_target(guard_x, guard_y)
            self.state = "defend"
            return None

        # 球很近时不预测，避免追逐自己推走后的虚拟位置。
        ahead = self.options["prediction"] if distance > 150 else 0.0
        bx, by = clamp_target(ball.x + ball.vx * ahead, ball.y + ball.vy * ahead)
        if shot:
            dx, dy = shot
        else:
            # 没有直达门口的角度：先把球带进门口纵深范围或绕开阻挡。
            center_y = (GOAL_MIN + GOAL_MAX) / 2
            dy = 1 if by < center_y else -1
            if abs(by - center_y) < 45 and self.options["avoid_blocker"]:
                dy = 1 if opponent.y <= by else -1
            dx = 0
        length = math.hypot(dx, dy)
        dx, dy = dx / length, dy / length
        px, py = -dy, dx
        rx, ry = player.x - bx, player.y - by
        behind = -(rx * dx + ry * dy)
        lateral = rx * px + ry * py
        safe_back = clamp_target(bx - dx * 50, by - dy * 50)
        available = (bx - safe_back[0]) * dx + (by - safe_back[1]) * dy
        required_behind = min(28, max(5, available - 8))
        if behind < required_behind:
            # 先横向绕出球的占地，再跑到球后；不直接把球顶进己方球门。
            if abs(lateral) < 72:
                self.lane = 1 if lateral >= 0 else -1
                # 若这一侧靠边，改走另一侧。
                candidate = (bx + px * self.lane * 95, by + py * self.lane * 95)
                if not (FIELD_TOP + 45 <= candidate[1] <= FIELD_BOTTOM - 45 and
                        FIELD_LEFT + 45 <= candidate[0] <= FIELD_RIGHT - 45):
                    self.lane *= -1
                self.target = clamp_target(player.x + px * (self.lane * 95 - lateral),
                                           player.y + py * (self.lane * 95 - lateral))
            else:
                self.lane = 1 if lateral >= 0 else -1
                self.target = clamp_target(bx - dx * 65 + px * self.lane * 90,
                                           by - dy * 65 + py * self.lane * 90)
            self.state = "circle"
        else:
            offset = 49 if shot else -12
            self.target = clamp_target(bx - dx * offset, by - dy * offset)
            self.state = "approach" if shot else "dribble"
        return None
