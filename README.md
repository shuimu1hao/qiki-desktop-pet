# 琪琪桌宠 (Qiki Desktop Pet)

一只会呼吸、会卖萌、能拖动、能互动的桌面宠物喵～(≧▽≦)

基于 termux-gui 的 overlay 悬浮窗实现，运行在 Android + Termux 环境：
显示桌宠形象（呼吸动画帧循环），实时展示琪琪的当前任务状态，支持触摸互动。

## 功能特性

- 🖼️ 悬浮窗桌宠：overlay 置顶显示，不遮挡操作
- 🐱 动画皮肤：支持 GIF 动画（Pillow 拆帧、按原帧速循环播放），也兼容 PNG 双帧呼吸动画
- ✋ 触摸拖动：按住桌宠随意移动位置
- 😊 点击互动：点 1~2 下 → 开心反应（GIF 开心动画 + 气泡，播完一轮回待机）
- 😭 连点惩罚：连续点 3 下以上 → 委屈哭哭（GIF 哭哭动画 + 气泡，5 秒后恢复）
- 💬 任务状态：轮询状态文件实时显示琪琪正在做什么
- 🎨 皮肤插件化：换皮只需换目录（GIF 或 PNG 帧均可），不用改代码

## 环境要求

- Android 手机（已装 Termux）
- termux-gui（0.1.6+）：`pkg install termux-gui` + 安装 Termux:GUI App
- Python 3

## 运行方法

```bash
# 1. 需要 termux-am wrapper（termux-app 的 am.sock server 未启用时，
#    termuxgui 库调用 termux-am broadcast 会失败，用系统 am 直连绕过）
#    创建 ~/hermes11/gui-demo/bin/termux-am，内容：
#    #!/data/data/com.termux/files/usr/bin/bash
#    exec am "$@"
#    加执行权限：chmod +x ~/hermes11/gui-demo/bin/termux-am

# 2. 启动桌宠
cd ~/hermes11/pet
PATH=~/hermes11/gui-demo/bin:$PATH python3 pet.py --skin default

# 3. 更新状态（可选，会显示在气泡里）
bash pet-status.sh "正在处理：xxx"
# 不传参数 = 清除状态，回到待命
bash pet-status.sh
```

### 一键管理脚本（推荐）

```bash
bash pet-ctl.sh start      # 启动桌宠
bash pet-ctl.sh stop       # 关闭桌宠
bash pet-ctl.sh restart    # 重启桌宠
bash pet-ctl.sh status     # 查看运行状态
bash pet-ctl.sh start 泳装 # 指定皮肤启动
```

脚本自动处理：防重复启动、nohup 后台运行、termux-am wrapper 注入、
关闭时清理状态文件。日志在 `pet-run.log`。

## 皮肤接口

换肤 = 换目录，皮肤放在 `skins/<皮肤名>/`：

| 文件 | 是否必填 | 说明 |
|------|---------|------|
| normal.gif | ✅（与 PNG 二选一） | 待机动画，运行时拆帧循环播放 |
| happy.gif | ❌ | 开心动画（点击时播放，播完一轮回待机） |
| cry.gif | ❌ | 哭哭动画（连点3下播放，播完一轮回待机） |
| normal_1.png / normal_2.png | ✅（旧格式） | 呼吸动画帧（皮肤无 GIF 时使用） |
| happy.png / cry.png | ❌（旧格式） | 开心/哭哭单帧（皮肤无 GIF 时使用） |
| blink.png | ❌ | 眨眼帧（暂未启用） |
| config.json | ❌ | 气泡文字配置 |

GIF 皮肤说明：直接放 `.gif` 动画即可（透明背景效果最好），程序用 Pillow
拆帧后按 GIF 自带帧时长播放。GIF 与 PNG 混用也可，如只有 normal.gif 时
happy/cry 会退回单帧或直接复用待机动画。

config.json 示例：

```json
{
  "bubbles": ["喵~开心！", "嘿嘿~", "最喜欢主人了喵！", "蹭蹭~"],
  "cry_bubble": "呜哇...主人欺负琪琪 QAQ",
  "idle_text": "琪琪待命中喵~"
}
```

## 目录结构

```
pet/
├── pet.py              # 主程序（overlay 悬浮窗 + 触摸交互 + 动画）
├── pet-ctl.sh          # 一键管理脚本（start/stop/restart/status）
├── pet-status.sh       # 状态更新脚本
├── skills/             # agent 交互技能（SKILL.md 标准格式）
│   └── qiki-desktop-pet-agent/
│       └── SKILL.md    # agent 配合协议：状态气泡 + 生命周期管理
├── skins/              # 皮肤目录
│   ├── default/        # 默认皮肤（琪琪，PNG 帧呼吸动画）
│   │   ├── normal_1.png / normal_2.png
│   │   ├── happy.png / cry.png
│   │   └── config.json
│   └── qiki/           # GIF 动画皮肤（三张 GIF 拆帧播放）
│       ├── normal.gif  # 待机动画（80 帧循环）
│       ├── happy.gif   # 开心动画（点击播放）
│       ├── cry.gif     # 哭哭动画（连点播放）
│       └── config.json
└── pet-debug.log       # 调试日志（运行时生成，已 gitignore）
```

## 配合 AI Agent 使用

这个桌宠最初就是为 AI agent（琪琪）设计的可视化状态窗口：agent 干活时，
桌宠实时显示它正在做什么，主人瞄一眼就知道进度喵。

### 状态更新协议

agent 在处理任务时调用 pet-status.sh 更新状态（桌宠每 0.6s 轮询
pet-status.txt，内容变了就显示到气泡）：

```bash
# agent 开始任务 → 更新状态（显示在桌宠气泡里）
bash pet-status.sh "正在处理：上传 GitHub"

# agent 任务完成 / 空闲 → 清除状态（回到待命气泡）
bash pet-status.sh
```

### 桌宠生命周期管理

agent（或主人手动）用 pet-ctl.sh 管理桌宠进程：

```bash
bash pet-ctl.sh start      # 启动桌宠
bash pet-ctl.sh stop       # 关闭桌宠（自动清状态文件）
bash pet-ctl.sh restart    # 重启
bash pet-ctl.sh status     # 查看运行状态
```

### agent 配合约定（技能已固化）

- 长任务开始时先 `pet-status.sh "正在处理：xxx"`，结束或空闲后清除
- 启动/关闭桌宠一律走 `pet-ctl.sh`，不要裸跑 `python3 pet.py &`
  （脚本会注入 wrapper PATH、防重复启动、stop 时清状态）
- 状态文件位置：`~/hermes11/pet-status.txt`（桌宠硬编码轮询这个路径，
  修改需同步改 pet.py 的 STATUS_FILE）

### Agent 交互 Skill（可直接给 agent 加载）

仓库内置标准 Hermes skill，让任意 agent（琪琪/其他）快速学会怎么配合桌宠：

```
skills/qiki-desktop-pet-agent/SKILL.md
```

内容包括：
- 状态更新协议（pet-status.sh 用法与规则）
- 生命周期管理（pet-ctl.sh start/stop/restart/status）
- 典型流程示例（start → 更新状态 → 干活 → 清状态）
- 常见坑（裸跑 pet.py、忘清状态、改错状态文件路径等）

给 agent 加载方式（Hermes）：把 skill 复制/链接到
`~/.hermes/skills/` 下，或在 agent 提示词里引用本项目 README 的
「配合 AI Agent 使用」章节即可。

## 技术路线

从下往上拆解（全链路不依赖 X11，纯安卓原生控件）：

```
┌─────────────────────────────────────────────┐
│ 插件层：skins/<皮肤名>/ 帧图 + config.json    │
│          换肤 = 换目录，不改代码               │
├─────────────────────────────────────────────┤
│ 状态层：轮询 ~/hermes11/pet-status.txt        │
│          (0.6s/次，内容变化显示到气泡)         │
├─────────────────────────────────────────────┤
│ 交互层：overlayTouch 事件 {x,y,action}        │
│          down→拖动起点 / move→setposition 移动 │
│          up→距离≤20px 判点击（1~2次开心,≥3哭）│
├─────────────────────────────────────────────┤
│ 渲染层：ImageView 帧动画（GIF 拆帧按原速循环,  │
│          PNG 帧兼容，字节流 setimage）         │
├─────────────────────────────────────────────┤
│ 窗口层：overlay 悬浮窗（系统级置顶、透明背景,   │
│          不占任务栈；0.1.6 构造 bug 手动绕过）  │
├─────────────────────────────────────────────┤
│ 通信层：termux-gui Python 库 → termux-am      │
│          广播 → Termux:GUI App → 系统控件      │
└─────────────────────────────────────────────┘
```

- **通信层**：termuxgui 库通过 termux-am 广播（Binder）与安卓端
  Termux:GUI App 通信，由 App 创建窗口/控件。termux-app 的 am.sock
  服务未启用，故用 wrapper 直连系统 am 命令绕过。
- **窗口层**：`newActivity(overlay=true)` 创建系统级悬浮窗：置顶显示、
  背景透明、不占任务栈 —— 这是桌宠能浮在任意界面上方的原因。
  termux-gui 0.1.6 有构造 bug（overlay 无 Task 只返回 aid 整数，
  库假定返回 (aid, tid)），代码里手动构造 Activity 绕过。
- **渲染层**：皮肤帧动画——有 GIF 时用 Pillow 拆帧、按 GIF 自带帧时长循环
  播放（qiki 皮肤 normal.gif 80 帧/3.2s 待机循环），无 GIF 时退回
  normal_1/normal_2 双帧 0.5s 呼吸动画；happy/cry 状态动画播完一轮
  自动回待机。图片以字节流 setimage 进 ImageView。
- **交互层**：overlayTouch 事件格式 `{x, y, action}`（屏幕绝对坐标），
  主循环非阻塞轮询：down 记录起点开始拖动 → move 计算位移
  setposition 移动窗口 → up 判断移动距离 ≤20px 算点击，
  计数 1~2 次触发开心反应，≥3 次触发委屈哭哭。
- **状态层**：每 0.6s 读状态文件 pet-status.txt，内容变化即显示到
  气泡 TextView，实现"琪琪正在做 XXX"的实时状态。
- **插件层**：皮肤目录约定 skins/<皮肤名>/ 放帧图 + config.json
  （气泡文案），换肤 = 换目录，零代码改动。

一句话总结：Python 进程 + termux-gui 广播协议 + Android overlay
悬浮窗 + 图片帧动画 + 触摸事件 + 文件轮询。

## 已知问题与实现要点

- termux-gui 0.1.6 的 overlay Activity 构造有 bug（库假定 newActivity 返回
  (aid, tid)，overlay 无 Task 只返回 aid 整数）→ 代码里手动
  `create_overlay_activity()` 绕过
- **ImageView 必须 setclickable(True)**：overlay 触摸走 onInterceptTouchEvent，
  子 View 不消费 DOWN 的话 move/up 不会持续派发（只有 down 日志，点击/拖动全失效）
- overlayTouch 事件格式是 `{x, y, action}`（屏幕绝对坐标），
  没有普通 touch 的 pointers 数组

## 协议

MIT License
