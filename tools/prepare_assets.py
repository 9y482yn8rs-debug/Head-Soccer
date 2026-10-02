"""教师制作工具：把生成的动作条按格导出；游戏启动不需要运行本文件。"""
from pathlib import Path
import pygame

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "source"
OUTPUT = ROOT / "assets" / "images"


def prepare():
    actions = ("idle", "run_1", "run_2", "jump", "kick")
    for team in ("red", "blue"):
        sheet = pygame.image.load(str(SOURCE / (team + "_sheet.png")))
        for index, action in enumerate(actions):
            left = round(index * sheet.get_width() / 5)
            right = round((index + 1) * sheet.get_width() / 5)
            cell = sheet.subsurface((left, 0, right - left, sheet.get_height()))
            # 所有格子使用相同缩放和脚底基准，不逐帧自动裁剪。
            scaled = pygame.transform.smoothscale(cell, (145, 241))
            canvas = pygame.Surface((256, 256), pygame.SRCALPHA)
            canvas.blit(scaled, (56, 7))
            pygame.image.save(canvas, str(OUTPUT / (team + "_" + action + ".png")))
            if action == "idle":
                portrait = canvas.subsurface((62, 12, 132, 132))
                portrait = pygame.transform.smoothscale(portrait, (128, 128))
                pygame.image.save(portrait, str(OUTPUT / (team + "_portrait.png")))
    ball = pygame.image.load(str(OUTPUT / "ball.png"))
    ball = ball.subsurface(ball.get_bounding_rect(min_alpha=128))
    pygame.image.save(pygame.transform.smoothscale(ball, (96, 96)),
                      str(OUTPUT / "ball_ready.png"))
    goal = pygame.image.load(str(SOURCE / "goal_generated.png"))
    goal = goal.subsurface(goal.get_bounding_rect(min_alpha=128))
    pygame.image.save(pygame.transform.smoothscale(goal, (96, 216)),
                      str(OUTPUT / "goal_left.png"))
    print("素材导出完成。")


if __name__ == "__main__":
    prepare()
