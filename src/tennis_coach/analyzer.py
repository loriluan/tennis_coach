# -*- coding: utf-8 -*-
import math
from .data import ANGLE_DEFS, ANGLE_THRESHOLDS, ANGLE_ADVICE


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
            })
    return issues


def evaluate(student_parts: dict, template: dict, action: str) -> dict:
    """完整评估流程，返回报告字典。"""
    student_angles = extract_angles(student_parts)
    template_angles = template.get('angles', {})
    issues = compare_to_template(student_angles, template_angles, action)

    total = len(template_angles)
    problem_count = len(issues)
    score = max(0, round((1 - problem_count / max(total, 1)) * 100))

    return {
        "动作": action,
        "得分": score,
        "学员角度": student_angles,
        "标准角度": template_angles,
        "问题列表": issues,
        "总结": f"共检测 {total} 个角度，{problem_count} 个需改进。" if problem_count
                else "动作规范，各关节角度均在标准范围内！",
    }
