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
| **视频分析** | 上传网球动作视频，自动提取关键帧并逐帧分析，生成完整动作评估报告 |
| **VL 语义** | 调用通义千问 VL 补充握拍、击球点等自然语言建议（可选） |

---

## 环境要求

- **Python 3.10**（项目使用 conda 环境 `ai-camp`）
- pip
- 网络连接（用于调用百度 API；MediaPipe 首次运行需下载约 30 MB 模型）

---

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/loriluan/tennis_coach.git
cd tennis_coach
```

### 2. 使用 conda 环境（推荐）

本项目已配置 conda 环境 `ai-camp`，其中包含所有依赖（包括 mediapipe）。

```bash
# 激活环境
conda activate ai-camp
```

### 3. 安装依赖

如果环境中缺少依赖，运行：

```bash
pip install -r requirements.txt
```

安装完成后验证：

```bash
python -c "import mediapipe, cv2, requests, dotenv, numpy; print('OK')"
# 输出 OK 即表示依赖安装成功
```

> **注意**：MediaPipe 目前仅支持 Python 3.10 及以下版本。如果使用系统自带的 Python 3.13/3.12，可能无法安装 mediapipe。请使用 conda 环境 `ai-camp`（Python 3.10）。

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

### 方式一：使用 run.sh（推荐）

```bash
chmod +x run.sh
./run.sh
```

### 方式二：手动启动

```bash
conda activate ai-camp
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

系统支持两种训练方式：

#### 方式一：图片训练
1. 点击「训练模式」
2. 在「方式一：图片训练」中选择动作类型
3. 上传该动作的标准照片
4. 点击「提取关键点并保存模板」
5. 建议每个动作至少训练 3 张照片，系统自动取均值

#### 方式二：视频训练（推荐）
1. 在「方式二：视频训练」中选择动作类型
2. 选择检测方案（推荐 MediaPipe，支持3D）
3. 选择模板策略：
   - **多帧平均**（推荐）：使用所有成功帧的角度平均值，充分利用视频信息
   - **最佳帧**：选择得分最高的单帧
   - **第一帧**：使用视频第一帧
4. 上传标准动作视频（支持 MP4、MOV、AVI）
5. 点击「从视频训练模板」
6. 系统自动提取关键帧，分析后保存最佳帧或平均帧作为模板

**视频训练优势**：
- 一次上传，自动提取所有关键帧
- 多帧平均，充分利用视频信息，更准确
- 自动计算最佳动作角度
- 减少单帧噪声和误差

### 评估学员动作

1. 点击「评估模式」
2. 上传学员照片（全身清晰、背景简洁为佳）
3. 系统自动匹配最接近的动作阶段，生成角度对比报告和改进建议

### 视频分析

1. 点击「视频分析」
2. 选择检测方案（推荐 MediaPipe，支持3D角度）
3. 调整分析设置（最大帧数、帧间隔）
4. 上传网球动作视频（支持 MP4、MOV、AVI 等格式）
5. 点击「开始分析视频」
6. 系统自动提取关键帧，逐帧分析动作角度
7. 生成完整报告，包括：
   - 平均得分和成功分析帧数
   - 检测到的动作类型和次数
   - 最常见问题统计
   - 最佳动作帧和最需改进帧
   - 问题帧详情（前10帧）

### 对比两种检测方案

1. 点击「百度 vs MediaPipe 对比」
2. 上传照片，点击「同时分析（两种方案）」
3. 左侧展示百度 API 结果，右侧展示 MediaPipe 结果

### 视频分析注意事项

- **视频质量**：建议使用清晰、背景简洁的视频，人物占画面 30% 以上
- **视频长度**：建议 10-30 秒，系统默认提取最多 30 帧（可调整）
- **检测方案**：推荐使用 MediaPipe，支持 3D 角度计算，准确率更高
- **分析时间**：根据视频长度和帧数，分析可能需要 10-60 秒
- **帧间隔**：默认每 0.5 秒提取一帧，可根据动作速度调整（0.2-2 秒）

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
│   ├── analyzer.py                # 角度计算 + 偏差分析（支持2D/3D）
│   ├── templates.py               # 标准模板读写（带内存缓存）
│   ├── history.py                 # 评估历史记录管理
│   ├── utils.py                   # 工具函数（Token缓存、文件校验）
│   └── video_analyzer.py          # 视频分析模块（帧提取、逐帧分析）
├── web/                           # 前端（纯 HTML / CSS / JS，无需构建）
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── data/
    ├── tennis_templates.json      # 训练生成的标准模板
    ├── tennis_samples/            # 示例图片
    ├── history.json               # 评估历史记录
    └── pose_landmarker_heavy.task # MediaPipe 模型（首次运行自动下载）
```

---

## 常见问题

**Q: 提示 `BAIDU_API_KEY 或 BAIDU_SECRET_KEY 未配置`**
确认 `.env` 文件存在于项目根目录（与 `server.py` 同级），Key 名称区分大小写。

**Q: `No module named 'cv2'` 或 `No module named 'mediapipe'`**
依赖没有装到当前 Python 环境。确认激活了 conda 环境 `ai-camp` 后重新运行 `pip install -r requirements.txt`。

**Q: 使用 Python 3.13/3.12 时无法安装 mediapipe**
MediaPipe 目前仅支持 Python 3.10 及以下版本。请使用 conda 环境 `ai-camp`（Python 3.10），或使用项目提供的 `run.sh` 脚本启动服务。

**Q: MediaPipe 首次运行很慢或超时**
需要从 Google 服务器下载模型（`pose_landmarker_heavy.task`，约 30 MB）。网络不稳定时可能失败，重试即可。模型下载成功后保存在本地，后续不再下载。

**Q: MediaPipe 提示「未检测到人体」**
该方案对图片质量要求较严格：人物需占画面较大面积（建议 30% 以上），全身清晰、背景简洁。可先用百度 API 模式验证照片是否有效。

**Q: VL 语义分析无结果**
检查 `.env` 中 `QIANWEN_API_KEY` 是否填写，以及阿里云账号余额。此功能为可选项，不影响角度分析主功能。

**Q: 端口 8080 被占用**
更改 `server.py` 末尾的 `port = 8080` 为其他端口，如 `8888`。

**Q: 视频分析失败或速度慢**
- 确保视频格式为 MP4/MOV/AVI，编码为 H.264
- 视频分辨率建议 720p 或 1080p，过高会增加处理时间
- 减少最大帧数或增大帧间隔可以加快分析速度
- MediaPipe 方案比百度 API 慢，但支持 3D 角度计算

**Q: 视频分析结果不准确**
- 确保视频中人物清晰可见，动作完整
- 建议从正面或侧面 45 度角拍摄
- 使用 MediaPipe 方案获得更高的准确率
- 确保已训练相应的标准动作模板

**Q: 视频训练和图片训练有什么区别？**
- **图片训练**：单张图片，简单快速，适合精确控制
- **视频训练**：多帧分析，自动选最佳帧，更稳定准确
- 建议：关键动作用图片训练，完整动作用视频训练

**Q: 视频训练应该选择哪种策略？**
- **多帧平均**（推荐）：使用所有成功帧的角度平均值，充分利用视频信息，最准确
- **最佳帧**：选择得分最高的单帧，适合动作清晰的标准视频
- **第一帧**：使用视频第一帧，适合第一帧就是最佳动作的场景
