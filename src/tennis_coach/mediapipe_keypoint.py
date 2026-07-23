# -*- coding: utf-8 -*-
"""
MediaPipe Pose 关键点提取（Tasks API，兼容 0.10+）。
把 MediaPipe 33 点映射到与百度 API 相同的字段名。
"""
import base64

_MP_TO_BAIDU = {
    0:  'top_head',
    7:  'left_ear',
    8:  'right_ear',
    11: 'left_shoulder',
    12: 'right_shoulder',
    13: 'left_elbow',
    14: 'right_elbow',
    15: 'left_wrist',
    16: 'right_wrist',
    23: 'left_hip',
    24: 'right_hip',
    25: 'left_knee',
    26: 'right_knee',
    27: 'left_ankle',
    28: 'right_ankle',
}


def detect_keypoints_mediapipe(image_b64: str) -> dict:
    try:
        import numpy as np
        import cv2
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions
        from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
    except ImportError as e:
        raise ImportError(f'MediaPipe 未安装或不可用: {e}')
    
    import urllib.request
    from pathlib import Path

    # 首次运行自动下载模型（带完整性校验）
    model_path = Path(__file__).resolve().parents[2] / 'data' / 'pose_landmarker_heavy.task'
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    url = ('https://storage.googleapis.com/mediapipe-models/pose_landmarker/'
           'pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task')
    
    # 使用带校验的下载函数
    from .utils import download_file_with_verify
    if not model_path.exists():
        print(f'[MediaPipe] 首次运行，下载模型...')
    
    # MediaPipe heavy模型约30MB，验证文件大小（至少20MB）
    if not model_path.exists() or model_path.stat().st_size < 20 * 1024 * 1024:
        download_file_with_verify(url, model_path)
        print('[MediaPipe] 模型下载完成')

    # base64 → numpy
    img_bytes = base64.b64decode(image_b64)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise ValueError('无法解码图片')
    h, w = img_bgr.shape[:2]
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(model_path)),
        running_mode=RunningMode.IMAGE,
        num_poses=1,
    )
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    with PoseLandmarker.create_from_options(options) as landmarker:
        result = landmarker.detect(mp_image)

    if not result.pose_landmarks:
        return {}

    lm = result.pose_landmarks[0]
    parts = {}

    for idx, name in _MP_TO_BAIDU.items():
        p = lm[idx]
        vis = getattr(p, 'visibility', 1.0) or 1.0
        parts[name] = {
            'x': round(p.x * w, 1),
            'y': round(p.y * h, 1),
            'z': round(p.z, 3),  # MediaPipe提供相对深度（z坐标）
            'score': round(vis, 3),
        }

    # 模拟 neck（两肩中点）
    if 'left_shoulder' in parts and 'right_shoulder' in parts:
        ls, rs = parts['left_shoulder'], parts['right_shoulder']
        parts['neck'] = {
            'x': round((ls['x'] + rs['x']) / 2, 1),
            'y': round((ls['y'] + rs['y']) / 2, 1),
            'z': round((ls.get('z', 0) + rs.get('z', 0)) / 2, 3),
            'score': round((ls['score'] + rs['score']) / 2, 3),
        }

    # 模拟 pelvis（两髋中点）
    if 'left_hip' in parts and 'right_hip' in parts:
        lh, rh = parts['left_hip'], parts['right_hip']
        parts['pelvis'] = {
            'x': round((lh['x'] + rh['x']) / 2, 1),
            'y': round((lh['y'] + rh['y']) / 2, 1),
            'z': round((lh.get('z', 0) + rh.get('z', 0)) / 2, 3),
            'score': round((lh['score'] + rh['score']) / 2, 3),
        }

    return parts
