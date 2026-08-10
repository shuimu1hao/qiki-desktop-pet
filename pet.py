#!/data/data/com.termux/files/usr/bin/python3
# -*- coding: utf-8 -*-
"""
🐾 琪琪桌宠 (Qiki Desktop Pet) (=^･ω･^=)
用 termux-gui overlay 悬浮窗：
  - 显示桌宠形象（支持动画帧循环 + 开心/哭哭状态切换）
  - 显示琪琪的运行进度与当前任务（轮询状态文件）
  - 触摸反馈：
      · 拖动 = 移动桌宠
      · 点击 1~2 次 = 开心反应（举手帧 + 跳一下 + 气泡）
      · 连续点 3 次以上 = 委屈流泪（哭哭帧 + 气泡，5 秒后恢复）

┌─ 皮肤插件接口 ─────────────────────────────┐
│ skins/<皮肤名>/                             │
│   normal_1.png normal_2.png  (呼吸动画帧,必填)│
│   blink.png      (眨眼帧,可选)               │
│   happy.png      (开心帧,可选)               │
│   cry.png        (哭哭帧,可选)               │
│   config.json    (气泡文字/时长,可选)         │
│ 用法: python3 pet.py [--skin <皮肤名>]       │
└─────────────────────────────────────────────┘
运行（需要 wrapper 修 termux-am）：
  PATH=~/hermes11/gui-demo/bin:$PATH python3 pet.py [--skin default]
"""
import os
import sys
import json
import time

from termuxgui import (Activity, Connection, ImageView, TextView,
                       LinearLayout, Event)

# ---------- 配置 ----------
PET_DIR = os.path.expanduser("~/hermes11/pet")
SKINS_DIR = os.path.join(PET_DIR, "skins")
STATUS_FILE = os.path.expanduser("~/hermes11/pet-status.txt")  # 任务状态文件

IDLE_TEXT = "琪琪待命中喵~"
POLL_SEC = 0.6          # 状态文件轮询间隔
TAP_RESET_SEC = 2.0     # 点击计数重置间隔
CRY_SEC = 5.0           # 委屈流泪持续时长
CLICK_DIST = 20         # 判定为点击的最大移动距离(px)
JUMP_PX = 14            # 开心跳一下的像素
HAPPY_SEC = 1.2         # 开心反应气泡停留时长
ANIM_SEC = 0.5          # 呼吸动画帧切换间隔

BG_TRANSPARENT = 0x00000000
BUBBLE_BG = 0x88000000  # 半透明黑底气泡

DEBUG_LOG = os.path.join(PET_DIR, "pet-debug.log")  # 调试日志（可关：设 None）

DEFAULT_CFG = {
    "bubbles": ["喵~开心！", "嘿嘿~", "最喜欢主人了喵！", "蹭蹭~"],
    "cry_bubble": "呜哇...主人欺负琪琪 QAQ",
    "idle_text": "琪琪待命中喵~",
}


class Skin:
    """皮肤插件：从 skins/<name>/ 目录读取帧图片与配置。"""
    def __init__(self, name="default"):
        self.dir = os.path.join(SKINS_DIR, name)
        self.cfg = dict(DEFAULT_CFG)
        cfg_path = os.path.join(self.dir, "config.json")
        if os.path.isfile(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    self.cfg.update(json.load(f))
            except Exception:
                pass
        self.normal = self._load_list(["normal_1.png", "normal_2.png"])
        self.blink = self._load_one("blink.png")
        self.happy = self._load_one("happy.png")
        self.cry = self._load_one("cry.png")

    def _path(self, fn):
        return os.path.join(self.dir, fn)

    def _load_list(self, names):
        out = []
        for n in names:
            p = self._path(n)
            if os.path.isfile(p):
                with open(p, "rb") as f:
                    out.append(f.read())
        return out

    def _load_one(self, name):
        return self._load_list([name])[0] if os.path.isfile(self._path(name)) else None

    def ok(self):
        return bool(self.normal)


def read_status():
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            txt = f.read().strip()
        return txt if txt else "待命中喵~"
    except OSError:
        return "待命中喵~"


def set_img(img, data):
    if data:
        img.setimage(data)


def create_overlay_activity(c):
    """手动创建 overlay Activity（绕过 termuxgui 0.1.6 的 overlay bug：
    库假定 newActivity 返回 (aid, tid)，但 overlay 无 Task 只返回 aid 整数）。"""
    res = c.send_read_msg({"method": "newActivity",
                           "params": {"overlay": True, "canceloutside": True,
                                      "intercept": False}})
    aid = res
    a = Activity.__new__(Activity)
    a.c = c
    a.aid = aid
    a.t = None
    return a


def main():
    skin_name = "default"
    if "--skin" in sys.argv:
        i = sys.argv.index("--skin")
        if i + 1 < len(sys.argv):
            skin_name = sys.argv[i + 1]
    skin = Skin(skin_name)
    if not skin.ok():
        print(f"皮肤 {skin_name} 没有 normal_1.png，请检查 {SKINS_DIR}/{skin_name}/", file=sys.stderr)
        return

    c = Connection()
    a = create_overlay_activity(c)
    a.settheme(0x00000000, 0x00000000, BG_TRANSPARENT, 0xFFFFFFFF, 0xFF80DEEA)
    a.sendoverlayevents(True)

    root = LinearLayout(a)
    root.setbackgroundcolor(BG_TRANSPARENT)

    img = ImageView(a, root)
    set_img(img, skin.normal[0])
    img.setdimensions("wrap", "wrap")
    # ⚠️ 关键：ImageView 必须 clickable！termux-gui overlay 触摸走
    # onInterceptTouchEvent，子 View 不消费 DOWN 的话 move/up 事件不会持续
    # 派发（实测日志只有 down，点击/拖动全失效）。clickable=true 后
    # 触摸序列完整：down → move → up。
    img.setclickable(True)

    bubble = TextView(a, skin.cfg["idle_text"], root)
    bubble.settextsize(13)
    bubble.settextcolor(0xFFFFFFFF)
    bubble.setbackgroundcolor(BUBBLE_BG)
    bubble.setdimensions("wrap", "wrap")
    bubble.setvisibility(2)

    try:
        cfg = c.getconfiguration(a.aid)
        sw = int(round(cfg.get("screenwidth", 0) * cfg.get("density", 1)))
        sh = int(round(cfg.get("screenheight", 0) * cfg.get("density", 1)))
    except Exception:
        sw, sh = 1080, 2044
    if sw < 100:
        sw, sh = 1080, 2044
    wx, wy = sw - 200, 120
    a.setposition(wx, wy)

    # 状态
    tap_count = 0
    last_tap = 0.0
    cry_until = 0.0
    happy_until = 0.0
    happy_idx = 0
    bubble_visible = False
    dragging = False
    down_x = down_y = 0
    win_x0 = win_y0 = 0
    last_status = None
    last_poll = 0.0
    last_heartbeat = time.time()
    anim_i = 0
    last_anim = 0.0

    def show_bubble(text, secs):
        nonlocal bubble_visible, happy_until
        bubble.settext(text)
        bubble.setvisibility(0)
        bubble_visible = True
        happy_until = time.time() + secs

    def hide_bubble():
        nonlocal bubble_visible
        bubble.setvisibility(2)
        bubble_visible = False

    def play_happy():
        nonlocal happy_until, happy_idx
        happy_until = time.time() + HAPPY_SEC
        happy_idx = (happy_idx + 1) % len(skin.cfg["bubbles"])
        show_bubble(skin.cfg["bubbles"][happy_idx], HAPPY_SEC)
        if skin.happy:
            set_img(img, skin.happy)
        a.setposition(wx, wy - JUMP_PX)
        time.sleep(0.12)
        a.setposition(wx, wy)

    def play_cry():
        nonlocal cry_until, tap_count
        cry_until = time.time() + CRY_SEC
        tap_count = 0
        if skin.cry:
            set_img(img, skin.cry)
        show_bubble(skin.cfg["cry_bubble"], CRY_SEC)

    while True:
        now = time.time()

        # ---- 非阻塞取事件 ----
        while True:
            ev = c.checkevent()
            if ev is None:
                break
            t = ev.type
            if t == Event.overlaytouch:
                val = ev.value
                action = val.get("action", "")
                # ⚠️ overlayTouch 事件格式是 {x, y, action}（屏幕绝对坐标），
                # 没有普通 touch 的 pointers 数组（termux-gui 源码 v0json.kt 实测）
                px = val.get("x", 0)
                py = val.get("y", 0)
                if DEBUG_LOG:
                    with open(DEBUG_LOG, "a", encoding="utf-8") as f:
                        f.write(f"[{time.strftime('%H:%M:%S')}] overlayTouch action={action} x={px} y={py}\n")

                if action == "down":
                    dragging = True
                    down_x, down_y = px, py
                    win_x0, win_y0 = wx, wy
                elif action == "move" and dragging:
                    dx, dy = px - down_x, py - down_y
                    wx = max(0, min(win_x0 + dx, sw - 60))
                    wy = max(0, min(win_y0 + dy, sh - 100))
                    a.setposition(wx, wy)
                elif action == "up":
                    if dragging:
                        dist = ((px - down_x) ** 2 + (py - down_y) ** 2) ** 0.5
                        if dist <= CLICK_DIST:
                            tap_count += 1
                            last_tap = now
                            if tap_count >= 3:
                                play_cry()
                            else:
                                play_happy()
                        dragging = False
            elif t == Event.destroy:
                return

        # ---- 心跳 ----
        if now - last_heartbeat < 0.05:
            time.sleep(0.02)
            continue
        last_heartbeat = now

        if tap_count and now - last_tap > TAP_RESET_SEC:
            tap_count = 0
        if cry_until and now >= cry_until:
            cry_until = 0
            if skin.normal:
                set_img(img, skin.normal[0])
        if bubble_visible and cry_until == 0 and now >= happy_until:
            hide_bubble()

        # 呼吸动画（非开心/哭状态时循环 normal 帧）
        if cry_until == 0 and happy_until < now and len(skin.normal) > 1:
            if now - last_anim >= ANIM_SEC:
                last_anim = now
                anim_i = (anim_i + 1) % len(skin.normal)
                set_img(img, skin.normal[anim_i])

        # 轮询状态文件
        if now - last_poll >= POLL_SEC:
            last_poll = now
            status = read_status()
            if status != last_status:
                last_status = status
                if not bubble_visible and cry_until == 0:
                    show_bubble(status, 2.0)
                else:
                    bubble.settext(status)
        time.sleep(0.02)


if __name__ == "__main__":
    main()
