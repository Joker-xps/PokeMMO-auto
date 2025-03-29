#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PokeMMO自动化工具 - 窗口测试脚本
这个脚本用于测试窗口检测和截图功能
"""

import os
import sys
import time
import cv2
import win32gui

from core.window import GameWindow
from core.image import ImageManager

def list_all_windows():
    """列出所有可见窗口"""
    print("\n=== 当前系统所有可见窗口 ===")
    windows = []
    
    def enum_windows_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if window_title:  # 只显示有标题的窗口
                results.append((hwnd, window_title))
        return True
    
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    # 按标题排序
    windows.sort(key=lambda x: x[1].lower())
    
    for i, (hwnd, title) in enumerate(windows):
        print(f"{i+1}. '{title}' (句柄: {hwnd})")
    
    return windows

def test_window(window_name=None):
    """测试指定名称的窗口"""
    if window_name is None:
        window_name = "PokeMMO"  # 默认窗口名称
    
    print(f"\n=== 测试窗口 '{window_name}' ===")
    
    # 创建GameWindow实例
    window = GameWindow(window_name)
    
    # 测试窗口是否有效
    is_valid = window.is_window_valid()
    print(f"窗口有效: {is_valid}")
    
    if is_valid:
        # 获取窗口位置
        window_rect = window.update_window_rect()
        print(f"窗口位置: {window_rect}")
        
        # 获取客户区大小
        client_rect = window.get_client_rect()
        print(f"客户区: {client_rect}")
        
        # 尝试设为前台
        print("尝试设置为前台窗口...")
        result = window.set_foreground()
        print(f"设置前台结果: {result}")
        
        # 创建ImageManager并截图
        print("尝试截取屏幕...")
        img_manager = ImageManager(window)
        try:
            screen = img_manager.capture_screen()
            
            # 创建screenshots目录
            screenshots_dir = "screenshots"
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)
            
            # 保存截图
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshots_dir, f"test_{timestamp}.png")
            cv2.imwrite(screenshot_path, screen)
            print(f"截图已保存到: {screenshot_path}")
            print(f"截图尺寸: {screen.shape[1]}x{screen.shape[0]}")
            
            return True
        except Exception as e:
            print(f"截图失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("窗口无效，无法进行后续测试")
        return False

def main():
    """主函数"""
    print("PokeMMO自动化工具 - 窗口测试")
    
    # 列出所有窗口
    windows = list_all_windows()
    
    # 询问用户选择窗口
    print("\n请输入要测试的窗口序号或直接输入窗口名称（直接回车使用默认'PokeMMO'）:")
    user_input = input("> ")
    
    window_name = "PokeMMO"  # 默认窗口名称
    
    if user_input:
        try:
            # 尝试解析为序号
            index = int(user_input) - 1
            if 0 <= index < len(windows):
                window_name = windows[index][1]
            else:
                print(f"序号 {user_input} 超出范围，使用输入作为窗口名称")
                window_name = user_input
        except ValueError:
            # 不是数字，直接作为窗口名称
            window_name = user_input
    
    # 测试指定窗口
    test_result = test_window(window_name)
    
    if test_result:
        print("\n窗口测试成功！现在您可以使用这个窗口名称进行自动化操作")
        print(f"窗口名称: '{window_name}'")
        print("建议在config.json文件中设置正确的窗口名称")
    else:
        print("\n窗口测试失败！请确保窗口存在且可见")
        print("您可以再次运行此脚本尝试其他窗口")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序异常: {e}")
        import traceback
        traceback.print_exc() 