# -*- coding: utf-8 -*-
import base64
import json
import os
import sys
from pathlib import Path


def _get_access_token():
    from pathlib import Path
    import os
    root = Path(__file__).resolve().parents[2]
    env_path = root / '.env'
    api_key = secret_key = None
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith('BAIDU_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
            elif line.startswith('BAIDU_SECRET_KEY='):
                secret_key = line.split('=', 1)[1].strip()
    api_key = api_key or os.environ.get('BAIDU_API_KEY')
    secret_key = secret_key or os.environ.get('BAIDU_SECRET_KEY')
    if not api_key or not secret_key:
        raise RuntimeError('BAIDU_API_KEY 或 BAIDU_SECRET_KEY 未配置')
    
    # 使用缓存token
    from .utils import get_cached_baidu_token
    return get_cached_baidu_token(api_key, secret_key)


def detect_keypoints(image_b64: str) -> dict:
    """调用百度人体关键点 API，返回原始响应。"""
    import requests
    token = _get_access_token()
    url = f'https://aip.baidubce.com/rest/2.0/image-classify/v1/body_analysis?access_token={token}'
    resp = requests.post(
        url,
        data={'image': image_b64},
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30,
    )
    return resp.json()


def parse_keypoints(api_response: dict) -> list[dict]:
    """从百度返回值中提取关键点列表，每项格式：{part: str, x: float, y: float, score: float}"""
    persons = api_response.get('person_info', [])
    result = []
    for person in persons:
        parts = {}
        for part_name, info in person.get('body_parts', {}).items():
            parts[part_name] = {
                'x': info.get('x', 0),
                'y': info.get('y', 0),
                'score': info.get('score', 0),
            }
        result.append(parts)
    return result
