# -*- coding: utf-8 -*-
import json
from pathlib import Path

TEMPLATES_FILE = Path(__file__).resolve().parents[2] / 'data' / 'tennis_templates.json'


def load_templates() -> dict:
    if TEMPLATES_FILE.exists():
        return json.loads(TEMPLATES_FILE.read_text(encoding='utf-8'))
    return {}


def save_template(action: str, angles: dict, sample_count: int):
    """保存或更新某动作的标准模板（多次训练取均值）。"""
    TEMPLATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    templates = load_templates()

    if action in templates:
        existing = templates[action]
        n = existing.get('sample_count', 1)
        merged = {}
        for k in set(list(existing['angles'].keys()) + list(angles.keys())):
            old = existing['angles'].get(k, angles.get(k, 0))
            new = angles.get(k, old)
            merged[k] = round((old * n + new) / (n + 1), 1)
        templates[action] = {'angles': merged, 'sample_count': n + 1}
    else:
        templates[action] = {'angles': angles, 'sample_count': sample_count}

    TEMPLATES_FILE.write_text(
        json.dumps(templates, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    return templates[action]


def delete_template(action: str):
    templates = load_templates()
    templates.pop(action, None)
    TEMPLATES_FILE.write_text(
        json.dumps(templates, ensure_ascii=False, indent=2), encoding='utf-8'
    )
