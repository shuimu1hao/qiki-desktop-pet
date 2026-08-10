# 皮肤插件参考（Skin Plugin Guide）

桌宠的皮肤是**插件化**的：换肤 = 换目录，不用改任何代码。
本参考以 `skins/qiki/`（GIF 动画皮肤）为模板，说明皮肤接口规格与制作步骤。

## 1. 皮肤目录约定

皮肤放在 `skins/<皮肤名>/`，启动时用 `--skin <皮肤名>` 指定：

```bash
bash pet-ctl.sh start qiki      # 用 qiki 皮肤启动
bash pet-ctl.sh start 我的皮肤   # 用任意皮肤名启动
```

## 2. 文件规格

### GIF 动画皮肤（推荐，本项目参考模板 = skins/qiki/）

| 文件 | 是否必填 | 说明 |
|------|---------|------|
| `normal.gif` | ✅ | 待机动画，运行时用 Pillow 拆帧、按 GIF 自带帧时长循环播放 |
| `happy.gif` | ❌ | 开心动画（点击 1~2 下播放，播完一轮自动回待机） |
| `cry.gif` | ❌ | 哭哭动画（连点 3 下播放，播完一轮自动回待机） |
| `config.json` | ❌ | 气泡文字配置 |

### PNG 帧皮肤（旧格式，兼容）

| 文件 | 是否必填 | 说明 |
|------|---------|------|
| `normal_1.png` / `normal_2.png` | ✅ | 呼吸动画双帧，每 0.5s 切换 |
| `happy.png` | ❌ | 开心单帧（点击时显示） |
| `cry.png` | ❌ | 哭哭单帧（连点 3 下显示） |
| `blink.png` | ❌ | 眨眼帧（暂未启用） |
| `config.json` | ❌ | 气泡文字配置 |

GIF 与 PNG 可以混用（如只有 `normal.gif` 时 happy/cry 会复用待机动画）。

### config.json 配置项

```json
{
  "bubbles": ["喵~开心！", "嘿嘿~", "最喜欢主人了喵！", "蹭蹭~"],
  "cry_bubble": "呜哇...主人欺负琪琪 QAQ",
  "idle_text": "琪琪待命中喵~"
}
```

- `bubbles`：点击开心时依次轮播的气泡文案
- `cry_bubble`：连点 3 下时的哭哭气泡文案
- `idle_text`：待命气泡文案

## 3. 参考模板：qiki 皮肤

`skins/qiki/` 是内置的 GIF 动画皮肤参考示例，规格如下：

| 文件 | 尺寸 | 帧数 | 帧时长 | 循环时长 |
|------|------|------|--------|---------|
| normal.gif | 180x180 | 80 | 40ms | 3.2s |
| happy.gif | 180x180 | 74 | 40ms | 2.96s |
| cry.gif | 180x180 | 43 | 40ms | 1.84s |

要点：
- **透明背景**（RGBA）——悬浮窗才能只显示形象、不显示黑底
- 三张 GIF 尺寸、帧时长保持一致，切换状态时画面不跳变
- 帧时长建议 40~100ms（过短 CPU 占用高，过长显得卡顿）

## 4. 制作一个新皮肤（照 qiki 模板抄）

```bash
# 1. 复制模板
cd ~/hermes11/pet
cp -r skins/qiki skins/我的皮肤

# 2. 替换素材：把做好的透明背景 GIF 覆盖进去
#    待机动画 → normal.gif（必填）
#    开心动画 → happy.gif（可选）
#    哭哭动画 → cry.gif（可选）

# 3. 可选：改 config.json 气泡文案

# 4. 启动
bash pet-ctl.sh start 我的皮肤
```

素材制作提示：
- 推荐 180x180 或 256x256（正方形，悬浮窗缩放观感最好）
- 用 AI 生图/画师出图后转 GIF（如 ffmpeg：`ffmpeg -i 帧%03d.png -loop 0 -delay 4 normal.gif`）
- 导出时保持透明通道，帧数 40~90 帧即可（帧太多拆帧内存占用高）

## 5. 验证皮肤

```bash
bash pet-ctl.sh status                  # 确认桌宠在跑、皮肤名
tail -20 pet-run.log                    # 无报错 = 加载正常
```

皮肤目录缺 `normal.gif`（或 PNG 帧）时会启动失败，`pet-run.log` 会提示缺文件。
