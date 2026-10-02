# 素材记录

原球场、红蓝球员动作条、足球和旧版球门由 OpenAI 内置 imagegen 生成。完整原始提示词见 [生成提示词](生成提示词.md)。B 方案实现时，使用内置 image_gen 从选中的 B 概念图派生干净球场背景，见 [B 背景生成提示词](../visual-comparisons/2026-10-01-B-implementation/prompts.md)。场线、条纹、白色透视球门、近球方向提示与软阴影由 Pygame 绘制。

以下路径均相对于项目根目录：

- `assets/source/red_sheet.png`、`blue_sheet.png`：五格原始动作条。
- `assets/images/stadium_b_clean.png`：当前运行背景，保留 B 的看台氛围和草地质感，已移除角色、足球、HUD、球门和场线。
- `assets/images/field.png`：旧版背景，保留但当前不加载。
- `assets/images/ball_ready.png`：已导出的透明足球。
- `assets/images/red_*.png`、`blue_*.png`：站立、两帧跑动、踢球和头像；旧 jump 图保留但不加载。
- `assets/source/goal_generated.png`、`assets/images/goal_left.png`：旧版球门，保留备查，当前不加载。
- `assets/source/reference/`：初始项目示意图，非运行资源。

`tools/prepare_assets.py` 保留原始五格动作条导出逻辑，可由教师重新导出素材，正常游戏无需运行。本版运行加载四个动作×两队、两个头像、一个背景和一个足球，共 12 张图片。

不随项目分发系统商业字体。resources.py 优先读取电脑已有中文字体：Windows 微软雅黑、macOS 苹方/宋体，以及 Noto 中文字体等。若自行附带字体，应同时保留该字体要求的许可文件。

生成图按实际来源记录为 OpenAI imagegen 生成，不据此宣称专有版权或第三方许可。历史生成提示词中的单线地面和跳跃描述是原始素材制作记录，不代表当前玩法。
