# 图像生成提示词与来源

生成方式：内置 image_gen；全部以 A-current.png 为编辑目标。没有使用 CLI/API fallback。

版本：2026-10-01-v01。每张图保留原始输出，不做后期拼贴或像素修改。A 为原游戏截图，B/C/D 为 AI 视觉概念图，不是已实现的运行截图。

## B — 美术加强（第一张）

```text
Use case: precise-object-edit.
Asset type: full-screen 16:9 game UI visual comparison mockup, version B: conservative visual refinement.
Image 1 is the EDIT TARGET: actual screenshot of our existing children's two-player 2D soccer game. Produce ONE revised screenshot, not a comparison board.
Primary request: carefully polish spatial coherence of the pitch and the two side goals while retaining the existing attractive cartoon stadium background. This is a VISUAL PROPOSAL, not a redesign of the game's identity.
Invariants: preserve the entire top scoreboard HUD, all Chinese/English labels, timer 01:30 and scores 0:0; preserve the smiling chibi brown-haired red-shirt player on the left and blonde blue-shirt player on the right, their identities, poses, approximate sizes and positions, the small central soccer ball and colored foot arrows. Preserve the blue sky, white clouds, city silhouette, trees, curved grandstands, colorful crowd and navy outlined cel-shaded illustration. Upper 0-45% of the image should remain as close to the input as possible. No bottom control bars, no extra buttons or labels.
Change only the field presentation, ground/stadium transition, and goal art:
- Keep the expanded play area: pitch back edge about y=340/720, front edge about y=687/720, near corners about x=100/1280 and x=1180/1280. Do NOT shrink the usable field or turn it into a distant tiny pitch.
- Use very gentle near-wide/far-narrow geometry and calm, subtly textured grass with alternating mowing bands; coherent white center circle ellipse and penalty boxes following the same shallow perspective.
- Add a thin, convincing grass/verge/low perimeter-wall transition at the back edge without occupying the pitch.
- Redraw both goals as attractive readable white tubular soccer goals facing inward from the left and right touchlines, same world goal mouths and approximate footprint. Posts stand vertically, consistent height in the shallow view, horizontal crossbar and support frames with a light translucent-looking white mesh and mild contact shadows. The goal mouth is an OPEN portal facing the center of the pitch. Avoid opaque dark panels, thin collapsed goal shapes, or giant goals.
- Keep the lively polished original cartoon aesthetics, bright green pitch and cheerful daylight, modest soft grounding shadows only. No photorealism, no dramatic camera shift, no new obstacles, no new characters.
Output: one high-quality 16:9 landscape screenshot-like visual at 1280x720 or equivalent 16:9. Do not add B labels, annotations, borders, or proposal captions inside the image.
```

## C — 俯视全景（第二张）

```text
Use case: precise-object-edit.
Asset type: full-screen 16:9 game UI visual comparison mockup, version C: unified gentle elevated camera.
Image 1 is the EDIT TARGET: actual current screenshot of our existing children's two-player 2D soccer game. Produce ONE alternative screenshot, not a comparison board.
Primary request: show what a more unified gentle elevated/three-quarter stadium camera could look like, while keeping the original gorgeous bright cartoon visual identity. Retain the stadium's charm and richness. The goal is a tasteful spatially coherent alternative, not a sparse flat diagram.
Invariants: preserve the top scoreboard HUD layout, red and blue avatars, all Chinese/English labels, timer 01:30, score 0:0. Keep exactly two same chibi players: brown-haired red-shirt on left, blonde blue-shirt on right, approximately original screen positions and sizes, and one small soccer ball at center with the colored foot arrows. Preserve the colorful sunny palette, blue sky, clouds, distant city, trees, curved roofed grandstands and multicolored spectators, navy outlines and polished cel shading. No bottom instruction bars.
Camera and world changes:
- Reinterpret the lower grandstands and low pitch-side barrier from a moderately elevated, shallow downward view, so the visible tops of low walls, goal frames and field all agree. Use the original background as art-direction reference; do not merely vertically squash it.
- Pitch remains generous and playable, filling roughly x=100..1180 and y=330..687 of a 1280x720 image. Keep far width at least ~85% of near width; no extreme vanishing point or heavily shrunken far end. Maintain all four visible pitch corners and the expanded front boundary near the bottom.
- A warm bright green field, subtle grass texture, alternating mowing bands, crisp restrained white markings and elliptical center circle all share a single gentle camera perspective.
- Two readable white tubular goal frames on the left and right centered in the side boundaries, facing inward toward the ball, in coherent mild three-quarter perspective. Light netting, actual open mouths, structural depth, restrained grounding shadows. No opaque green goal slabs, no free-floating posts.
- Keep players primarily familiar chibi side/three-quarter sprites suitable for this simple 2D game. Coherent soft foot shadows and mild near/far scaling connect them to the field. Do not shrink them or make new 3D toy characters.
The change should be noticeable mainly in the stadium-to-field connection and goal geometry, with attractive layered depth and a cohesive polished game-art look. Avoid excessive realism, excessive tilt, night lighting, cinematic effects, visual clutter or lost playing area.
Output: one high-quality 16:9 landscape screenshot-like visual at 1280x720 or equivalent 16:9. No C labels, annotations, borders, or proposal captions inside the image.
```

## D — 克制小改（第三张）

```text
Use case: precise-object-edit.
Asset type: conservative, minimally edited game screenshot, full 16:9.
Image 1 is the EDIT TARGET, the actual current game screenshot. Make a STRICT minimal-local-edit proposal. The user likes this exact original stadium background and needs a fair apples-to-apples comparison, not a redesign.
PIXEL-PLACEMENT INVARIANTS: Preserve the entire sky, skyline, trees, grandstands, seats and perimeter wall in the top 340/720 of the image. Keep their shapes, framing, positions and sizes as close as possible to the reference. Preserve the complete HUD, same text and typography, exact scores and timer, and same character sprites and small ball, foot rings and direction arrows, at the same proportional image coordinates. No changes to player scale. Leave the smooth simple cartoon art style intact.
Most important: lock the WHITE PITCH OUTLINE to these normalized vertices: far left (0.137,0.472), far right (0.863,0.472), near right (0.922,0.954), near left (0.078,0.954). This is a nearly rectangular pitch with weak convergence, NOT a strongly trapezoidal stadium. Do not move front corners to image edges, shrink the far width, reduce playable area, or add foreground stands. Keep center line, center circle ellipse and penalty areas near the original exact locations.
Only improve two things:
1. Replace the two thin dark slab-looking goals with neat white tubular goal frames and very light open diamond netting, still matching their original footprints and original mouth lengths. Left mouth occupies roughly x=0.092..0.125 and y=0.53..0.81, right is mirrored. Make all posts structurally coherent and standing upright; mouths face inward. Frame and net must stay subtle, not enormous. Keep goal boundaries readable.
2. Add ONLY a slight illustrated grass grain, soften alternating green bands very slightly, and use delicate grounding shadows and a narrow tidy grass-to-wall seam. The large pitch should still look like a clean 2D cartoon playing surface, not a photographic lawn.
Explicitly avoid changes to background art, field camera, player identity/scale/position, HUD, layout, time, score, and control scheme. No new labels, no proposal titles, no bottom instructions, no cinematic light. ONE image, no collage. 16:9. This should look almost identical at first glance to image 1, with improved goals and surface finish visible on closer inspection.
```

