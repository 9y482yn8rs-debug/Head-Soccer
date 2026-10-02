"""白名单打包：只交付课堂运行文件和学生材料，不包含教师答案。"""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def package():
    output = ROOT / "deliverables"
    output.mkdir(exist_ok=True)
    files = ["main.py", "ai.py", "ai_settings.py", "player.py", "ball.py",
             "collision.py", "match.py", "settings.py", "field.py", "scenery.py",
             "resources.py", "ui.py", "requirements.txt", ".gitignore", ".gitattributes",
             "docs/previews/game.png",
             "tests/test_game.py", "tests/test_ai.py", "tools/check_ai.py"]
    files += ["assets/images/" + name for name in ("stadium_b_clean.png", "ball_ready.png")]
    files += [f"assets/images/{team}_{action}.png" for team in ("red", "blue")
              for action in ("idle", "run_1", "run_2", "kick", "portrait")]
    docs = ("学生使用指南.md", "学生练习.md", "学习记录.md", "GitHub师生协作教程.md",
            "GitHub提交清单.md", "素材与版本说明.md")
    entries = {name: (ROOT / name).read_bytes() for name in files}
    entries.update({"docs/" + name: (ROOT / "docs/classroom" / name).read_bytes() for name in docs})
    entries["README.md"] = (ROOT / "README.md").read_text(encoding="utf-8").replace(
        "docs/classroom/", "docs/").encode("utf-8")
    path = output / "head-soccer-student-v1.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr("head-soccer-student/" + name, data)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = "# 学生包交付清单\n\n文件：head-soccer-student-v1.zip\n\n"
    manifest += f"共 {len(entries)} 个文件；大小 {path.stat().st_size:,} 字节。\n\nSHA256：`{digest}`\n\n"
    manifest += "教师保留原工作目录，发给学生此 ZIP 即可。包内无教师答案、虚拟环境、缓存、Git 历史或旧版美术。\n\n"
    manifest += "解压后按 docs/学生使用指南.md 运行；GitHub 首次导入时复制内层目录的内容。\n\n## 文件列表\n\n"
    manifest += "\n".join("- " + name for name in sorted(entries)) + "\n"
    (output / "README.md").write_text(manifest, encoding="utf-8")
    print(f"Created {path} ({len(entries)} files)")

if __name__ == "__main__":
    package()
