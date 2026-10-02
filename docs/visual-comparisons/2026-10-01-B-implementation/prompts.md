# B 方案运行背景：实际生成提示词

生成方式：内置 image_gen；以 `../2026-10-01-v01/B-art-polish.png` 为编辑目标。输出复制为 `assets/images/stadium_b_clean.png`，没有替换或修改 v01 原始方案图。

原始输出：`C:/Users/Administrator/.codex/generated_images/01a0f683-6142-7391-b237-b992470d165f/exec-3382de6f-746c-4287-9826-a9cf499ad4b7.png`。

```text
Use case: precise-object-edit.
Asset type: production background plate for a 1280x720 2D soccer game.
Input image 1 is the EDIT TARGET: the selected B art-polish mockup. Derive a CLEAN GAME BACKGROUND from it, retaining its beautiful bright cheerful cartoon stadium style.
Preserve the lovely blue sky, white clouds, distant blue city skyline, lush trees, curved dark-blue roof structures, floodlights, multicolored crowd, lower blue-white perimeter barriers and polished cel-shaded art. Keep the same overall art quality and composition.
REMOVE COMPLETELY: all HUD panels, red/blue score cards and avatars, every letter and number, timer, titles and labels; both player characters and all character shadows; the soccer ball and its shadow; all red/blue arrows and ground rings; BOTH goals, netting and goal shadows; ALL white pitch markings including boundary lines, penalty boxes, center circle, center line, corner arcs and penalty spots. Seamlessly reconstruct the sky behind all removed HUD/text and reconstruct grass behind all removed game objects. There must be NO text, humans/players on the field, balls, goals, icons, scoreboards or white field lines baked into this background.
Grass: retain B's refined illustrated grass texture, natural subtle lighting and attractive saturated yellow-green color. Make the grass texture gently UNIFORM, without large alternating mowing bands (the engine will draw those accurately). Avoid an obvious circular patch where the ball was removed. The entire foreground below the stadium must be open uninterrupted grass.
Critical production framing: 16:9. In a 1280x720 canvas, the main stadium wall/grassy verge finishes near y=330 (46% down). Below y=340 all the way to y=720 there is clear grass, across full image width. Keep a narrow illustrated grass edging/contact shadow at the foot of the stadium. No foreground fences, stands or obstacles. No heavy spotlight gradient, no lens blur, no photographic turf; polished cartoon game illustration.
This is a clean reusable scenery asset, not a game screenshot. Single full-bleed image, no frame.
```

本图仅含看台、天空和草地。运行时场线、条纹、球门由 scenery.py 绘制；球员、足球、HUD 和方向提示继续由游戏动态绘制。没有将带有角色和 UI 的概念图直接贴进游戏。

