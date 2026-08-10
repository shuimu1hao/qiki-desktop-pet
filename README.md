# 琪琪桌宠 (Qiki Desktop Pet)

一只会呼吸、会卖萌、能拖动、能互动的桌面宠物喵～(≧▽≦)

基于 termux-gui 的 overlay 悬浮窗实现，运行在 Android + Termux 环境：
显示桌宠形象（呼吸动画帧循环），实时展示琪琪的当前任务状态，支持触摸互动。

## 功能特性

- 🖼️ 悬浮窗桌宠：overlay 置顶显示，不遮挡操作
- 🐱 呼吸动画：normal_1 / normal_2 两帧循环，形象活灵活现
- ✋ 触摸拖动：按住桌宠随意移动位置
- 😊 点击互动：点 1~2 下 → 开心反应（举手跳一下 + 气泡）
- 😭 连点惩罚：连续点 3 下以上 → 委屈哭哭（哭脸 + 气泡，5 秒后恢复）
- 💬 任务状态：轮询状态文件实时显示琪琪正在做什么
- 🎨 皮肤插件化：换皮只需换目录，不用改代码

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
| normal_1.png | ✅ | 呼吸动画帧 1 |
| normal_2.png | ✅ | 呼吸动画帧 2 |
| blink.png | ❌ | 眨眼帧（暂未启用） |
| happy.png | ❌ | 开心帧（点击时显示） |
| cry.png | ❌ | 哭哭帧（连点3下显示） |
| config.json | ❌ | 气泡文字配置 |

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
├── skins/              # 皮肤目录
│   └── default/        # 默认皮肤（琪琪）
│       ├── normal_1.png / normal_2.png
│       ├── happy.png / cry.png
│       └── config.json
└── pet-debug.log       # 调试日志（运行时生成，已 gitignore）
```

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
