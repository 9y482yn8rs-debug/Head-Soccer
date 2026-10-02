"""只在启动时读取素材；游戏过程中复用已加载的图片和字体。"""
from pathlib import Path
import os
import pygame
from settings import WIDTH, HEIGHT
from scenery import build_scenery

ROOT = Path(__file__).resolve().parent
WINDOWS_FONTS = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
FONT_FILES = [
    ROOT / "assets" / "fonts" / "NotoSansSC-Regular.ttf",
    WINDOWS_FONTS / "msyh.ttc",
    WINDOWS_FONTS / "simhei.ttf",
    WINDOWS_FONTS / "simsun.ttc",
    Path("/System/Library/Fonts/PingFang.ttc"),
    Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
    Path("/Library/Fonts/Arial Unicode.ttf"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
]


def find_chinese_font():
    # 优先直接读取文件。Windows字体注册表可能含异常值，扫描会报错。
    for path in FONT_FILES:
        if path.is_file():
            return str(path)
    try:
        font_path = pygame.font.match_font(
            "microsoftyahei,simhei,pingfangsc,songtisc,notosanscjksc,wenquanyizenhei")
    except (TypeError, ValueError, OSError):
        font_path = None
    if font_path is None:
        raise RuntimeError(
            "未找到可用中文字体。请安装微软雅黑或黑体，或将 Noto Sans SC "
            "字体保存为 assets/fonts/NotoSansSC-Regular.ttf。")
    return font_path


def load_image(name, size):
    image = pygame.image.load(str(ROOT / "assets" / "images" / name))
    image = image.convert_alpha()
    return pygame.transform.smoothscale(image, size)


def load_resources():
    pictures = {}
    background = load_image("stadium_b_clean.png", (WIDTH, HEIGHT))
    pictures["pitch"], pictures["goal_fronts"] = build_scenery(background)
    pictures["ball"] = load_image("ball_ready.png", (48, 48))
    for team in ("red", "blue"):
        frames = {}
        for action in ("idle", "run_1", "run_2", "kick"):
            frame = load_image(team + "_" + action + ".png", (192, 192))
            frames[action] = frame
            frames[action + "_left"] = pygame.transform.flip(frame, True, False)
        pictures[team] = frames
        pictures[team + "_portrait"] = load_image(team + "_portrait.png", (64, 64))

    # 使用电脑已有的中文字体，不随项目分发商业字体文件。
    font_path = find_chinese_font()
    fonts = {}
    bold_path = WINDOWS_FONTS / "msyhbd.ttc"
    for size in (16, 18, 20, 22, 26, 30, 36, 42, 56, 68):
        if size >= 26 and bold_path.exists():
            fonts[size] = pygame.font.Font(str(bold_path), size)
        else:
            fonts[size] = pygame.font.Font(font_path, size)
        if size >= 26 and not bold_path.exists():
            fonts[size].set_bold(True)
    return pictures, fonts
