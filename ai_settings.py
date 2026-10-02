"""课堂修改入口：数值越小，reaction 越快；速度不能超过玩家。"""
AI_LEVELS = {
    "easy": {
        "label": "简单", "reaction": 0.65, "speed_ratio": 0.52,
        "kick_interval": 1.10, "prediction": 0.0,
        "defend": False, "diagonal": False, "avoid_blocker": False,
    },
    "normal": {
        "label": "中等", "reaction": 0.28, "speed_ratio": 0.82,
        "kick_interval": 0.55, "prediction": 0.10,
        "defend": True, "diagonal": True, "avoid_blocker": False,
    },
    "hard": {
        "label": "困难", "reaction": 0.12, "speed_ratio": 1.0,
        "kick_interval": 0.32, "prediction": 0.24,
        "defend": True, "diagonal": True, "avoid_blocker": True,
    },
}
