课题名称：基于计算机视觉的网球动作分析系统

摘要：
目前大量网球爱好者在训练中缺乏持续教练陪伴，动作不规范难以及时纠正，影响训练效果。本课题提出并实现了一个基于人体关键点的网球动作分析系统：使用 MediaPipe 本地姿态估计或百度人体云端 API 提取关键点，基于向量点积计算关节角度，采用加权 RMSE 与模板匹配实现动作阶段自动识别，并生成 0–100 的量化评分与针对性改进建议。为补足难以用角度量化的细节（如握拍方式、击球节奏），系统设计了将多模态大语言模型纳入建议生成的可扩展接口。系统以 Python 实现，模块化设计，支持静态图像与视频批量分析，并保存历史记录以便进度追踪。

关键词：计算机视觉；姿态估计；网球动作分析；关节角度；MediaPipe；Python

1 引言

1.1 课题来源与背景
自基层网球训练的体验出发，业余球员在无教练陪伴下难以准确判断动作质量，传统视频回放依赖主观判断且缺乏量化指标。计算机视觉中的人体姿态估计可自动获取关键点坐标，为动作量化评价提供基础。本课题将该技术与运动学指标、模板匹配和自然语言建议结合，面向爱好者与教练提供可复现的训练反馈体系。

1.2 研究目的与意义
- 自动识别人体 17 个关键点并可视化。
- 计算 7 个核心关节角度并与标准模板比较，输出 0–100 分评分。
- 无需手工标注动作类型：通过 RMSE 最小化自动匹配动作阶段。
- 生成针对每个问题关节的可执行改进建议，并提供历史趋势追踪。

1.3 查新情况
对比现有文献与产品，本系统优势在于：支持本地 MediaPipe 与可选云 API 双方案；将几何量化与语言模型结合以覆盖语义细节；和低门槛的自动阶段匹配策略。

2 技术原理与总体思路

2.1 总体架构（功能模块）
- 关键点提取模块（MediaPipe 本地 / 百度云端），实现文件：src/tennis_coach/mediapipe_keypoint.py 与 src/tennis_coach/keypoint.py。
- 角度计算模块：src/tennis_coach/analyzer.py。
- 模板库管理：src/tennis_coach/templates.py。
- 模型匹配与评分：加权 RMSE 与非线性惩罚评分。
- 建议生成：基于规则引擎的映射，和预留的大模型接口。
- 历史记录管理与可视化：src/tennis_coach/history.py。

图 1：系统总体技术路线图（在最终稿中插入 pipeline_flowchart.html 的截图并置入图注）。

2.2 关键数学模型与符号说明
符号约定：
- 关键点集合：对于一张图片（或视频帧），以字典表示的关键点为 P，其中单点 p ∈ P 表示为 p = (x_p, y_p, z_p, s_p)，其中 x,y 为像素坐标，z 为相对深度，s 表示关键点置信度。
- 角度集合：对某一定义角度 i，用 A_i 表示其值（以度为单位）。模板对应角度记为 T_i，学员测得角度记为 S_i。
- 权重集：w_i 表示角度 i 的重要性权重（例如肩和肘权重更大）。
- 阈值：τ_i 表示在某动作阶段允许的角度偏差阈值（度）。

2.2.1 关节角度计算（向量点积法）
设角度 A 对应三点 a, b, c（以 b 为顶点），构造向量 u = a − b，v = c − b。则角度 θ 由向量点积定义：

$$
theta = \arccos\left(\dfrac{u\cdot v}{\|u\|\|v\|}\right)
$$

其中 u·v 表示向量点积，若使用 3D 则包含 z 分量。若模长接近 0 则该角度不可计算。

代码段 1（角度计算核心函数，已在论文正文解释）：

```
def calc_angle(a, b, c, use_3d: bool = False) -> Optional[float]:
    if not (a and b and c):
        return None
    if use_3d and 'z' in a and 'z' in b and 'z' in c:
        ax, ay, az = a['x'] - b['x'], a['y'] - b['y'], a['z'] - b['z']
        cx, cy, cz = c['x'] - b['x'], c['y'] - b['y'], c['z'] - b['z']
        dot = ax * cx + ay * cy + az * cz
        mag_a = math.sqrt(ax**2 + ay**2 + az**2)
        mag_c = math.sqrt(cx**2 + cy**2 + cz**2)
    else:
        ax, ay = a['x'] - b['x'], a['y'] - b['y']
        cx, cy = c['x'] - b['x'], c['y'] - b['y']
        dot = ax * cx + ay * cy
        mag_a = math.sqrt(ax**2 + ay**2)
        mag_c = math.sqrt(cx**2 + cy**2)
    mag = mag_a * mag_c
    if mag < 1e-6:
        return None
    cos_val = max(-1.0, min(1.0, dot / mag))
    return round(math.degrees(math.acos(cos_val)), 1)
```

（代码格式：示例放入 Word 文档时应置入文本框，字体比正文小两号，使用等宽字体。）

2.2.2 模板匹配：加权 RMSE
为衡量学员角度 S 与模板角度 T 的相似度，采用加权均方根误差：

$$
\mathrm{RMSE}_w(S,T)=\sqrt{\dfrac{\sum_{i\in I} w_i\,(S_i-T_i)^2}{\sum_{i\in I} w_i}}
$$

其中 I 为 S 与 T 的公共角度索引集合，w_i 为角度 i 的重要性权重。

2.2.3 非线性评分模型（从偏差到 0–100 分）
对每个问题角度 i 计算相对阈值归一化偏差 r_i = |S_i-T_i|/τ_i，采用平方惩罚并按权重累加：

$$
\mathrm{penalty} = \sum_{i} w_i\cdot \min(r_i^2,\,C)
$$

取 C=4，上界防止单角度主导，最终得分按线性映射到 0–100。

3 系统实现细节（代码选择性列示并说明）

3.1 关键点检测（MediaPipe 实现要点）
实现文件：src/tennis_coach/mediapipe_keypoint.py。该模块完成模型文件自动下载、base64 图片解码、调用 MediaPipe Tasks API，并将 33 点映射为系统使用的命名空间，额外合成 neck 与 pelvis 点以便角度定义一致。

3.2 角度抽取与问题诊断
实现文件：src/tennis_coach/analyzer.py 中的 extract_angles()、compare_to_template() 与 evaluate()。核心对比逻辑示例：

```
def compare_to_template(student_angles: dict, template_angles: dict, action: str) -> list:
    thresholds = ANGLE_THRESHOLDS.get(action, {})
    issues = []
    for angle_name, std_val in template_angles.items():
        if angle_name not in student_angles:
            continue
        student_val = student_angles[angle_name]
        threshold = thresholds.get(angle_name, 25)
        diff = student_val - std_val
        if abs(diff) > threshold:
            direction = "偏大" if diff > 0 else "偏小"
            advice = ANGLE_ADVICE.get(angle_name, {}).get(direction, "请参考标准动作调整。")
            issues.append({...})
    issues.sort(key=lambda i: i['权重'] * abs(i['偏差']), reverse=True)
    return issues
```

（代码说明：按动作阶段使用不同阈值集合 ANGLE_THRESHOLDS 控制敏感度；问题按权重×偏差排序。）

3.3 数据定义与模板
数据定义见 src/tennis_coach/data.py，其中包含 ANGLE_DEFS、ANGLE_THRESHOLDS、ANGLE_WEIGHTS 与 ANGLE_ADVICE。建议在论文附表中列出表格并使用小两号字体作为表注。

4 实验设计与结果验证

4.1 数据与测试文件
- 模板与样本：data/tennis_templates.json 与 data/tennis_samples/。
- 测试脚本：test_video_analysis.py、test_video_training.py、test_batch_training.py、test_3d_angles.py。

4.2 实验流程
- 静态图像评估：对标准动作图片与学员图片运行 evaluate() 并记录评分。
- 视频逐帧评估：使用 video_analyzer 逐帧提取角度序列并做滑动窗口匹配。
- 量化验证：计算与人工评分的相关性并评估鲁棒性。

4.3 实验结论
- MediaPipe 在清晰单人拍摄条件下稳定；角度计算重复性好。
- 加权 RMSE 能有效匹配动作阶段；非线性评分在偏差大时更具惩罚性。
- 对握拍和节奏等语义问题需结合视觉局部特征或语言模型补充。

5 结论与展望

5.1 结论
本课题实现了一个基于关键点角度的网球动作分析原型，支持检测、评分、问题诊断与历史追踪，满足业余训练的量化反馈需求。

5.2 展望
- 引入拍面/握拍检测与 LLM 增强建议。
- 引入 3D 姿态或多摄融合。
- 移动端/边缘部署以提升实时性。

6 致谢与收获
（按学校模板补充导师与同学致谢）

7 参考文献
- Google MediaPipe. https://mediapipe.dev/
- OpenCV. https://opencv.org/
- 项目源码文件（仓库内）：src/tennis_coach/analyzer.py、src/tennis_coach/mediapipe_keypoint.py、src/tennis_coach/data.py

附录：图注与表注说明
- 图注：置于图下方，含编号与简短说明，字体比正文小两号（示例：图 1：系统总体技术路线图）。
- 表注：置于表下方，含编号与说明，字体比正文小两号（示例：表 1：角度定义与权重）。

（当生成 Word 文档时，代码块会以等宽小号字体单独段落输出，图与表占位处会插入说明并保留图注空位，后续可替换为实际图片或表格。）
