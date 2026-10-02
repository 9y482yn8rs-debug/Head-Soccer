# 大头足球 · 地面自由移动版

Python + Pygame 足球教学项目，支持单人对电脑（三档难度）与本地双人。沿球场上下左右跑位、带球和射门；90 秒内进球更多的一方获胜。

课堂交付从 [课堂材料目录](classroom/README.md) 开始；学生按 [学生使用指南](classroom/学生使用指南.md) 运行。教师分发 deliverables/head-soccer-student-v1.zip。

## 运行

入口是项目根目录的 `main.py`。所有命令都在项目根目录执行，不是在 docs 文件夹中执行。正常游戏不需要运行 tools 中的制作工具。

需要 Python（建议 3.10–3.13）和 requirements.txt 中的 Pygame。给另一台电脑时，请复制完整项目，至少保留根目录所有 Python 文件、requirements.txt 和 assets/images；不要只复制 main.py。

### Windows

首次安装依赖，然后运行：

```powershell
python -m pip install -r requirements.txt
python main.py
```

以后直接 `python main.py`。也可以在 IDE 中选择已安装 Pygame 的解释器，运行 main.py。

### macOS

先安装 Python。在终端进入项目文件夹，首次执行：

```bash
cd "/你的项目路径/headSoccer"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

以后进入项目目录，执行 `source .venv/bin/activate` 和 `python main.py`。不要复制 Windows 的虚拟环境到 Mac，需在 Mac 上重新创建。安装依赖后可离线游戏。

游戏查找 Windows 微软雅黑、macOS 苹方/宋体及 Linux Noto 中文字体。找不到时，可将 Noto Sans SC 字体放在 `assets/fonts/NotoSansSC-Regular.ttf`。当前版本已在 Windows 验证，macOS 尚未实机验证。

## 操作

开始界面的“规则介绍”集中展示两队按键与基本玩法；比赛中不再显示底部操作栏，腾出的空间用于扩大场地。

| 动作 | 红队 | 蓝队 |
|---|---|---|
| 移动、瞄准 | WASD | 方向键 |
| 踢球 | 空格 | Enter |

单人模式中蓝队改由 AI 控制。首页 Tab 切模式，1/2/3 选择简单、中等、困难；也可点击对应按钮。

- 同时按两个相邻方向键可以斜跑，斜跑与直跑的地面速度相同。
- 靠近球时，淡色小尖角指示踢球方向；远离球时隐藏，脚下仅保留自然阴影。按踢球时有方向输入就朝该方向踢，否则沿最后一次移动方向踢。
- 每次按下踢球键触发一次，有短暂冷却；按住不连发。球必须在面前且足够近。
- 跑动接触足球会轻推带球；主动踢球会踢得更远。球不吸附在脚上，可以抢断。
- 人物之间有地面阻挡，可以上下绕行。足球全程贴地，没有跳跃、头球或高射。
- 球门两侧居中；整个球从门口越过门线才计分。其他边界反弹，没有界外球流程。
- 首页点击按钮或按空格开始；结束按 R 重开；Esc 回首页；F1 显示地面碰撞与踢球范围。
- 进球后庆祝 1 秒，庆祝也计入 90 秒。关闭窗口退出。

部分键盘会漏掉多人同时按下的组合键，可尝试外接支持多键同时输入的键盘。

## 文档与目录

- [后续优化与功能拓展](后续优化与功能拓展.md)：体验改进、训练模式与电脑对手的后续调优路线。
- [教学设计与题目规划](教学设计与题目规划.md)：8 组代码片段、分层学习路线与 5 选择 / 5 判断 / 5 简答的题目蓝图。

- [玩法设计](玩法设计.md)：当前移动、射门、碰撞与透视方案。
- [代码结构](代码结构.md)：模块关系、主循环顺序、阅读和修改入口。
- [视觉方案档案](visual-comparisons/README.md)：原版与多个概念图对比，以及已选 B 方案的实现记录。
- [透视优化分析](透视优化分析.md)：早期分析与 B 方案落地链接。
- [验证记录](验证记录.md)：检查范围与平台限制。
- [素材记录](assets/README.md)、[原始生成提示词](assets/生成提示词.md)。
- `previews/`：当前版本截图；`archive/`：早期文档和旧版截图，仅作历史参考。
- 项目根目录保留核心 Python 模块、依赖与 Git 配置，以及 GitHub 展示用 README；素材在 `assets/`，工具在 `tools/`，测试在 `tests/`。

## 开发检查

```bash
python -m unittest discover -s tests -v
python tools/preview.py
```

第二条命令用无窗口模式生成预览到 docs/previews，不影响正常游戏设置。角色素材沿用左右侧身动画，八方向通过移动与近球方向提示表达；暂未制作完整八方向人物动作，已支持三档 AI；暂未加入音效或独立应用打包。
