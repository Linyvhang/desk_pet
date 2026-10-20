# 月牙雪熊桌宠

Windows 桌面宠物 MVP，使用 Python、PySide6 和现有 GIF 动作素材。

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

程序启动后，桌宠会以透明无边框窗口显示。右键桌宠可以选择动作、暂停自动行为、置顶、隐藏、保存或退出。

- 拖动：按住左键移动桌宠
- 普通点击：放松动作
- 约 0.8 秒内连续三次点击：受击动作
- Ctrl+左键：生气动作
- 长时间无互动：睡觉动作

## 测试

```powershell
pytest
```

如果当前机器没有 Python，可使用项目技术方案中指定的 Python 3.12+ 环境。Qt 无头测试环境可以设置 `QT_QPA_PLATFORM=offscreen`。

## 打包

```powershell
pyinstaller --noconfirm --clean --windowed --name YueyaSnowBear `
  --add-data "月牙雪熊;月牙雪熊" run.py
```

MVP 首选 one-folder 输出，确认资源和运行环境稳定后再评估 one-file 包。
