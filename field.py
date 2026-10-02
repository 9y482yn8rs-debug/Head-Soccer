"""地面投影：世界范围不变，B 方案用更开阔的近端和一致的立体高度。"""
from settings import FIELD_LEFT, FIELD_RIGHT, FIELD_TOP, FIELD_BOTTOM

SCREEN_FIELD_TOP = 364
SCREEN_FIELD_BOTTOM = 698


def depth_scale(y):
    depth = max(0.0, min(1.0, (y - FIELD_TOP) / (FIELD_BOTTOM - FIELD_TOP)))
    return 0.86 + 0.22 * depth


def project(x, y):
    center = (FIELD_LEFT + FIELD_RIGHT) / 2
    depth = (y - FIELD_TOP) / (FIELD_BOTTOM - FIELD_TOP)
    return (round(center + (x - center) * depth_scale(y)),
            round(SCREEN_FIELD_TOP + depth * (SCREEN_FIELD_BOTTOM - SCREEN_FIELD_TOP)))


def project_height(x, y, height):
    """球门高度同样随纵深缩放；height 只服务美术，不参与地面物理。"""
    px, py = project(x, y)
    return px, round(py - height * depth_scale(y))
