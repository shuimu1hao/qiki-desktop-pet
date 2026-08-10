# qiki 皮肤（GIF 动画参考模板）

这是本项目内置的 **GIF 动画皮肤参考示例**：三张透明背景 GIF，待机/开心/哭哭
三个状态全部是动画，运行时由 pet.py 用 Pillow 拆帧、按 GIF 自带帧时长循环播放。

| 文件 | 说明 | 规格 |
|------|------|------|
| normal.gif | 待机动画（必填） | 180x180，80 帧，40ms/帧（3.2s 循环） |
| happy.gif | 开心动画（点击 1~2 下） | 180x180，74 帧，40ms/帧 |
| cry.gif | 哭哭动画（连点 3 下） | 180x180，43 帧，40ms/帧 |
| config.json | 气泡文案 | 见主 README「皮肤接口」 |

想照着做自己的皮肤？完整制作步骤见
[references/skin-plugin-guide.md](../../references/skin-plugin-guide.md)。
