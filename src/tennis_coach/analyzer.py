# -*- coding: utf-8 -*-
import math
from .data import ANGLE_DEFS, ANGLE_THRESHOLDS, ANGLE_ADVICE, ANGLE_WEIGHTS


def calc_angle(a, b, c) -> float | None:
    """计算 a-b-c 三点以 b 为顶点的夹角（度）。"""
    if not (a and b and c):
        return None
    ax, ay = a['x'] - b['x'], a['y'] - b['y']
    cx, cy = c['x'] - b['x'], c['y'] - b['y']
    dot = ax * cx + ay * cy
    mag = math.sqrt(ax**2 + ay**2) * math.sqrt(cx**2 + cy**2)
    if mag < 1e-6:
        return None
    cos_val = max(-1.0, min(1.0, dot / mag))
    return round(math.degrees(math.acos(cos_val)), 1)


def extract_angles(parts: dict) -> dict:
    """从关键点字典计算所有定义的角度。"""
    angles = {}
    for angle_name, (a_key, b_key, c_key) in ANGLE_DEFS.items():
        a = parts.get(a_key)
        b = parts.get(b_key)
        c = parts.get(c_key)
        val = calc_angle(a, b, c)
        if val is not None:
            angles[angle_name] = val
    return angles


def weighted_rmse(student_angles: dict, template_angles: dict) -> float:
    """加权 RMSE：重要角度（肩、肘）权重更高，匹配更准确。"""
    shared = [k for k in student_angles if k in template_angles]
    if not shared:
        return float('inf')
    total_weight = sum(ANGLE_WEIGHTS.get(k, 1.0) for k in shared)
    weighted_sq = sum(
        ANGLE_WEIGHTS.get(k, 1.0) * (student_angles[k] - template_angles[k]) ** 2
        for k in shared
    )
    return math.sqrt(weighted_sq / total_weight)


def compare_to_template(student_angles: dict, template_angles: dict, action: str) -> list:
    """对比学员角度与标准模板，返回问题列表。"""
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
    # 按权重 × 偏差绝对值降序排列，最严重的问题排前面
    issues.sort(key=lambda i: i['权重'] * abs(i['偏差']), reverse=True)
    return issues


def _nonlinear_score(issues: list, template_angles: dict) -> int:
    """非线性评分：偏差越大扣分越多（平方惩罚），权重高的角度影响更大。"""
    if not template_angles:
        return 100
    total_weight = sum(ANGLE_WEIGHTS.get(k, 1.0) for k in template_angles)
    penalty = 0.0
    for iss in issues:
        w = iss['权重']
        threshold = next(
            (v for action_thresh in [{}]  # 只是占位，下面直接用偏差/阈值比
             for v in [25]), 25)
        # 用偏差相对阈值的倍数做平方惩罚
        ratio = abs(iss['偏差']) / max(iss.get('threshold', 25), 1)
        penalty += w * min(ratio ** 2, 4.0)  # 上限 4 倍，防止单角度压垮总分
    max_penalty = total_weight * 4.0
    score = max(0, round(100 * (1 - penalty / max_penalty)))
    return score


def evaluate(student_parts: dict, template: dict, action: str) -> dict:
    """完整评估流程，返回报告字典。"""
    student_angles = extract_angles(student_parts)
    template_angles = template.get('angles', {})
    issues = compare_to_template(student_angles, template_angles, action)

    # 补充 threshold 到 issue 供评分使用
    thresholds = ANGLE_THRESHOLDS.get(action, {})
    for iss in issues:
        iss['threshold'] = thresholds.get(iss['角度名称'], 25)

    score = _nonlinear_score(issues, template_angles)
    problem_count = len(issues)

    return {
        "动作": action,
        "得分": score,
        "学员角度": student_angles,
        "标准角度": template_angles,
        "问题列表": issues,
        "总结": f"共检测 {len(template_angles)} 个角度，{problem_count} 个需改进。" if problem_count
                else "动作规范，各关节角度均在标准范围内！",
    }
