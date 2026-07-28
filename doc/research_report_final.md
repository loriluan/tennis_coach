研究报告

课题名称：基于计算机视觉的网球动作分析系统

摘要：
目前网球爱好者在训练过程中，由于缺乏专业教练的长期陪同，动作不规范的问题难以被及时发现和纠正，自我提升效率极低。本课题基于计算机视觉技术，通过分析运动员动作照片，自动识别人体关键点并计算关节角度，与预先建立的标准动作模板进行对比，对学员动作进行量化评分，并生成个性化改进建议。本课题还探究了将多模态大语言模型引入动作分析系统，对握拍方式等难以用角度量化的技术细节进行语义层面的补充分析，从而帮助网球爱好者在没有教练陪同的情况下，也能随时获得客观、量化的动作反馈。

关键词：计算机视觉；姿态估计；网球；Python；MediaPipe

1、引言

1.1 课题的来源与背景
我从初中开始练习网球，在没有教练陪同时，经常不知道自己的动作哪里出了问题。有时候明明感觉挥拍很顺手，但击球总是不稳定；想对着镜子自我检查，又看不出哪个关节角度有偏差。类似的困惑在身边同样打网球的朋友中十分普遍：大家往往要等到下一次上课时才能请教练帮忙纠正，而这时错误动作早已在肌肉记忆中被重复了几百次。

从整个网球教育领域来看，专业教练资源稀缺、费用高昂，大量网球爱好者难以获得持续的专业指导。传统的视频回放方式虽然可以事后复盘，但只能依赖主观判断，缺乏客观的量化指标。近年来，随着计算机视觉和人工智能技术的快速发展，人体姿态估计已经在多个运动项目中得到了应用探索，但专门面向网球动作分析的系统仍较为少见，且大多停留在学术研究层面，普通爱好者难以便捷使用。

1.2 课题研究的目的与意义
该网球动作分析系统利用人体关键点检测、关节角度计算等计算机视觉技术，以及多模态大语言模型，实现的主要功能包括：自动识别人体 17 个关键点、计算 7 个核心关节角度、与标准模板对比后生成 0–100 分的量化评分，以及输出针对每个关节的改进建议。

对于使用者，可以随时上传训练照片，不依赖教练即可获得客观的动作反馈，问题关节一目了然，改进建议清晰具体。对于教练，可以将标准动作照片录入系统建立模板库，节省重复讲解的时间，也能通过历史记录直观追踪自己的进步曲线。

1.3 查新情况
通过在知网中下载并阅读文献，笔者将其与本课题进行了分析、对比，发现本课题的优势在于：

1）同时支持百度人体分析云端 API 与 MediaPipe 本地离线模型两种检测方案，可在无网络环境下正常使用，实用性更强；

2）将几何量化分析（关节角度偏差）与多模态大语言模型的语义理解相结合，能够对握拍方式、击球点等难以量化的技术细节给出自然语言建议；

3）无需手动标注动作类型，系统通过 RMSE 最小化策略自动匹配最接近的动作阶段，使用门槛低。

在检索中未见与本课题完全相同的报道，表明目前还没有相似的课题，因而本课题的研究具有一定的价值和意义。

2、技术原理和总体思路

本课题的主要功能包括：1.人体关键点自动检测与可视化；2.关节角度计算与标准模板对比评分；3.个性化改进建议生成；4.学员训练历史记录与进度追踪。

课题采用人体姿态估计技术，实现人体 17 个关键点的自动识别功能；用向量点积法，实现 7 个核心关节角度的精确计算功能；用 RMSE 相似度匹配，实现动作阶段自动识别功能；用多模态大语言模型，实现握拍方式等语义细节的分析功能。

2.1 人体姿态估计
本系统主要采用两种人体关键点检测方案：百度人体分析云端 API 和 MediaPipe Pose 本地离线模型。后者在本项目中的实现见 `src/tennis_coach/mediapipe_keypoint.py`，该模块完成模型自动下载、base64 图片解码、MediaPipe 关键点检测及坐标映射。在检测结果中，系统把 MediaPipe 的 33 个关键点映射为 17 个核心关键点，并通过两肩与两髋内点生成 `neck` 和 `pelvis`，用于后续角度计算。

2.2 角度计算与动作判定模型
对于三点 $a,b,c$，以 $b$ 为顶点的关节角度采用向量点积公式：

$$
\theta = \arccos\left(\frac{u\cdot v}{\left|u\right| \left|v\right|}\right)
$$

其中 $u=a-b$，$v=c-b$。符号说明：$a,b,c$ 为关键点坐标；$u\cdot v$ 表示向量点积；$\left|u\right|$ 和 $\left|v\right|$ 为向量模长。该公式在项目中的实现见 `src/tennis_coach/analyzer.py` 中 `calc_angle()` 函数。

代码段 1：关节角度计算核心实现
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
该代码首先判断关键点是否齐全，再分别使用二维或三维坐标计算向量点积与模长，并通过 $\arccos$ 求取夹角，最终返回以度为单位的关节角度。

2.3 动作阶段自动识别与评分模型
系统对每张图片计算出的角度向量 $S=[S_i]$ 与标准模板角度 $T=[T_i]$ 进行加权 RMSE 匹配：

$$
\mathrm{RMSE}_w(S,T)=\sqrt{\frac{\sum_{i\in I} w_i (S_i-T_i)^2}{\sum_{i\in I} w_i}}
$$

其中 $I$ 为学员角度与模板角度的公共集合，$w_i$ 为角度 $i$ 的重要性权重。该公式用于在所有模板中选择最小 RMSE 的动作阶段，从而实现无需手动标注动作类型的自动阶段识别。

评分上，系统对每个问题角度计算相对偏差 $r_i=|S_i-T_i|/\tau_i$，并按权重进行平方惩罚：

$$
\mathrm{penalty}=\sum_i w_i \cdot \min(r_i^2, 4)
$$

最终得分映射为：

$$
\mathrm{Score}=\max\left(0,\;100\left(1-\frac{\mathrm{penalty}}{4\sum_i w_i}\right)\right)
$$

其中 $\tau_i$ 为该动作阶段下角度 $i$ 的容差阈值。该设计使得偏差较大的角度扣分更多，同时保留角度权重对整体评分的影响。

代码段 2：模板对比与问题列表生成
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
            issues.append({
                "角度名称": angle_name,
                "标准值": std_val,
                "实际值": student_val,
                "偏差": round(diff, 1),
                "方向": direction,
                "建议": advice,
                "权重": ANGLE_WEIGHTS.get(angle_name, 1.0),
            })
    issues.sort(key=lambda i: i['权重'] * abs(i['偏差']), reverse=True)
    return issues
```
该函数根据当前动作阶段的阈值判断哪些角度偏差超过标准，并按权重与偏差大小排序，最终形成问题列表和建议输出。

表1：关键角度定义与重要性权重
| 角度名称 | 对应关键点 | 权重 |
| --- | --- | --- |
| 右肘角 | right_shoulder, right_elbow, right_wrist | 2.0 |
| 左肘角 | left_shoulder, left_elbow, left_wrist | 2.0 |
| 右肩角 | right_hip, right_shoulder, right_elbow | 2.5 |
| 左肩角 | left_hip, left_shoulder, left_elbow | 2.5 |
| 右膝角 | right_hip, right_knee, right_ankle | 1.0 |
| 左膝角 | left_hip, left_knee, left_ankle | 1.0 |
| 躯干倾角 | neck, pelvis, right_hip | 1.5 |

表1：系统使用的关键角度定义与权重。

2.4 系统总体思路
系统总体技术路线图见图1。系统先通过两种关键点检测引擎获取人体关键点坐标，接着计算角度向量，按 RMSE 与模板库匹配动作阶段，最后输出评分、问题列表与自然语言建议。若云端不可用则自动切换到本地 MediaPipe；若本地图像质量不佳则补充百度云端检测结果。

图1：系统总体技术路线图。

3、系统实现

3.1 功能模块
本系统由关键点检测模块、角度计算与评分模块、模板管理模块、建议生成模块和历史记录模块组成。关键点检测模块支持 `src/tennis_coach/mediapipe_keypoint.py` 中的 MediaPipe 实现和 `src/tennis_coach/keypoint.py` 中的百度 API 适配。

3.2 代码实现概述
关键点检测模块先将输入图片解码为 RGB 图像，然后调用 MediaPipe PoseLandmarker 进行人体姿态分析，输出像素坐标与相对深度。角度计算模块在 `src/tennis_coach/analyzer.py` 中实现，每个角度的定义与阈值集中于 `src/tennis_coach/data.py`，便于后续调整。

3.3 提问与回答处模型设计
本项目采用几何模型与权重模板相结合的方式进行动作判定。通过公式 $\theta=\arccos\left(\frac{u\cdot v}{\left|u\right|\left|v\right|}\right)$ 得到角度，再用加权 RMSE 匹配动作阶段，最后用基于相对阈值平方惩罚的评分函数生成整体得分。该模型既保留物理量化原则，又兼顾不同关节对网球动作的重要性差异。

3.4 语义补充建议
对于握拍方式、击球点、重心转移等难以用角度直接量化的细节，系统预留了多模态大语言模型接口。该接口可根据关键点分布、动作阶段与图像局部特征生成自然语言建议，实现几何量化分析与语义理解的融合。

4、实验验证

4.1 实验设计
实验采集真实网球动作照片，分别使用百度人体分析 API 与 MediaPipe 本地模型进行检测。对比两种方案在不同光照、角度与背景下的关键点识别结果，并分析评分结果与经验教练判断的一致性。

4.2 主要实验结果
在清晰单人拍摄条件下，MediaPipe 本地模型的关键点检测稳定性较高；在弱光、复杂背景下，百度云端 API 的关键点补全能力更强。通过标准模板匹配，系统能自动识别正手、反手、发球等动作阶段，并给出有针对性的关节改进建议。

4.3 性能验证
测试脚本包括 `test_video_analysis.py`、`test_video_training.py`、`test_batch_training.py` 和 `test_3d_angles.py`，用于验证角度计算、模板匹配和批量分析流程，保证系统各模块在代码层面运行稳定。

5、结论

本课题实现了基于计算机视觉的网球动作分析系统，完成从关键点检测、角度计算到模板比对与量化评分的端到端流程，并支持多模态大语言模型的语义建议扩展。该系统能为业余网球爱好者提供客观的技术反馈，降低专业指导门槛，提高训练效率。

6、参考文献
[1] Google MediaPipe. https://mediapipe.dev/
[2] OpenCV. https://opencv.org/
[3] 项目源码文件：src/tennis_coach/analyzer.py、src/tennis_coach/mediapipe_keypoint.py、src/tennis_coach/data.py
