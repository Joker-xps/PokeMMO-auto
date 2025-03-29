#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import random
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import GameWindow, ImageManager, OCRManager, InputManager, AlertManager
from utils import load_config, save_config, create_directory, get_all_templates

class FishingTask:
    def __init__(self, bot):
        """
        钓鱼任务
        bot: PokeMMOAutoBot实例
        """
        self.bot = bot
        self.game_window = bot.game_window
        self.image_manager = bot.image_manager
        self.ocr_manager = bot.ocr_manager
        self.input_manager = bot.input_manager
        self.alert_manager = bot.alert_manager
        self.config = bot.config
        self.templates = bot.templates
        
        # 钓鱼相关配置
        self.fishing_config = {
            "max_attempts": 1000,  # 最大钓鱼次数
            "wait_time_min": 2,    # 等待咬钩最小时间（秒）
            "wait_time_max": 20,   # 等待咬钩最大时间（秒）
            "fishing_regions": {   # 可以定义多个钓鱼区域
                "default": None,   # 整个屏幕
                "center": (100, 100, 400, 300)  # 自定义区域 (x, y, width, height)
            },
            "fishing_rod_key": "1",  # 钓鱼竿物品栏位置对应的快捷键
        }
        
        # 钓鱼状态
        self.fish_caught = 0
        self.attempts = 0
    
    def start_fishing(self, region_name="default", max_attempts=None):
        """
        开始钓鱼
        region_name: 钓鱼区域名称
        max_attempts: 最大尝试次数
        """
        if max_attempts is not None:
            self.fishing_config["max_attempts"] = max_attempts
        
        # 获取钓鱼区域
        region = self.fishing_config["fishing_regions"].get(region_name)
        
        # 确保游戏窗口在前台
        self.game_window.set_foreground()
        
        print(f"开始钓鱼任务，区域: {region_name}，最大尝试次数: {self.fishing_config['max_attempts']}")
        
        # 开始钓鱼循环
        self.fish_caught = 0
        self.attempts = 0
        
        try:
            while self.attempts < self.fishing_config["max_attempts"] and not self.bot.stop_event.is_set():
                # 检查是否暂停
                if self.bot.paused:
                    time.sleep(0.5)
                    continue
                
                # 尝试钓鱼
                self.attempts += 1
                print(f"钓鱼尝试 #{self.attempts}")
                
                # 1. 使用钓鱼竿
                self._use_fishing_rod()
                
                # 2. 等待鱼咬钩
                if self._wait_for_bite(region):
                    # 3. 拉鱼
                    if self._reel_in():
                        self.fish_caught += 1
                        print(f"成功钓到鱼！总计: {self.fish_caught}")
                    else:
                        print("鱼跑掉了...")
                else:
                    print("等待超时，没有鱼咬钩")
                
                # 随机延迟，模拟人类行为
                delay = random.uniform(1.0, 3.0)
                time.sleep(delay)
        
        except Exception as e:
            print(f"钓鱼过程中出现错误: {str(e)}")
        
        print(f"钓鱼任务结束。总尝试次数: {self.attempts}，成功钓到: {self.fish_caught}")
        return self.fish_caught
    
    def _use_fishing_rod(self):
        """使用钓鱼竿"""
        # 按下对应的物品栏快捷键
        rod_key = self.fishing_config["fishing_rod_key"]
        self.input_manager.press_key(rod_key)
        time.sleep(self.game_window.random_delay(0.2, 0.5))
        
        # 点击屏幕中央位置（钓鱼位置）
        client_rect = self.game_window.get_client_rect()
        center_x = client_rect["width"] // 2
        center_y = client_rect["height"] // 2
        
        # 添加一些随机偏移
        offset = 20
        center_x += random.randint(-offset, offset)
        center_y += random.randint(-offset, offset)
        
        # 点击施放钓鱼竿
        self.image_manager.click_position((center_x, center_y))
        
        # 等待钓鱼竿抛出
        time.sleep(self.game_window.random_delay(0.8, 1.2))
    
    def _wait_for_bite(self, region=None):
        """
        等待鱼咬钩
        region: 监测区域
        """
        # 钓鱼咬钩关键词
        bite_keywords = ["鱼咬钩了", "咬钩", "有鱼"]
        
        # 钓鱼咬钩图像模板
        bite_templates = ["fishing_bite", "fishing_exclamation"]
        
        # 等待时间
        min_wait = self.fishing_config["wait_time_min"]
        max_wait = self.fishing_config["wait_time_max"]
        wait_time = random.uniform(min_wait, max_wait)
        start_time = time.time()
        
        print(f"等待鱼咬钩，最长等待 {wait_time:.1f} 秒...")
        
        while time.time() - start_time < wait_time and not self.bot.stop_event.is_set():
            # 检查是否暂停
            if self.bot.paused:
                time.sleep(0.5)
                continue
            
            # 方法1：OCR检测文字提示
            for keyword in bite_keywords:
                text_pos = self.ocr_manager.find_text(keyword, region=region)
                if text_pos:
                    print(f"检测到咬钩文字: '{keyword}'")
                    time.sleep(self.game_window.random_delay(0.1, 0.3))  # 短暂延迟，模拟反应时间
                    return True
            
            # 方法2：图像模板匹配
            for template_name in bite_templates:
                if template_name in self.templates:
                    template_path = self.templates[template_name]
                    result = self.image_manager.find_template(template_path, region=region)
                    if result:
                        print(f"检测到咬钩图标，匹配度: {result[2]:.2f}")
                        time.sleep(self.game_window.random_delay(0.1, 0.3))  # 短暂延迟，模拟反应时间
                        return True
            
            # 方法3：特定颜色检测（如感叹号的颜色）
            exclamation_color = (255, 255, 0)  # 黄色
            color_pos = self.image_manager.find_color(exclamation_color, tolerance=30, region=region)
            if color_pos:
                print(f"检测到咬钩颜色: {exclamation_color} 在位置 {color_pos}")
                time.sleep(self.game_window.random_delay(0.1, 0.3))  # 短暂延迟，模拟反应时间
                return True
            
            # 短暂休眠，避免过高的CPU使用率
            time.sleep(0.1)
        
        return False
    
    def _reel_in(self):
        """
        拉鱼（钓鱼竿收杆）
        """
        # 方法1：点击屏幕
        client_rect = self.game_window.get_client_rect()
        center_x = client_rect["width"] // 2
        center_y = client_rect["height"] // 2
        
        # 添加一些随机偏移
        offset = 20
        center_x += random.randint(-offset, offset)
        center_y += random.randint(-offset, offset)
        
        # 点击收杆
        self.image_manager.click_position((center_x, center_y))
        
        # 等待钓鱼结果
        wait_time = random.uniform(1.5, 3.0)
        time.sleep(wait_time)
        
        # 这里应该检测是否成功钓到鱼，但由于没有具体的游戏机制细节，暂时随机模拟
        # 实际使用时，应该基于实际游戏界面添加检测逻辑
        success_rate = 0.7  # 假设70%成功率
        return random.random() < success_rate 