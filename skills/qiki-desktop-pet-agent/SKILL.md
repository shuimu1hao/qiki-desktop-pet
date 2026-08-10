---
name: qiki-desktop-pet-agent
description: Use when agent needs to interact with the Qiki desktop pet (start/stop/status bubbles).
version: 1.0.0
author: shuimu1hao
license: MIT
metadata:
  hermes:
    tags: [desktop-pet, termux-gui, overlay, agent-status, android]
    related_skills: [termux-tooling]
---

# 琪琪桌宠 × Agent 交互协议 (Qiki Desktop Pet Agent Protocol)

桌宠（qiki-desktop-pet）是 AI agent 的可视化状态窗口：agent 干活时，
桌宠实时显示它正在做什么；主人瞄一眼悬浮窗就知道进度。

## Overview

- 桌宠本体：termux-gui overlay 悬浮窗（Android/Termux），Python 实现
- 交互面：两个脚本 `pet-ctl.sh`（生命周期）+ `pet-status.sh`（状态气泡）
- agent 只需要会调这两个脚本，不需要碰 pet.py 内部
- 状态文件：`~/hermes11/pet-status.txt`（桌宠每 0.6s 轮询）

## When to Use

- 桌宠已在运行，agent 开始/结束一个任务，想把进度显示到桌宠气泡
- 需要启动/关闭/重启桌宠，或确认桌宠是否在跑
- 写 agent 自动化流程时，需要把桌宠状态更新编进任务流程

Don't use for:
- 修改桌宠外观/皮肤（那是换目录，见项目 README）
- 桌宠自身的 bug 修复（那是改 pet.py 的事）

## 状态更新协议（pet-status.sh）

```bash
# agent 开始任务 → 更新状态（桌宠气泡立即显示）
bash ~/hermes11/pet/pet-status.sh "正在处理：上传 GitHub"

# agent 任务完成 / 空闲 → 清除状态（回到待命气泡）
bash ~/hermes11/pet/pet-status.sh
```

规则：
1. 长任务开始时必须先更新状态，结束或空闲后必须清除
2. 状态文本要简短口语化（气泡空间有限），如"正在处理：xxx"
3. 多次子任务可以连续覆盖更新，不用先清再设

## 生命周期管理（pet-ctl.sh）

```bash
bash ~/hermes11/pet/pet-ctl.sh start        # 启动桌宠（默认皮肤 default）
bash ~/hermes11/pet/pet-ctl.sh start 泳装   # 指定皮肤启动
bash ~/hermes11/pet/pet-ctl.sh stop         # 关闭（自动清状态文件）
bash ~/hermes11/pet/pet-ctl.sh restart      # 重启
bash ~/hermes11/pet/pet-ctl.sh status       # 查看运行状态（返回 pid/状态气泡）
```

规则：
1. 启动/关闭一律走 pet-ctl.sh，**禁止裸跑 `python3 pet.py &`**
   （脚本会注入 termux-am wrapper PATH、防重复启动、stop 清状态）
2. 脚本自带防重复启动：已在跑时再 start 会提示不重复拉起
3. 桌宠是长驻进程，agent 会话结束不自动杀（nohup 后台）

## 典型流程示例

```bash
# 1. 确认桌宠状态
bash ~/hermes11/pet/pet-ctl.sh status

# 2. 没在跑就启动
bash ~/hermes11/pet/pet-ctl.sh start

# 3. 开始长任务 → 播报状态
bash ~/hermes11/pet/pet-status.sh "正在处理：整理文档"

# ... 干活 ...

# 4. 任务完成 → 清除状态
bash ~/hermes11/pet/pet-status.sh
```

## Common Pitfalls

1. **裸跑 python3 pet.py &** → 没有 wrapper PATH 注入，termux-gui 连不上
   （报 am broadcast 错误）；也没防重复启动。一律用 pet-ctl.sh。
2. **任务完成忘了清状态** → 桌宠气泡一直挂着旧任务，主人误以为还在干活。
   结束/空闲必须 `pet-status.sh` 清一次。
3. **状态文件路径改错** → 桌宠硬编码轮询 `~/hermes11/pet-status.txt`；
   移动/改名需同步改 pet.py 的 STATUS_FILE，否则气泡不更新。
4. **以为 status 命令会启动桌宠** → status 只读不写，桌宠没跑时返回
   "⚪ 桌宠未运行"，需要先 start。

## Verification Checklist

- [ ] `pet-ctl.sh status` 能看到运行状态（🟢/⚪）
- [ ] `pet-status.sh "正在处理：xxx"` 后桌宠气泡出现对应文字
- [ ] `pet-status.sh` 清空后桌宠回到待命气泡
- [ ] 长任务流程里 start → 更新状态 → 干活 → 清状态 顺序正确
