# -*- coding: utf-8 -*-
"""工具函数：Token缓存、文件校验等。"""
import hashlib
import json
import os
import time
from pathlib import Path
from threading import Lock

# 百度API Token缓存
_token_cache = {'token': None, 'expires_at': 0}
_token_lock = Lock()

# 模板文件内存缓存
_templates_cache = {'data': None, 'mtime': 0, 'path': None}
_templates_lock = Lock()


def get_cached_baidu_token(api_key: str, secret_key: str) -> str:
    """获取百度API access_token（带缓存和自动刷新）。"""
    global _token_cache
    
    with _token_lock:
        # 检查缓存是否有效（提前5分钟过期）
        if (_token_cache['token'] and 
            time.time() < _token_cache['expires_at'] - 300):
            return _token_cache['token']
        
        # 重新获取token
        import requests
        resp = requests.get(
            'https://aip.baidubce.com/oauth/2.0/token',
            params={'grant_type': 'client_credentials',
                    'client_id': api_key, 
                    'client_secret': secret_key},
            timeout=10,
        )
        data = resp.json()
        token = data.get('access_token')
        expires_in = data.get('expires_in', 2592000)  # 默认30天
        
        if token:
            _token_cache['token'] = token
            _token_cache['expires_at'] = time.time() + expires_in
            return token
        
        raise RuntimeError(f"获取token失败: {data}")


def get_cached_templates(templates_path: Path) -> dict:
    """获取模板数据（带内存缓存，文件变化时自动重载）。"""
    global _templates_cache
    
    with _templates_lock:
        # 检查文件是否变化
        if templates_path.exists():
            mtime = templates_path.stat().st_mtime
            if (_templates_cache['data'] is not None and
                _templates_cache['path'] == templates_path and
                _templates_cache['mtime'] == mtime):
                return _templates_cache['data']
        
        # 重新加载
        if templates_path.exists():
            data = json.loads(templates_path.read_text(encoding='utf-8'))
        else:
            data = {}
        
        _templates_cache['data'] = data
        _templates_cache['path'] = templates_path
        _templates_cache['mtime'] = templates_path.stat().st_mtime if templates_path.exists() else 0
        return data


def save_templates(templates_path: Path, data: dict):
    """保存模板数据并更新缓存。"""
    global _templates_cache
    
    templates_path.parent.mkdir(parents=True, exist_ok=True)
    templates_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), 
        encoding='utf-8'
    )
    
    # 更新缓存
    with _templates_lock:
        _templates_cache['data'] = data
        _templates_cache['path'] = templates_path
        _templates_cache['mtime'] = templates_path.stat().st_mtime


def verify_file_integrity(file_path: Path, expected_md5: str = None) -> bool:
    """验证文件完整性（MD5校验）。"""
    if not file_path.exists():
        return False
    
    if expected_md5:
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest() == expected_md5
    
    return True


def download_file_with_verify(url: str, dest_path: Path, 
                              expected_md5: str = None, 
                              chunk_size: int = 8192) -> bool:
    """下载文件并验证完整性，失败时重试。"""
    import urllib.request
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 如果文件已存在且完整，跳过下载
    if dest_path.exists() and verify_file_integrity(dest_path, expected_md5):
        return True
    
    # 下载文件
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"[Utils] 下载文件 (尝试 {attempt + 1}/{max_retries}): {url}")
            urllib.request.urlretrieve(url, dest_path)
            
            # 验证完整性
            if verify_file_integrity(dest_path, expected_md5):
                print(f"[Utils] 下载完成: {dest_path}")
                return True
            else:
                print(f"[Utils] 文件校验失败，删除重试...")
                dest_path.unlink(missing_ok=True)
        except Exception as e:
            print(f"[Utils] 下载失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                raise
    
    return False