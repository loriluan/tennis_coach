# Tennis Coach — 网球动作智能教练

基于百度人体分析 API 和 MediaPipe Pose 的网球动作分析系统。

## 功能

- **训练模式**：上传标准技术动作照片，提取关节角度并保存为标准模板
- **评估模式**：上传学员照片，自动识别动作阶段，对比标准模板给出改进建议
- **对比模式**：同一张照片同时用百度 API 和 MediaPipe 两种方案分析，结果并排展示
- **通义千问 VL**：在角度分析基础上补充握拍、击球点等语义建议

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器（端口 8080）
python server.py
```

然后打开 http://127.0.0.1:8080

## 项目结构

```
tennis_coach/
├── server.py              # Web 服务器 + API 端点
├── requirements.txt
├── .env                   # API Keys（不提交到 git）
├── src/tennis_coach/
│   ├── data.py            # 动作定义、角度阈值、建议文案
│   ├── keypoint.py        # 百度人体关键点 API
│   ├── mediapipe_keypoint.py  # MediaPipe Pose
│   ├── analyzer.py        # 角度计算 + 偏差分析
│   └── templates.py       # 标准模板读写
├── web/                   # 前端（HTML/CSS/JS）
└── data/
    ├── tennis_templates.json  # 训练好的标准模板
    └── tennis_samples/        # 样本图片
```
