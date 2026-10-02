"""教师用检查：规则、碰撞边界和主循环流程；学生无需学习测试工具。"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import math
import unittest
from collections import defaultdict
from unittest.mock import patch
import pygame
import ui
from ball import Ball
from player import Player
from match import goal_scorer, winner, remaining_time
from collision import collide_walls, try_kick, collide_player, collide_players
from main import update_physics, run, read_directions
from settings import (FIELD_LEFT, FIELD_RIGHT, FIELD_TOP, FIELD_BOTTOM,
                      GOAL_MIN, GOAL_MAX, PLAYER_SPEED, KICK_SPEED)
from field import project, depth_scale
from resources import find_chinese_font


class FontTests(unittest.TestCase):
    def test_startup_skips_broken_font_registry(self):
        # 重现用户遇到的扫描异常：有已知字体时完全不调用扫描。
        with patch("pygame.font.match_font", side_effect=TypeError("font is int")) as scan:
            result = run(max_frames=1)
            self.assertEqual(result["state"], "start")
            scan.assert_not_called()

    def test_scan_fallback_when_known_files_missing(self):
        with patch("resources.FONT_FILES", []), \
             patch("pygame.font.match_font", return_value="other_chinese.ttf"):
            self.assertEqual(find_chinese_font(), "other_chinese.ttf")

    def test_broken_scan_gives_actionable_message(self):
        with patch("resources.FONT_FILES", []), \
             patch("pygame.font.match_font", side_effect=TypeError("font is int")):
            with self.assertRaisesRegex(RuntimeError, "NotoSansSC-Regular.ttf"):
                find_chinese_font()


class RulesTests(unittest.TestCase):
    def test_winners_and_clock(self):
        self.assertEqual(winner(3, 1), "红队获胜！")
        self.assertEqual(winner(1, 3), "蓝队获胜！")
        self.assertEqual(winner(2, 2), "精彩平局！")
        self.assertEqual(remaining_time(1000, 46000), 45)
        self.assertEqual(remaining_time(1000, 99999), 0)

    def test_goal_requires_whole_ball_and_mouth(self):
        ball = Ball()
        for line, sign, team in ((FIELD_LEFT, -1, 'blue'), (FIELD_RIGHT, 1, 'red')):
            ball.x = line + sign * ball.radius
            self.assertIsNone(goal_scorer(ball))
            ball.x += sign * 0.1
            self.assertEqual(goal_scorer(ball), team)
            ball.y = GOAL_MIN + ball.radius - 0.1
            self.assertIsNone(goal_scorer(ball))
            ball.y = GOAL_MAX - ball.radius + 0.1
            self.assertIsNone(goal_scorer(ball))
            ball.reset()

    def test_four_directions_and_normalized_diagonal(self):
        for direction in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)):
            player = Player('red', 600, 1)
            start = (player.x, player.y)
            player.update(direction, 0.1)
            self.assertAlmostEqual(math.hypot(player.x - start[0], player.y - start[1]),
                                   PLAYER_SPEED * 0.1)
            self.assertAlmostEqual(math.hypot(player.vx, player.vy), PLAYER_SPEED)

    def test_boundaries_stop_players(self):
        for direction in ((1, 1), (-1, -1)):
            player = Player('red', 600, 1)
            player.update(direction, 10)
            self.assertTrue(FIELD_LEFT + player.radius <= player.x <= FIELD_RIGHT - player.radius)
            self.assertTrue(FIELD_TOP + player.radius <= player.y <= FIELD_BOTTOM - player.radius)

    def test_idle_remembers_direction_and_reset_faces_opponent(self):
        player = Player('red', 600, 1)
        player.update((0, -1), 0.1)
        player.update((0, 0), 0.1)
        player.kick()
        self.assertEqual(player.kick_direction, (0, -1))
        self.assertEqual((player.vx, player.vy), (0, 0))
        player.reset()
        self.assertEqual(player.aim, (1, 0))
        self.assertEqual(player.cooldown, 0)

    def test_eight_shot_directions_and_constant_power(self):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            player = Player('red', 600, 1)
            length = math.hypot(dx, dy)
            ball = Ball()
            ball.x, ball.y = player.x + dx / length * 50, player.y + dy / length * 50
            player.kick((dx, dy))
            self.assertTrue(try_kick(player, ball))
            self.assertAlmostEqual(ball.vx, dx / length * KICK_SPEED)
            self.assertAlmostEqual(ball.vy, dy / length * KICK_SPEED)
            self.assertFalse(try_kick(player, ball))

    def test_shot_is_locked_and_cooldown_blocks_repeat(self):
        player = Player('red', 600, 1)
        player.kick((1, 1))
        locked = player.kick_direction
        player.update((-1, 0), 0.02)
        player.kick((-1, 0))
        self.assertEqual(player.kick_direction, locked)
        player.update((0, 0), 0.31)
        player.kick((-1, 0))
        self.assertEqual(player.kick_direction, (-1, 0))

    def test_behind_far_and_wrong_depth_cannot_be_kicked(self):
        player = Player('red', 600, 1)
        for dx, dy in ((-45, 0), (200, 0), (0, 80), (40, 120)):
            ball = Ball()
            ball.x, ball.y = player.x + dx, player.y + dy
            player.kick()
            self.assertFalse(try_kick(player, ball))
            self.assertEqual((ball.vx, ball.vy), (0, 0))
            player.reset()

    def test_body_push_and_depth_separation(self):
        player = Player('red', 600, 1)
        player.update((1, 0), 0)
        ball = Ball()
        ball.x, ball.y = player.x + 35, player.y
        collide_player(player, ball)
        self.assertGreater(ball.vx, 0)
        self.assertLess(ball.vx, KICK_SPEED)
        self.assertGreaterEqual(ball.x - player.x, ball.radius + player.radius)
        ball.x, ball.y, ball.vx = player.x, player.y + 100, 0
        collide_player(player, ball)
        self.assertEqual(ball.vx, 0)
        self.assertEqual(ball.y, player.y + 100)

    def test_players_block_but_can_pass_at_different_depths(self):
        first, second = Player('red', 600, 1), Player('blue', 630, -1)
        collide_players(first, second)
        self.assertAlmostEqual(second.x - first.x, first.radius + second.radius)
        first.x = second.x = 600
        second.y = first.y + 80
        collide_players(first, second)
        self.assertEqual(first.x, second.x)
        self.assertEqual(second.y - first.y, 80)

    def test_all_walls_and_open_goals(self):
        ball = Ball()
        ball.y, ball.vy = FIELD_TOP, -200
        collide_walls(ball)
        self.assertEqual(ball.y, FIELD_TOP + ball.radius)
        self.assertGreater(ball.vy, 0)
        ball.y, ball.vy = FIELD_BOTTOM, 200
        collide_walls(ball)
        self.assertEqual(ball.y, FIELD_BOTTOM - ball.radius)
        self.assertLess(ball.vy, 0)
        for line, inward in ((FIELD_LEFT, 1), (FIELD_RIGHT, -1)):
            ball.x, ball.y, ball.vx = line, 60, -inward * 200
            collide_walls(ball)
            self.assertEqual(ball.x, line + inward * ball.radius)
            self.assertGreater(ball.vx * inward, 0)
            ball.x, ball.y, ball.vx = line, (GOAL_MIN + GOAL_MAX) / 2, -inward * 200
            collide_walls(ball)
            self.assertEqual(ball.x, line)
            self.assertLess(ball.vx * inward, 0)

    def test_diagonal_shot_at_post_does_not_score(self):
        players = [Player('red', 350, 1), Player('blue', 930, -1)]
        ball = Ball()
        ball.x, ball.y = FIELD_RIGHT - 25, GOAL_MIN + 10
        ball.vx, ball.vy = 700, -150
        for _ in range(20):
            scorer, _ = update_physics(players, ball, [(0, 0), (0, 0)], 1 / 60)
            self.assertIsNone(scorer)
        self.assertLess(ball.x, FIELD_RIGHT)

    def test_fast_ball_hits_footprint(self):
        players = [Player('red', 500, 1), Player('blue', 1000, -1)]
        ball = Ball()
        ball.x, ball.vx = 430, 800
        for _ in range(5):
            update_physics(players, ball, [(0, 0), (0, 0)], 1 / 30)
        self.assertLess(ball.vx, 0)
        self.assertLess(ball.x, 500)

    def test_diagonal_goal_and_single_score(self):
        players = [Player('red', 350, 1), Player('blue', 930, -1)]
        ball = Ball()
        ball.x, ball.y, ball.vx, ball.vy = FIELD_RIGHT - 50, 240, 520, 200
        scorer = None
        for _ in range(30):
            scorer, _ = update_physics(players, ball, [(0, 0), (0, 0)], 1 / 60)
            if scorer:
                break
        self.assertEqual(scorer, 'red')

    def test_friction_same_across_frame_rates_and_stops(self):
        results = []
        for fps in (30, 60, 120):
            ball = Ball()
            ball.vx, ball.vy = 200, 100
            for _ in range(fps):
                ball.update(1 / fps)
            results.append((ball.x, ball.y, ball.vx, ball.vy))
            self.assertAlmostEqual(ball.vx / ball.vy, 2)
        for result in results[1:]:
            for actual, expected in zip(result, results[0]):
                self.assertAlmostEqual(actual, expected, places=7)
        for _ in range(1200):
            ball.update(1 / 60)
        self.assertEqual((ball.vx, ball.vy), (0, 0))

    def test_keyboard_mapping_and_opposing_keys(self):
        keys = defaultdict(bool, {pygame.K_w: True, pygame.K_d: True,
                                pygame.K_DOWN: True, pygame.K_LEFT: True})
        self.assertEqual(read_directions(keys), [(1, -1), (-1, 1)])
        keys[pygame.K_a] = True
        self.assertEqual(read_directions(keys)[0], (0, -1))

    def test_projection_has_depth_and_consistent_center(self):
        self.assertLess(depth_scale(FIELD_TOP), depth_scale(FIELD_BOTTOM))
        self.assertLess(project(640, FIELD_TOP)[1], project(640, FIELD_BOTTOM)[1])
        self.assertEqual(project(640, FIELD_TOP)[0], project(640, FIELD_BOTTOM)[0])


class FakeClock:
    def __init__(self):
        self.now = 0
        self.frame = 0

    def tick(self, fps):
        self.frame += 1
        self.now += 16
        if self.frame == 90:
            self.now += 90000
        return 16


class FlowTests(unittest.TestCase):
    def simulate(self, frames, mouse_start=False):
        clock = FakeClock()

        def events():
            if clock.frame == 1:
                if mouse_start:
                    return [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=ui.START_BUTTON.center),
                            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=ui.START_BUTTON.center)]
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]
            if clock.frame == 91:
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)]
            if clock.frame == 92:
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
            return []

        def physics(players, ball, directions, dt):
            if clock.frame == 10:
                ball.x, ball.y = 1205, 270
                ball.vx, ball.vy = 0, 0
            return update_physics(players, ball, directions, dt)

        with patch("pygame.time.Clock", return_value=clock), \
             patch("pygame.time.get_ticks", side_effect=lambda: clock.now), \
             patch("pygame.event.get", side_effect=events), \
             patch("main.update_physics", side_effect=physics):
            return run(max_frames=frames, mode="local")

    def test_goal_counts_once_and_resets(self):
        result = self.simulate(89)
        self.assertEqual(result["state"], "playing")
        self.assertEqual(result["red_score"], 1)
        self.assertEqual(result["blue_score"], 0)

    def test_mouse_start_and_game_over(self):
        result = self.simulate(90, mouse_start=True)
        self.assertEqual(result["state"], "finished")
        self.assertEqual(result["remaining"], 0)
        self.assertEqual(result["red_score"], 1)

    def test_restart(self):
        result = self.simulate(91)
        self.assertEqual(result["state"], "playing")
        self.assertEqual(result["red_score"], 0)
        self.assertEqual(result["remaining"], 90)

    def test_same_frame_direction_and_kick_reaches_physics(self):
        ball = Ball()
        ball.x, ball.y = 390, (FIELD_TOP + FIELD_BOTTOM) / 2 - 40
        keys = defaultdict(bool, {pygame.K_w: True, pygame.K_d: True})
        with patch('main.Ball', return_value=ball), \
             patch('pygame.key.get_pressed', return_value=keys), \
             patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]):
            result = run(max_frames=1, start_playing=True)
        self.assertEqual(result['state'], 'playing')
        self.assertGreater(ball.vx, 0)
        self.assertLess(ball.vy, 0)
        self.assertAlmostEqual(abs(ball.vx), abs(ball.vy))

    def test_repeated_keydown_does_not_kick(self):
        ball = Ball()
        ball.x, ball.y = 400, 270
        with patch('main.Ball', return_value=ball), \
             patch('pygame.key.get_pressed', return_value=defaultdict(bool)), \
             patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, repeat=True)]):
            run(max_frames=1, start_playing=True)
        self.assertEqual((ball.vx, ball.vy), (0, 0))

    def test_home(self):
        result = self.simulate(92)
        self.assertEqual(result["state"], "start")
        self.assertEqual(result["red_score"], 0)


if __name__ == "__main__":
    unittest.main()
