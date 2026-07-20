# Tennis Coach — 网球动作智能教练

基于百度人体分析 API 和 MediaPipe Pose 的网球动作分析系统。上传照片即可提取关节角度、与标准模板对比，并给出改进建议。可选接入通义千问 VL 获取自然语言语义分析。

GitHub: https://github.com/loriluan/tennis_coach

---

## 功能

| 模式 | 说明 |
|------|------|
| **训练** | 上传标准技术动作照片，提取关节角度并保存为模板 |
| **评估** | 上传学员照片，自动匹配动作阶段，对比模板给出改进建议 |
| **对比** | 同一张照片同时用百度 API 和 MediaPipe 两种方案分析，结果并排展示 |
| **VL 语义** | 调用通义千问 VL 补充握拍、击球点等自然语言建议（可选） |

---

## 环境要求

- **Python 3.10 或以上**（推荐 3.11 / 3.12 / 3.13）
- pip
- 网络连接（用于调用百度 API；MediaPipe 首次运行需下载约 30 MB 模型）

---

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/loriluan/tennis_coach.git
cd tennis_coach
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

> **注意（macOS Homebrew Python）**：如果提示 `externally-managed-environment`，改用：
> ```bash
> pip install -r requirements.txt --break-system-packages
> ```
> 或先按步骤 2 创建虚拟环境再安装（推荐）。

安装完成后验证：

```bash
python -c "import mediapipe, cv2, requests, dotenv, numpy; print('OK')"
# 输出 OK 即表示依赖安装成功
```

### 4. 配置 API Keys

在项目根目录创建 `.env` 文件（已在 `.gitignore` 中，不会提交到 git）：

```ini
# 百度 AI — 人体分析（必填）
BAIDU_API_KEY=你的百度API_KEY
BAIDU_SECRET_KEY=你的百度Secret_Key

# 通义千问 — VL 语义分析（可选，不填则跳过该功能）
QIANWEN_API_KEY=你的通义千问API_KEY
```

**百度 API 申请**：
1. 登录 [百度智能云控制台](https://console.bce.baidu.com/)
2. 搜索「人体分析」，开通免费额度
3. 在「应用列表」新建应用，获取 `API Key` 和 `Secret Key`

**通义千问 API 申请**（可选）：
1. 登录 [阿里云百炼](https://bailian.console.aliyun.com/)
2. 开通服务后，在「API-KEY 管理」创建密钥

---

## 启动服务

```bash
python server.py
```

终端输出：

```
Tennis Coach server at http://127.0.0.1:8080
```

打开浏览器访问 [http://127.0.0.1:8080](http://127.0.0.1:8080)。

按 `Ctrl+C` 停止服务。

---

## 使用流程

### 训练标准模板

1. 点击「训练模式」
2. 选择动作类型（正手击球 - 击球瞬间、发球 - 击球瞬间 等）
3. 上传该动作的标准照片，点击「提取关键点并保存模板」
4. 建议每个动作至少训练 3 张照片，系统自动取均值

### 评估学员动作

1. 点击「评估模式」
2. 上传学员照片（全身清晰、背景简洁为佳）
3. 系统自动匹配最接近的动作阶段，生成角度对比报告和改进建议

### 对比两种检测方案

1. 点击「百度 vs MediaPipe 对比」
2. 上传照片，点击「同时分析（两种方案）」
3. 左侧展示百度 API 结果，右侧展示 MediaPipe 结果

> **MediaPipe 注意事项**：
> - 首次运行会自动下载约 30 MB 的模型文件，需等待 10–30 秒
> - 对图片质量要求较高：人物应占画面 30% 以上，全身清晰可见，背景不宜过于复杂
> - 模型文件保存在 `data/pose_landmarker_heavy.task`，之后运行无需重新下载

---

## 项目结构

```
tennis_coach/
├── server.py                      # Web 服务器 + API 路由
├── requirements.txt               # Python 依赖
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
    ├── tennis_samples/            # 示例图片
    └── pose_landmarker_heavy.task # MediaPipe 模型（首次运行自动下载）
```

---

## 常见问题

**Q: 提示 `BAIDU_API_KEY 或 BAIDU_SECRET_KEY 未配置`**
确认 `.env` 文件存在于项目根目录（与 `server.py` 同级），Key 名称区分大小写。

**Q: `No module named 'cv2'` 或 `No module named 'mediapipe'`**
依赖没有装到当前 Python 环境。确认激活了虚拟环境后重新运行 `pip install -r requirements.txt`。

**Q: MediaPipe 首次运行很慢或超时**
需要从 Google 服务器下载模型（`pose_landmarker_heavy.task`，约 30 MB）。网络不稳定时可能失败，重试即可。模型下载成功后保存在本地，后续不再下载。

**Q: MediaPipe 提示「未检测到人体」**
该方案对图片质量要求较严格：人物需占画面较大面积（建议 30% 以上），全身清晰、背景简洁。可先用百度 API 模式验证照片是否有效。

**Q: VL 语义分析无结果**
检查 `.env` 中 `QIANWEN_API_KEY` 是否填写，以及阿里云账号余额。此功能为可选项，不影响角度分析主功能。

**Q: 端口 8080 被占用**
更改 `server.py` 末尾的 `port = 8080` 为其他端口，如 `8888`。
