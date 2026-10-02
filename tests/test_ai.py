"""AI 行为与模式回归：固定场景不等同于真人胜率。"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import unittest
from collections import defaultdict
from unittest.mock import patch
import pygame
from ai import AIController, should_defend
from ball import Ball
from player import Player
from main import run
from tools.check_ai import scenario
import ui

class AITests(unittest.TestCase):
    def test_defense_requires_both_conditions(self):
        ball = Ball()
        for x, vx, expected in ((700,120,True),(700,-120,False),(600,120,False),(640,120,False)):
            ball.x, ball.vx = x, vx
            self.assertEqual(should_defend("blue", ball), expected)

    def test_ai_only_returns_intentions_and_respects_cooldown(self):
        blue, red, ball = Player("blue",690,-1), Player("red",350,1), Ball()
        red.y = 70
        before = (ball.x, ball.y, ball.vx, ball.vy, blue.x, blue.y)
        ai = AIController("hard")
        _, kick = ai.update(blue, ball, red, 1/60)
        self.assertEqual(kick, (-1,0))
        self.assertEqual(before, (ball.x, ball.y, ball.vx, ball.vy, blue.x, blue.y))
        self.assertIsNone(ai.update(blue,ball,red,1/60)[1])
        ai.reset()
        blue.cooldown = 1
        self.assertIsNone(ai.update(blue,ball,red,1/60)[1])

    def test_reaction_holds_target_then_updates(self):
        ai = AIController("normal")
        blue, red, ball = Player("blue",930,-1), Player("red",350,1), Ball()
        ai.update(blue,ball,red,0.01)
        target = ai.target
        ball.y = 80
        ai.update(blue,ball,red,0.01)
        self.assertEqual(ai.target,target)
        ai.update(blue,ball,red,0.30)
        self.assertNotEqual(ai.target,target)
        ai.reset()
        self.assertIsNone(ai.target)
        self.assertEqual((ai.elapsed,ai.shots,ai.kick_left),(0,0,0))

    def test_reachable_and_blocked_ball_scenarios(self):
        for level in ("easy","normal","hard"):
            for name in ("center","upper","lower","wrong_side","blocked"):
                with self.subTest(level=level,scenario=name):
                    self.assertEqual(scenario(level,name)["scorer"],"blue")

    def test_defensive_interception(self):
        for level in ("normal","hard"):
            self.assertEqual(scenario(level,"incoming")["scorer"],"blue")

    def test_keyboard_and_mouse_mode_selection(self):
        for key, level in ((pygame.K_1,"easy"),(pygame.K_2,"normal"),(pygame.K_3,"hard")):
            events = iter([[pygame.event.Event(pygame.KEYDOWN,key=key)],
                           [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE)]])
            with patch("pygame.event.get",side_effect=lambda:next(events)):
                result=run(max_frames=2)
            self.assertEqual((result["state"],result["difficulty"]),("playing",level))
        pos=ui.MODE_BUTTONS["local"].center
        events=iter([[pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos),
                      pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=pos)],
                     [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE)]])
        with patch("pygame.event.get",side_effect=lambda:next(events)), patch("main.AIController.update") as update:
            result=run(max_frames=2)
        self.assertEqual(result["mode"],"local")
        update.assert_not_called()

    def test_blue_keyboard_disabled_in_single_only(self):
        for mode, expected in (("single",0),("local",1)):
            with patch("pygame.event.get",return_value=[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN)]), \
                 patch("pygame.key.get_pressed",return_value=defaultdict(bool)), \
                 patch("main.AIController.update",return_value=((0,0),None)), \
                 patch("player.Player.kick") as kick:
                run(max_frames=1,start_playing=True,mode=mode)
            self.assertEqual(kick.call_count,expected)

    def test_home_does_not_update_ai(self):
        with patch("main.AIController.update") as update:
            run(max_frames=2)
        update.assert_not_called()

if __name__ == "__main__":
    unittest.main()
