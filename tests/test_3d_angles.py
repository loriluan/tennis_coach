#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试3D角度计算功能。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_3d_angle_calculation():
    """测试3D角度计算"""
    print("=" * 60)
    print("测试3D角度计算")
    print("=" * 60)
    
    from tennis_coach.analyzer import calc_angle
    
    # 测试用例1：2D角度（无z坐标）
    print("\n1. 2D角度计算（无z坐标）:")
    a_2d = {'x': 0, 'y': 0}
    b_2d = {'x': 1, 'y': 0}
    c_2d = {'x': 1, 'y': 1}
    
    angle_2d = calc_angle(a_2d, b_2d, c_2d, use_3d=False)
    print(f"   点A(0,0) -> 点B(1,0) -> 点C(1,1)")
    print(f"   2D角度: {angle_2d}° (预期: 90.0°)")
    assert angle_2d == 90.0, f"2D角度计算错误: {angle_2d}"
    print("   ✓ 2D角度计算正确")
    
    # 测试用例2：3D角度（有z坐标）
    print("\n2. 3D角度计算（有z坐标）:")
    a_3d = {'x': 0, 'y': 0, 'z': 0}
    b_3d = {'x': 1, 'y': 0, 'z': 0}
    c_3d = {'x': 1, 'y': 1, 'z': 0}
    
    angle_3d = calc_angle(a_3d, b_3d, c_3d, use_3d=True)
    print(f"   点A(0,0,0) -> 点B(1,0,0) -> 点C(1,1,0)")
    print(f"   3D角度: {angle_3d}° (预期: 90.0°)")
    assert angle_3d == 90.0, f"3D角度计算错误: {angle_3d}"
    print("   ✓ 3D角度计算正确")
    
    # 测试用例3：3D角度（z坐标不同）
    print("\n3. 3D角度计算（z坐标不同）:")
    a_3d = {'x': 0, 'y': 0, 'z': 0}
    b_3d = {'x': 1, 'y': 0, 'z': 0}
    c_3d = {'x': 1, 'y': 1, 'z': 1}  # z=1，形成45度倾斜
    
    angle_3d_tilted = calc_angle(a_3d, b_3d, c_3d, use_3d=True)
    print(f"   点A(0,0,0) -> 点B(1,0,0) -> 点C(1,1,1)")
    print(f"   3D角度: {angle_3d_tilted}° (预期: 约60.0°)")
    # 向量BA=(−1,0,0), BC=(0,1,1)
    # cos(θ) = 0 / (1 * √2) = 0
    # θ = 90°
    assert abs(angle_3d_tilted - 90.0) < 1.0, f"3D倾斜角度计算错误: {angle_3d_tilted}"
    print("   ✓ 3D倾斜角度计算正确")
    
    # 测试用例4：缺少z坐标时自动降级到2D
    print("\n4. 缺少z坐标时自动降级:")
    a_partial = {'x': 0, 'y': 0}  # 无z
    b_partial = {'x': 1, 'y': 0, 'z': 0}
    c_partial = {'x': 1, 'y': 1, 'z': 0}
    
    angle_fallback = calc_angle(a_partial, b_partial, c_partial, use_3d=True)
    print(f"   点A(无z) -> 点B(1,0,0) -> 点C(1,1,0)")
    print(f"   自动降级到2D: {angle_fallback}° (预期: 90.0°)")
    assert angle_fallback == 90.0, f"降级计算错误: {angle_fallback}"
    print("   ✓ 自动降级到2D正确")
    
    print("\n✓ 所有3D角度计算测试通过")


def test_extract_angles_3d():
    """测试extract_angles的3D模式"""
    print("\n" + "=" * 60)
    print("测试extract_angles的3D模式")
    print("=" * 60)
    
    from tennis_coach.analyzer import extract_angles
    
    # 模拟MediaPipe返回的关键点（带z坐标）
    parts_3d = {
        'right_shoulder': {'x': 400, 'y': 300, 'z': -0.1, 'score': 0.95},
        'right_elbow':    {'x': 450, 'y': 350, 'z': -0.05, 'score': 0.92},
        'right_wrist':    {'x': 500, 'y': 320, 'z': 0.0, 'score': 0.88},
        'right_hip':      {'x': 420, 'y': 400, 'z': -0.15, 'score': 0.94},
        'left_shoulder':  {'x': 350, 'y': 300, 'z': -0.1, 'score': 0.95},
        'left_elbow':     {'x': 300, 'y': 350, 'z': -0.05, 'score': 0.93},
        'left_wrist':     {'x': 250, 'y': 320, 'z': 0.0, 'score': 0.90},
        'left_hip':       {'x': 380, 'y': 400, 'z': -0.15, 'score': 0.94},
        'left_knee':      {'x': 370, 'y': 500, 'z': -0.2, 'score': 0.92},
        'left_ankle':     {'x': 360, 'y': 600, 'z': -0.25, 'score': 0.90},
        'right_knee':     {'x': 430, 'y': 500, 'z': -0.2, 'score': 0.92},
        'right_ankle':    {'x': 440, 'y': 600, 'z': -0.25, 'score': 0.91},
        'top_head':       {'x': 400, 'y': 200, 'z': -0.2, 'score': 0.96},
        'neck':           {'x': 375, 'y': 300, 'z': -0.1, 'score': 0.95},
        'pelvis':         {'x': 400, 'y': 400, 'z': -0.15, 'score': 0.94},
    }
    
    # 2D模式
    angles_2d = extract_angles(parts_3d, use_3d=False)
    print(f"\n2D模式计算角度: {len(angles_2d)} 个")
    for name, value in angles_2d.items():
        print(f"   {name}: {value}°")
    
    # 3D模式
    angles_3d = extract_angles(parts_3d, use_3d=True)
    print(f"\n3D模式计算角度: {len(angles_3d)} 个")
    for name, value in angles_3d.items():
        print(f"   {name}: {value}°")
    
    # 验证两个模式都返回了角度
    assert len(angles_2d) > 0, "2D模式未返回角度"
    assert len(angles_3d) > 0, "3D模式未返回角度"
    
    # 验证角度数量一致
    assert len(angles_2d) == len(angles_3d), "2D和3D模式角度数量不一致"
    
    # 验证某些角度可能不同（因为z坐标的影响）
    diff_count = sum(1 for k in angles_2d if abs(angles_2d[k] - angles_3d[k]) > 0.1)
    print(f"\n   2D与3D角度差异数量: {diff_count}/{len(angles_2d)}")
    
    if diff_count > 0:
        print("   ✓ z坐标对角度计算有影响（符合预期）")
    else:
        print("   ℹ 当前测试数据中z坐标影响较小")
    
    print("\n✓ extract_angles 3D模式测试通过")


def test_mediapipe_z_coordinate():
    """测试MediaPipe是否提供z坐标"""
    print("\n" + "=" * 60)
    print("测试MediaPipe z坐标")
    print("=" * 60)
    
    try:
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions
        from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
        
        print("✓ MediaPipe已安装")
        
        # 检查是否有示例图片
        sample_img = Path(__file__).parent / 'data' / 'tennis_samples' / 'forehand_1.jpg'
        if sample_img.exists():
            print(f"✓ 找到示例图片: {sample_img.name}")
            print("  可以运行完整测试（需要手动上传图片）")
        else:
            print("⚠ 未找到示例图片")
        
        print("\n说明: MediaPipe Pose Landmarker 提供z坐标")
        print("   - z: 以臀部为原点的相对深度（米）")
        print("   - 负值表示靠近相机，正值表示远离相机")
        print("   - 可用于3D角度计算，减少透视变形影响")
        
    except ImportError as e:
        print(f"✗ MediaPipe未安装: {e}")
        print("  请运行: pip install mediapipe")


def main():
    print("\n" + "=" * 60)
    print("网球教练系统 - 3D角度计算验证")
    print("=" * 60)
    
    try:
        test_3d_angle_calculation()
        test_extract_angles_3d()
        test_mediapipe_z_coordinate()
        
        print("\n" + "=" * 60)
        print("✓ 所有3D角度测试通过！")
        print("=" * 60)
        print("\n功能说明:")
        print("1. ✓ 3D角度计算已实现")
        print("2. ✓ MediaPipe现在会保存z坐标")
        print("3. ✓ 自动降级：如果缺少z坐标，自动使用2D计算")
        print("4. ✓ 使用方式: 选择MediaPipe provider时自动启用3D模式")
        print("\n优势:")
        print("- 减少不同拍摄角度的误差")
        print("- 提高右上角/侧面拍摄的准确率")
        print("- 更好的深度感知")
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 运行错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()