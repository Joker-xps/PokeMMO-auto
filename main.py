#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import threading
import keyboard
import cv2

from core import GameWindow, ImageManager, OCRManager, InputManager, AlertManager
from utils import load_config, save_config, create_directory, get_all_templates

class PokeMMOAutoBot:
    def __init__(self, config_path="config.json"):
        """初始化自动化机器人"""
        print("初始化 PokeMMO 自动化工具...")
        
        # 加载配置
        self.config = load_config(config_path)
        if not self.config:
            print("配置文件加载失败，使用默认配置")
            self.config = {
                "window": {
                    "name": "PokeMMO",
                    "use_partial_match": True,
                    "auto_foreground": True
                },
                "templates_dir": "resources/templates",
                "sounds_dir": "resources/sounds",
                "screenshots_dir": "screenshots",
                "delay": {
                    "min": 0.5,
                    "max": 2.0
                },
                "ocr": {
                    "language": "ch",
                    "threshold": 0.6,
                    "enable": True
                },
                "debug": {
                    "save_screenshots": True,
                    "verbose_logging": True
                }
            }
        
        # 创建必要的目录
        create_directory(self.config["templates_dir"])
        create_directory(self.config["sounds_dir"])
        create_directory(self.config["screenshots_dir"])
        
        # 初始化组件
        try:
            # 初始化游戏窗口
            window_name = self.config["window"]["name"]
            use_partial_match = self.config["window"].get("use_partial_match", True)
            print(f"尝试查找窗口: {window_name} (部分匹配: {use_partial_match})")
            self.game_window = GameWindow(window_name, use_partial_match=use_partial_match)
            
            # 初始化图像管理器
            print("初始化图像管理器...")
            self.image_manager = ImageManager(self.game_window)
            
            # 初始化OCR管理器
            ocr_enable = self.config["ocr"].get("enable", True)
            if ocr_enable:
                print("初始化OCR管理器...")
                ocr_lang = self.config["ocr"]["language"]
                self.ocr_manager = OCRManager(
                    self.game_window, 
                    self.image_manager,
                    ocr_lang
                )
            else:
                print("OCR功能已禁用")
                self.ocr_manager = None
            
            # 初始化输入管理器
            print("初始化输入管理器...")
            self.input_manager = InputManager(self.game_window)
            
            # 初始化警报管理器
            if ocr_enable:
                print("初始化警报管理器...")
                check_interval = self.config.get("captcha", {}).get("check_interval", 5)
                self.alert_manager = AlertManager(self.ocr_manager, check_interval)
            else:
                print("警报管理器已禁用 (OCR未启用)")
                self.alert_manager = None
            
            # 加载模板
            print("加载图像模板...")
            self.templates = get_all_templates(self.config["templates_dir"])
            print(f"加载了 {len(self.templates)} 个模板图像")
            
            # 运行状态
            self.running = False
            self.paused = False
            self.stop_event = threading.Event()
            
            # 注册热键
            self._register_hotkeys()
            
            print("初始化完成！")
        
        except Exception as e:
            print(f"初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _register_hotkeys(self):
        """注册热键"""
        hotkeys = self.config.get("hotkeys", {})
        
        if "start" in hotkeys:
            keyboard.add_hotkey(hotkeys["start"], self.start)
            print(f"注册启动热键: {hotkeys['start']}")
            
        if "stop" in hotkeys:
            keyboard.add_hotkey(hotkeys["stop"], self.stop)
            print(f"注册停止热键: {hotkeys['stop']}")
            
        if "pause" in hotkeys:
            keyboard.add_hotkey(hotkeys["pause"], self.toggle_pause)
            print(f"注册暂停热键: {hotkeys['pause']}")
    
    def captcha_detected_callback(self):
        """验证码检测回调函数"""
        print("检测到验证码！程序已停止")
        self.stop()
    
    def start(self):
        """启动自动化"""
        if self.running:
            if self.paused:
                self.paused = False
                print("继续运行...")
            return
        
        print("开始自动化...")
        self.running = True
        self.paused = False
        self.stop_event.clear()
        
        # 启动验证码检测
        if self.alert_manager:
            self.alert_manager.start_captcha_check(self.captcha_detected_callback)
        
        # 启动主线程
        threading.Thread(target=self._main_loop, daemon=True).start()
    
    def stop(self):
        """停止自动化"""
        if not self.running:
            return
        
        print("停止自动化...")
        self.stop_event.set()
        self.running = False
        self.paused = False
        
        # 停止验证码检测
        if self.alert_manager:
            self.alert_manager.stop_captcha_check()
    
    def toggle_pause(self):
        """切换暂停状态"""
        if not self.running:
            return
        
        self.paused = not self.paused
        if self.paused:
            print("暂停...")
        else:
            print("继续...")
    
    def _main_loop(self):
        """主循环"""
        try:
            while self.running and not self.stop_event.is_set():
                # 如果暂停，等待
                if self.paused:
                    time.sleep(0.5)
                    continue
                
                # 示例功能：在屏幕上查找并点击物品按钮
                print("在屏幕上寻找目标...")
                
                # 示例图片模板查找
                template_name = "1"  # 替换为实际模板名称
                if template_name in self.templates:
                    template_path = self.templates[template_name]
                    result = self.image_manager.find_template(template_path, region=(1080,523,194,72))
                    
                    if result:
                        print(f"找到目标 {template_name}！位置: {result[:2]}")
                        # 点击找到的位置
                        self.image_manager.click_position(result)
                        time.sleep(1)  # 等待响应
                else:
                    print(f"模板 {template_name} 不存在")
                
                # 简单的随机延迟，模拟人类行为
                delay_min = self.config["delay"]["min"]
                delay_max = self.config["delay"]["max"]
                delay = self.game_window.random_delay(delay_min, delay_max)
                
                # 检查是否应该停止
                if self.stop_event.wait(0.1):
                    break
        
        except Exception as e:
            print(f"自动化过程中出现错误: {str(e)}")
            import traceback
            traceback.print_exc()
            self.stop()
    
    def run_example(self):
        """运行示例任务"""
        # 检查游戏窗口是否有效
        print("\n测试窗口状态...")
        if not self.game_window.is_window_valid():
            print("游戏窗口无效，请确保游戏正在运行")
            print("警告: 将继续运行，但可能无法正常工作")
        
        try:
            # 将游戏窗口设为前台
            print("尝试激活游戏窗口...")
            foreground_result = self.game_window.set_foreground()
            if foreground_result:
                print("游戏窗口已激活")
            else:
                print("警告: 无法将游戏窗口设为前台，但将继续尝试其他功能")
            
            # 获取窗口信息
            window_rect = self.game_window.update_window_rect()
            if window_rect:
                print(f"窗口位置: {window_rect}")
            else:
                print("警告: 无法获取窗口位置")
            
            # 截取屏幕
            print("尝试截取屏幕...")
            try:
                screen = self.image_manager.capture_screen()
                # 保存截图以便查看
                if self.config.get("debug", {}).get("save_screenshots", True):
                    screenshot_path = os.path.join(self.config["screenshots_dir"], "test_screenshot.png")
                    cv2.imwrite(screenshot_path, screen)
                    print(f"截图已保存到: {screenshot_path}")
                print(f"截取屏幕，尺寸: {screen.shape[1]}x{screen.shape[0]}")
            except Exception as e:
                print(f"截取屏幕失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 示例：查找文字 - 这可能比较慢，所以要捕获可能的异常
            if self.ocr_manager:
                print("尝试进行OCR文字识别...")
                try:
                    text_results = self.ocr_manager.recognize_text()
                    print("识别到以下文字:")
                    if text_results:
                        for text, position, confidence in text_results[:5]:  # 只显示前5个结果
                            print(f"- '{text}' 位置: {position}, 置信度: {confidence:.2f}")
                    else:
                        print("未识别到任何文字")
                except Exception as e:
                    print(f"OCR识别失败: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("跳过OCR文字识别 (OCR未启用)")
            
            # 示例：查找特定颜色
            print("尝试查找颜色...")
            try:
                target_color = (255, 0, 0)  # 红色
                color_pos = self.image_manager.find_color(target_color, tolerance=20)
                if color_pos:
                    print(f"找到颜色 {target_color} 在位置: {color_pos}")
                else:
                    print(f"未找到颜色 {target_color}")
            except Exception as e:
                print(f"查找颜色失败: {e}")
                import traceback
                traceback.print_exc()
            
            print("示例任务完成")
        
        except Exception as e:
            print(f"运行示例时出现错误: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """主函数入口点"""
    try:
        # 创建自动化机器人
        bot = PokeMMOAutoBot()
        
        # 运行示例
        bot._main_loop()
        
        # 提示用户使用热键
        print("\n使用以下热键控制程序:")
        hotkeys = bot.config.get("hotkeys", {})
        print(f"  启动: {hotkeys.get('start', 'F9')}")
        print(f"  停止: {hotkeys.get('stop', 'F10')}")
        print(f"  暂停/继续: {hotkeys.get('pause', 'F11')}")
        print("\n按 Ctrl+C 退出程序")
        
        # 保持程序运行
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"程序异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 