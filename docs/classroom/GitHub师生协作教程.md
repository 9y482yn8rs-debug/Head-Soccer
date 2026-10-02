# 学生拥有仓库，教师协作开发：一步一步操作

推荐方式：学生账号创建个人仓库，邀请教师为 Collaborator。双方各自在自己的电脑克隆同一仓库；学生是项目主人，教师负责辅助完善。第一节课不必先学习 Fork。

这里仅提供操作教程；当前没有替你们创建仓库、发送邀请或上传代码。

## 1. 学生创建仓库（学生操作）

1. 登录自己的 GitHub 账号，右上角 + → New repository。
2. Owner 选择学生自己的账号；Repository name 可填 `head-soccer`。
3. Description 可填“我的 Python 足球游戏学习项目”。初期可选 Private，作品准备好后再决定是否公开。
4. 勾选 Add a README file，创建一份可直接克隆的初始仓库。暂时不用选择 .gitignore 模板或许可证。
5. 点击 Create repository，记下网址：`https://github.com/学生用户名/head-soccer`。

本教程采用“先克隆新仓库，再复制文件”，所以勾选 README 是合适的。不要同时改用“把另一个已有 Git 仓库直接推送进来”的流程。[GitHub 创建仓库说明](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)

## 2. 邀请教师（学生邀请，教师接受）

学生进入这个仓库 → Settings → Access 下的 Collaborators → Add people，搜索教师的准确 GitHub 用户名并邀请。教师登录自己的账号，从通知或邮件进入邀请页面，点击接受。学生检查对方已加入，而不是仍在等待接受。[GitHub 邀请协作者说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository)

不需要分享账号密码。学生仍是仓库所有者；教师使用自己的账号参与提交。

## 3. 首次上传：建议由教师完成

双方安装并登录 GitHub Desktop，各用自己的账号。教师按以下步骤操作：

1. File → Clone repository → URL，填学生仓库 URL，选一个新的本地文件夹，再点 Clone。
2. Repository → Show in Explorer / Show in Finder，打开刚克隆的文件夹。确认它属于学生的仓库。
3. 解压 `head-soccer-student-v1.zip`。把解压后 **head-soccer-student 文件夹里的内容** 复制到刚克隆的仓库根目录，覆盖刚才自动生成的 README 即可。
4. 目录应直接包含 main.py、requirements.txt、assets、docs、tests、tools。不要变成 `head-soccer/head-soccer-student/main.py`。
5. 不复制教师工作目录的 .git、.venv、缓存、历史图稿或教师答案。学生包已经筛选过这些内容。
6. Desktop 的 Changes 中检查文件，提交说明填“课堂基线 v1：单人 AI 与本地双人”，点击 Commit to main，再点 Push origin。
7. 打开学生仓库网页刷新，确认能直接看到 main.py 和 README。首次上传的人是教师，并不改变学生拥有仓库这件事。

克隆会建立远端关联；不需要再点 Create a new repository 或 Publish repository。[GitHub Desktop 克隆说明](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop)

## 4. 学生下载并运行

学生在自己的 Desktop 里用同一个 URL 克隆仓库。如果已在上传前克隆过，点 Fetch origin，有更新再点 Pull origin 即可。打开本地目录，按 docs/学生使用指南.md 创建自己的虚拟环境并运行 main.py。

ZIP 是第一份交付材料；仓库建立后，以克隆目录作为日常工作目录。不要每次 Download ZIP 再覆盖旧目录，那样不方便保留自己的提交历史。

## 5. 每次上课的固定节奏

| 时机 | 学生 | 教师 |
|---|---|---|
| 开始修改前 | Fetch origin；有更新则 Pull origin | 同样先同步，并确认学生上次工作已推送 |
| 修改时 | 本节课只改一个任务，保存并运行 | 尽量避免同时改学生正在改的文件 |
| 完成后 | 看 Changes，写说明，Commit，然后 Push origin | 检查学生更新，再继续自己的改动 |
| 查看对方成果 | Fetch / Pull 后重新运行 | 相同步骤 |

Commit 只保存本机版本；Push 才把提交上传给对方。不要把“已保存文件”当成“已经交作业”。[GitHub Desktop 提交与检查说明](https://docs.github.com/en/desktop/making-changes-in-a-branch/committing-and-reviewing-changes-to-your-project-in-github-desktop)

小练习可以轮流在 main 上提交。教师准备较大改动时，建议在 Desktop 的 Current branch → New branch 创建 `feature/ai-improvement`，修改并提交后 Publish branch / Push，再 Create Pull Request；学生一起看懂变化并试玩后合并。main 保留能上课的版本。等学生熟悉基本提交后再教这一段。

## 6. 常见卡点

- 看不到私有仓库 / 404：核对 URL、当前登录账号、邀请是否接受。
- 被提示 Fork 或无法 Push：先检查教师是否已成为协作者，以及 Desktop 是否登录了受邀账号。
- Push 提示远端有更新：先保存并提交本地工作，再 Fetch/Pull。遇到冲突让教师协助比较两边，保留想要的内容，再测试、提交、Push。不要强推覆盖学生成果。
- 本地有两份项目：在 Desktop 通过 Show in Explorer/Finder 打开的那份才是本次仓库工作副本；确认编辑器打开的路径一致。
- 看到 .venv 或大量缓存准备上传：检查 .gitignore 是否复制成功，不要勾选上传这些文件。
- 想恢复实验：先判断修改是否已提交。保留学习记录，和教师一起通过历史比较恢复；不要直接删除整个仓库。

## 7. 第一节课完成标准

学生能从自己的仓库克隆并运行，教师能接受邀请和提交，学生能拉取教师更新，学生的一次练习提交也能由教师看到。账号或网络尚未准备好时，先用学生 ZIP 上课，之后再按本文导入，不必因此推迟代码学习。


提交前参照 [GitHub 提交清单](GitHub提交清单.md)，素材来源见 [素材与版本说明](素材与版本说明.md)。
