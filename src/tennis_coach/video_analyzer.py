# -*- coding: utf-8 -*-
"""
视频分析模块：提取视频帧，逐帧分析动作，生成时序报告。
"""
import base64
import json
import os
import tempfile
from pathlib import Path
from typing import List, Dict

import cv2
import numpy as np


def extract_frames(video_path: str, 
                   max_frames: int = 30,
                   min_interval: float = 0.5) -> List[Dict]:
    """从视频中提取关键帧。
    
    Args:
        video_path: 视频文件路径
        max_frames: 最大提取帧数
        min_interval: 最小帧间隔（秒）
    
    Returns:
        帧列表，每帧包含：{'frame_idx': int, 'timestamp': float, 'image_b64': str}
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f'无法打开视频: {video_path}')
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    # 计算采样间隔
    if duration > 0:
        interval_frames = max(int(fps * min_interval), 1)
        max_frames = min(max_frames, total_frames // interval_frames)
    else:
        interval_frames = max(1, total_frames // max_frames)
    
    frames = []
    frame_idx = 0
    
    while len(frames) < max_frames and frame_idx < total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break
        
        # 转换为base64
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        timestamp = frame_idx / fps if fps > 0 else 0
        
        frames.append({
            'frame_idx': frame_idx,
            'timestamp': round(timestamp, 2),
            'image_b64': image_b64,
        })
        
        frame_idx += interval_frames
    
    cap.release()
    return frames


def analyze_video_frames(frames: List[Dict],
                         provider: str = 'mediapipe',
                         templates: Dict = None,
                         action_types: List[str] = None,
                         match_threshold: float = 50.0) -> Dict:
    """分析视频中的每一帧。
    
    Args:
        frames: 帧列表（来自extract_frames）
        provider: 关键点检测provider ('baidu' 或 'mediapipe')
        templates: 标准模板字典
        action_types: 用户指定的动作类型列表（可选），如果提供则只匹配这些类型
        match_threshold: 匹配阈值（置信度分数），低于此值的帧不认为是有效匹配
    
    Returns:
        分析报告，包含每帧的详细结果
    """
    from tennis_coach.analyzer import extract_angles, evaluate, weighted_rmse
    from tennis_coach.keypoint import detect_keypoints, parse_keypoints
    from tennis_coach.mediapipe_keypoint import detect_keypoints_mediapipe
    
    # 确保 action_types 是列表
    if action_types is None:
        action_types = []
    
    results = {
        'total_frames': len(frames),
        'analyzed_frames': 0,
        'failed_frames': 0,
        'frames': [],
        'summary': {
            'actions_detected': {},
            'average_score': 0,
            'common_issues': {},
            'best_frame': None,
            'worst_frame': None,
        }
    }
    
    scores = []
    action_counts = {}
    issues_count = {}
    
    for i, frame in enumerate(frames):
        frame_result = {
            'frame_idx': frame['frame_idx'],
            'timestamp': frame['timestamp'],
            'success': False,
            'action': None,
            'score': None,
            'angles': None,
            'issues': None,
            'error': None,
        }
        
        try:
            # 检测关键点
            if provider == 'mediapipe':
                parts = detect_keypoints_mediapipe(frame['image_b64'])
                if not parts:
                    frame_result['error'] = '未检测到人体'
                    results['failed_frames'] += 1
                    results['frames'].append(frame_result)
                    continue
            else:
                raw = detect_keypoints(frame['image_b64'])
                if 'error_code' in raw:
                    frame_result['error'] = f"百度API错误: {raw.get('error_msg')}"
                    results['failed_frames'] += 1
                    results['frames'].append(frame_result)
                    continue
                persons = parse_keypoints(raw)
                if not persons:
                    frame_result['error'] = '未检测到人体'
                    results['failed_frames'] += 1
                    results['frames'].append(frame_result)
                    continue
                parts = persons[0]
            
            # 计算角度
            use_3d = (provider == 'mediapipe')
            student_angles = extract_angles(parts, use_3d=use_3d)
            
            # 匹配模板
            if templates:
                # 如果用户指定了动作类型列表，只匹配这些类型
                if action_types and len(action_types) > 0:
                    # 在选定的动作类型中找最佳匹配
                    best_action, best_score = None, float('inf')
                    for action_name in action_types:
                        if action_name in templates:
                            score = weighted_rmse(student_angles, templates[action_name]['angles'])
                            if score < best_score:
                                best_score = score
                                best_action = action_name
                else:
                    # 未指定动作类型，自动匹配所有模板
                    best_action, best_score = _find_best_match(student_angles, templates)
                
                # 只有匹配分数足够好（置信度 >= match_threshold）才认为是有效匹配
                # best_score 是 RMSE，越小越好；转换为置信度：100 - best_score
                confidence = max(0, 100 - best_score)
                
                if best_action and confidence >= match_threshold:
                    report = evaluate(parts, templates[best_action], best_action, use_3d=use_3d)
                    
                    frame_result['success'] = True
                    frame_result['action'] = best_action
                    frame_result['score'] = report['得分']
                    frame_result['angles'] = student_angles
                    frame_result['issues'] = report['问题列表']
                    
                    # 统计
                    scores.append(report['得分'])
                    action_counts[best_action] = action_counts.get(best_action, 0) + 1
                    
                    for issue in report['问题列表']:
                        issue_name = issue['角度名称']
                        issues_count[issue_name] = issues_count.get(issue_name, 0) + 1
                else:
                    # 匹配分数不够好，标记为无法识别
                    frame_result['error'] = f'匹配置信度不足 ({confidence:.1f}%)'
            else:
                # 无模板时只返回角度
                frame_result['success'] = True
                frame_result['angles'] = student_angles
            
            results['analyzed_frames'] += 1
            
        except Exception as e:
            frame_result['error'] = str(e)
            results['failed_frames'] += 1
        
        results['frames'].append(frame_result)
    
    # 生成总结
    if scores:
        results['summary']['average_score'] = round(sum(scores) / len(scores), 1)
        # 只从成功匹配的帧中找最佳/最差帧
        successful_frames = [f for f in results['frames'] if f['success']]
        if successful_frames:
            results['summary']['best_frame'] = max(successful_frames, 
                                                   key=lambda f: f.get('score') or 0)
            results['summary']['worst_frame'] = min(successful_frames, 
                                                   key=lambda f: f.get('score') or 100)
    
    results['summary']['actions_detected'] = action_counts
    results['summary']['common_issues'] = dict(sorted(issues_count.items(), 
                                                      key=lambda x: x[1], 
                                                      reverse=True)[:5])
    
    return results


def _find_best_match(student_angles: Dict, templates: Dict):
    """找到最匹配的模板。"""
    from tennis_coach.analyzer import weighted_rmse
    
    best_action, best_score = None, float('inf')
    for action, tmpl in templates.items():
        score = weighted_rmse(student_angles, tmpl['angles'])
        if score < best_score:
            best_score, best_action = score, action
    return best_action, best_score


def train_from_video(video_path: str,
                     action: str,
                     provider: str = 'mediapipe',
                     max_frames: int = 30,
                     min_interval: float = 0.5,
                     strategy: str = 'all') -> Dict:
    """从视频训练标准模板。
    
    Args:
        video_path: 视频文件路径
        action: 动作名称
        provider: 关键点检测provider
        max_frames: 最大提取帧数
        min_interval: 最小帧间隔（秒）
        strategy: 模板生成策略
            - 'all': 使用所有成功帧的角度平均值（推荐，充分利用视频信息）
            - 'best': 选择得分最高的帧
            - 'average': 所有成功帧的角度平均值（同all）
            - 'first': 第一帧
    
    Returns:
        训练结果，包含模板信息
    """
    from tennis_coach.analyzer import extract_angles
    from tennis_coach.templates import save_template
    
    # 提取帧
    frames = extract_frames(video_path, max_frames=max_frames, 
                           min_interval=min_interval)
    
    if not frames:
        raise ValueError('无法从视频中提取帧')
    
    # 分析所有帧
    analysis = analyze_video_frames(frames, provider=provider, templates=None)
    
    # 筛选成功分析的帧
    successful_frames = [f for f in analysis['frames'] if f['success'] and f['angles']]
    
    if not successful_frames:
        raise ValueError('视频中未检测到有效的人体姿势')
    
    # 根据策略生成模板
    if strategy in ['all', 'average']:
        # 使用所有成功帧的角度平均值（充分利用视频信息）
        all_angles = [f['angles'] for f in successful_frames]
        template_angles = {}
        
        # 获取所有角度名称
        all_keys = set()
        for angles in all_angles:
            all_keys.update(angles.keys())
        
        # 计算平均值
        for key in all_keys:
            values = [angles.get(key) for angles in all_angles if key in angles]
            if values:
                template_angles[key] = round(sum(values) / len(values), 1)
        
        used_frame = successful_frames[0]
        strategy_desc = f"平均{len(successful_frames)}帧（充分利用视频信息）"
    
    elif strategy == 'best':
        # 选择得分最高的帧
        best_frame = max(successful_frames, key=lambda f: f.get('score') or 0)
        template_angles = best_frame['angles']
        used_frame = best_frame
        strategy_desc = f"选择最佳帧（得分{best_frame.get('score')}）"
    
    else:  # 'first'
        # 使用第一帧
        used_frame = successful_frames[0]
        template_angles = used_frame['angles']
        strategy_desc = "使用第一帧"
    
    # 保存模板
    template = save_template(action, template_angles, 1)
    
    return {
        'action': action,
        'angles': template_angles,
        'sample_count': template['sample_count'],
        'strategy': strategy_desc,
        'total_frames': len(frames),
        'analyzed_frames': analysis['analyzed_frames'],
        'failed_frames': analysis['failed_frames'],
        'used_frame_timestamp': used_frame['timestamp'],
        'used_frame_score': used_frame.get('score'),
        'provider': provider,
        'use_3d': (provider == 'mediapipe'),
        'successful_frames_count': len(successful_frames),
    }


def batch_train_from_video(video_path: str,
                           actions: List[str],
                           provider: str = 'mediapipe',
                           max_frames: int = 30,
                           min_interval: float = 0.5,
                           strategy: str = 'all') -> Dict:
    """从视频批量训练多个动作模板。
    
    Args:
        video_path: 视频文件路径
        actions: 动作名称列表，如 ['正手击球 - 准备', '正手击球 - 引拍', ...]
        provider: 关键点检测provider
        max_frames: 最大提取帧数
        min_interval: 最小帧间隔（秒）
        strategy: 模板生成策略
    
    Returns:
        批量训练结果
    """
    from tennis_coach.analyzer import extract_angles
    from tennis_coach.templates import save_template
    
    # 提取帧
    frames = extract_frames(video_path, max_frames=max_frames, 
                           min_interval=min_interval)
    
    if not frames:
        raise ValueError('无法从视频中提取帧')
    
    # 分析所有帧（不匹配模板，只计算角度）
    analysis = analyze_video_frames(frames, provider=provider, templates=None)
    
    # 筛选成功分析的帧
    successful_frames = [f for f in analysis['frames'] if f['success'] and f['angles']]
    
    if not successful_frames:
        raise ValueError('视频中未检测到有效的人体姿势')
    
    # 为每个动作训练模板
    results = []
    for action in actions:
        # 根据策略生成模板
        if strategy in ['all', 'average']:
            # 使用所有成功帧的角度平均值
            all_angles = [f['angles'] for f in successful_frames]
            template_angles = {}
            
            # 获取所有角度名称
            all_keys = set()
            for angles in all_angles:
                all_keys.update(angles.keys())
            
            # 计算平均值
            for key in all_keys:
                values = [angles.get(key) for angles in all_angles if key in angles]
                if values:
                    template_angles[key] = round(sum(values) / len(values), 1)
            
            used_frame = successful_frames[0]
            strategy_desc = f"平均{len(successful_frames)}帧"
        
        elif strategy == 'best':
            # 选择得分最高的帧
            best_frame = max(successful_frames, key=lambda f: f.get('score') or 0)
            template_angles = best_frame['angles']
            used_frame = best_frame
            strategy_desc = f"最佳帧（得分{best_frame.get('score')}）"
        
        else:  # 'first'
            used_frame = successful_frames[0]
            template_angles = used_frame['angles']
            strategy_desc = "第一帧"
        
        # 保存模板
        template = save_template(action, template_angles, 1)
        
        results.append({
            'action': action,
            'angles': template_angles,
            'sample_count': template['sample_count'],
            'strategy': strategy_desc,
            'used_frame_timestamp': used_frame['timestamp'],
            'used_frame_score': used_frame.get('score'),
        })
    
    return {
        'total_actions': len(actions),
        'successful_actions': len(results),
        'total_frames': len(frames),
        'analyzed_frames': analysis['analyzed_frames'],
        'failed_frames': analysis['failed_frames'],
        'provider': provider,
        'use_3d': (provider == 'mediapipe'),
        'results': results,
    }


def generate_video_report(video_analysis: Dict) -> str:
    """生成视频分析的文字报告。"""
    summary = video_analysis['summary']
    
    report = []
    report.append("=" * 60)
    report.append("视频动作分析报告")
    report.append("=" * 60)
    report.append(f"\n总帧数: {video_analysis['total_frames']}")
    report.append(f"成功分析: {video_analysis['analyzed_frames']}")
    report.append(f"分析失败: {video_analysis['failed_frames']}")
    report.append(f"平均得分: {summary['average_score']}")
    
    if summary['actions_detected']:
        report.append("\n检测到的动作:")
        for action, count in summary['actions_detected'].items():
            report.append(f"  - {action}: {count}次")
    
    if summary['common_issues']:
        report.append("\n最常见问题:")
        for issue, count in summary['common_issues'].items():
            report.append(f"  - {issue}: 出现{count}次")
    
    if summary['best_frame']:
        best = summary['best_frame']
        report.append(f"\n最佳动作帧:")
        report.append(f"  时间点: {best['timestamp']}秒")
        report.append(f"  得分: {best.get('score')}")
        report.append(f"  动作: {best.get('action')}")
    
    if summary['worst_frame'] and summary['worst_frame'].get('score') is not None:
        worst = summary['worst_frame']
        report.append(f"\n最需改进帧:")
        report.append(f"  时间点: {worst['timestamp']}秒")
        report.append(f"  得分: {worst.get('score')}")
        report.append(f"  动作: {worst.get('action')}")
        if worst.get('issues'):
            report.append("  问题:")
            for issue in worst['issues'][:3]:
                report.append(f"    - {issue['角度名称']}: {issue['方向']} {issue['偏差']}°")
    
    report.append("\n" + "=" * 60)
    
    return "\n".join(report)
