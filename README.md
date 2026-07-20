# Tennis Coach — 网球动作智能教练

基于百度人体分析 API 和 MediaPipe Pose 的网球动作分析系统，支持关节角度提取、标准模板训练、学员动作评估，以及通义千问 VL 语义补充建议。

---

## 功能

| 模式 | 说明 |
|------|------|
| **训练** | 上传标准技术动作照片，提取关节角度并保存为标准模板 |
| **评估** | 上传学员照片，自动识别动作阶段，对比标准模板给出改进建议 |
| **对比** | 同一张照片同时用百度 API 和 MediaPipe 两种方案分析，结果并排展示 |
| **VL 语义** | 在角度分析基础上，调用通义千问 VL 补充握拍、击球点等自然语言建议 |

---

## 环境要求

- Python 3.10 及以上
- pip

---

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/loriluan/tennis_coach.git
cd tennis_coach
```

### 2. （推荐）创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

依赖列表：

| 包 | 用途 |
|----|------|
| `requests` | 调用百度 API / 通义千问 API |
| `python-dotenv` | 从 `.env` 文件读取 API Keys |
| `mediapipe` | 本地姿态估计（无需联网） |
| `opencv-python` | 图片解码（MediaPipe 前处理） |
| `numpy` | 角度计算 |

### 4. 配置 API Keys

在项目根目录创建 `.env` 文件（已在 `.gitignore` 中，不会提交到 git）：

```ini
# 百度 AI — 人体分析
BAIDU_API_KEY=你的百度API_KEY
BAIDU_SECRET_KEY=你的百度Secret_Key

# 通义千问 — VL 语义分析（可选）
QIANWEN_API_KEY=你的通义千问API_KEY
```

- **百度 API**：在 [百度智能云控制台](https://console.bce.baidu.com/) 开通「人体分析」服务后获取。
- **通义千问 API**：在 [阿里云百炼](https://bailian.console.aliyun.com/) 开通后获取。不填则 VL 语义分析功能自动跳过。

---

## 启动服务

```bash
python server.py
```

终端输出：

```
Tennis Coach server at http://127.0.0.1:8080
```

打开浏览器访问 [http://127.0.0.1:8080](http://127.0.0.1:8080) 即可使用。

按 `Ctrl+C` 停止服务。

---

## 使用流程

1. **训练**：切换到「训练」标签页，选择动作类型（正手击球、发球等），上传标准动作照片，点击「提取并保存模板」。建议每个动作至少训练 3 张不同角度的照片。
2. **评估**：切换到「评估」标签页，上传学员照片，系统自动匹配最相近的动作模板并生成报告。
3. **对比**：切换到「对比」标签页，上传照片后可同时查看百度 API 和 MediaPipe 两种检测结果的差异。

---

## 项目结构

```
tennis_coach/
├── server.py                      # Web 服务器 + API 路由
├── requirements.txt
├── .env                           # API Keys（本地配置，不提交）
├── src/tennis_coach/
│   ├── data.py                    # 动作定义、角度阈值、建议文案
│   ├── keypoint.py                # 百度人体关键点 API 封装
│   ├── mediapipe_keypoint.py      # MediaPipe Pose 封装
│   ├── analyzer.py                # 角度计算 + 偏差分析
│   └── templates.py               # 标准模板读写
├── web/                           # 前端（纯 HTML / CSS / JS，无需构建）
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── data/
    ├── tennis_templates.json      # 训练生成的标准模板
    └── tennis_samples/            # 示例图片
```

---

## API 端点（供调试）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/api/tennis-templates` | 查看已训练的模板摘要 |
| POST | `/api/tennis-keypoint`  | 提取单张图片关键点 |
| POST | `/api/tennis-train`     | 训练并保存标准模板 |
| POST | `/api/tennis-evaluate`  | 评估学员动作 |
| POST | `/api/tennis-compare`   | 双方案对比分析 |

---

## 常见问题

**Q: 提示 `BAIDU_API_KEY 或 BAIDU_SECRET_KEY 未配置`**  
确认 `.env` 文件存在于项目根目录，且 Key 名称拼写正确（区分大小写）。

**Q: MediaPipe 检测不到人体**  
MediaPipe 对图片质量要求较高，建议使用全身清晰、背景简洁的照片，人物占图片面积 30% 以上。

**Q: VL 语义分析结果为空**  
检查 `.env` 中 `QIANWEN_API_KEY` 是否填写，以及阿里云账号是否有余额。此功能为可选项，不影响角度分析。
