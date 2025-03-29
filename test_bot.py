#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
from main import PokeMMOAutoBot
from tasks.fishing import FishingTask

def main():
    print("开始测试 PokeMMO 自动化工具...")
    
    try:
        # 创建自动化机器人实例
        bot = PokeMMOAutoBot()
        
        # 检查窗口是否存在
        if not bot.game_window.is_window_valid():
            print("警告: 未找到游戏窗口，请确保 PokeMMO 游戏已运行")
            print("尝试在没有找到窗口的情况下继续...")
        
        # 运行示例功能
        print("\n=== 测试基本功能 ===")
        bot.run_example()
        
        # 询问用户是否要测试钓鱼功能
        print("\n=== 测试钓鱼功能 ===")
        response = input("是否要测试钓鱼功能？(y/n): ")
        
        if response.lower() == 'y':
            # 创建钓鱼任务实例
            fishing = FishingTask(bot)
            
            # 设置钓鱼参数
            max_attempts = 5  # 限制尝试次数为5次，方便测试
            region_name = "default"  # 使用默认区域（整个屏幕）
            
            # 开始钓鱼
            print(f"\n开始钓鱼测试，最大尝试次数: {max_attempts}")
            fishing.start_fishing(region_name=region_name, max_attempts=max_attempts)
        
        # 显示热键信息
        print("\n=== 热键控制 ===")
        hotkeys = bot.config.get("hotkeys", {})
        print(f"  启动: {hotkeys.get('start', 'F9')}")
        print(f"  停止: {hotkeys.get('stop', 'F10')}")
        print(f"  暂停/继续: {hotkeys.get('pause', 'F11')}")
        
        # 等待用户退出
        print("\n测试完成。按 Ctrl+C 退出程序...")
        
        try:
            # 保持程序运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n程序已退出")
    
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 