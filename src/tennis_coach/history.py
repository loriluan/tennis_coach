# -*- coding: utf-8 -*-
import json
from datetime import datetime
from pathlib import Path

_HISTORY_FILE = Path(__file__).resolve().parents[2] / 'data' / 'history.json'


def _load() -> list:
    if not _HISTORY_FILE.exists():
        return []
    try:
        return json.loads(_HISTORY_FILE.read_text(encoding='utf-8'))
    except Exception:
        return []


def _save(records: list):
    _HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _HISTORY_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')


def save_record(player: str, action: str, score: int, angles: dict,
                issues: list, confidence: float):
    """保存一次评估记录。"""
    records = _load()
    records.append({
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'player': player.strip() or '默认学员',
        'action': action,
        'score': score,
        'confidence': confidence,
        'angles': angles,
        'issue_count': len(issues),
        'issues': [{'name': i['角度名称'], 'direction': i['方向'],
                    'std': i['标准值'], 'actual': i['实际值'], 'diff': i['偏差']}
                   for i in issues],
    })
    _save(records)


def get_records(player: str = '') -> list:
    """返回所有记录，可按学员名过滤。"""
    records = _load()
    if player.strip():
        records = [r for r in records if r.get('player') == player.strip()]
    return sorted(records, key=lambda r: r['time'])


def list_players() -> list:
    """返回所有出现过的学员名列表。"""
    records = _load()
    seen, players = set(), []
    for r in records:
        name = r.get('player', '默认学员')
        if name not in seen:
            seen.add(name)
            players.append(name)
    return players


def clear_records(player: str = ''):
    """清空记录，可按学员名清空。"""
    if not player.strip():
        _save([])
    else:
        records = [r for r in _load() if r.get('player') != player.strip()]
        _save(records)
