#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PokeMMO自动化工具 - 配置工具
这个脚本用于修改配置文件
"""

import os
import sys
import json
import win32gui

def load_config(config_path="config.json"):
    """加载配置文件"""
    if not os.path.exists(config_path):
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return {}

def save_config(config, config_path="config.json"):
    """保存配置文件"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False

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

def configure_window(config):
    """配置窗口设置"""
    print("\n=== 窗口配置 ===")
    
    # 显示当前窗口设置
    current_name = config.get("window", {}).get("name", "PokeMMO")
    use_partial_match = config.get("window", {}).get("use_partial_match", True)
    auto_foreground = config.get("window", {}).get("auto_foreground", True)
    
    print(f"当前窗口名称: {current_name}")
    print(f"使用部分匹配: {use_partial_match}")
    print(f"自动设为前台: {auto_foreground}")
    
    # 列出所有窗口
    windows = list_all_windows()
    
    # 询问用户是否要更改窗口设置
    change = input("\n是否要更改窗口设置？(y/n): ")
    if change.lower() == 'y':
        # 询问用户选择窗口
        print("\n请输入要使用的窗口序号或直接输入窗口名称（直接回车保持不变）:")
        user_input = input("> ")
        
        window_name = current_name
        
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
        
        # 询问是否使用部分匹配
        use_partial = input("\n是否使用部分匹配？(y/n, 直接回车保持不变): ")
        if use_partial:
            use_partial_match = (use_partial.lower() == 'y')
        
        # 询问是否自动设为前台
        auto_fg = input("\n是否自动设为前台？(y/n, 直接回车保持不变): ")
        if auto_fg:
            auto_foreground = (auto_fg.lower() == 'y')
        
        # 更新配置
        if "window" not in config:
            config["window"] = {}
        
        config["window"]["name"] = window_name
        config["window"]["use_partial_match"] = use_partial_match
        config["window"]["auto_foreground"] = auto_foreground
        
        print("\n窗口配置已更新:")
        print(f"窗口名称: {window_name}")
        print(f"使用部分匹配: {use_partial_match}")
        print(f"自动设为前台: {auto_foreground}")
    
    return config

def configure_hotkeys(config):
    """配置热键设置"""
    print("\n=== 热键配置 ===")
    
    # 显示当前热键设置
    hotkeys = config.get("hotkeys", {})
    start_key = hotkeys.get("start", "f9")
    stop_key = hotkeys.get("stop", "f10")
    pause_key = hotkeys.get("pause", "f11")
    
    print(f"当前启动热键: {start_key}")
    print(f"当前停止热键: {stop_key}")
    print(f"当前暂停热键: {pause_key}")
    
    # 询问用户是否要更改热键设置
    change = input("\n是否要更改热键设置？(y/n): ")
    if change.lower() == 'y':
        # 询问用户输入新的热键
        new_start = input("\n请输入新的启动热键（直接回车保持不变）: ")
        if new_start:
            start_key = new_start.lower()
        
        new_stop = input("请输入新的停止热键（直接回车保持不变）: ")
        if new_stop:
            stop_key = new_stop.lower()
        
        new_pause = input("请输入新的暂停热键（直接回车保持不变）: ")
        if new_pause:
            pause_key = new_pause.lower()
        
        # 更新配置
        if "hotkeys" not in config:
            config["hotkeys"] = {}
        
        config["hotkeys"]["start"] = start_key
        config["hotkeys"]["stop"] = stop_key
        config["hotkeys"]["pause"] = pause_key
        
        print("\n热键配置已更新:")
        print(f"启动热键: {start_key}")
        print(f"停止热键: {stop_key}")
        print(f"暂停热键: {pause_key}")
    
    return config

def configure_ocr(config):
    """配置OCR设置"""
    print("\n=== OCR配置 ===")
    
    # 显示当前OCR设置
    ocr_config = config.get("ocr", {})
    language = ocr_config.get("language", "ch")
    threshold = ocr_config.get("threshold", 0.6)
    enable = ocr_config.get("enable", True)
    
    print(f"当前OCR语言: {language}")
    print(f"当前OCR阈值: {threshold}")
    print(f"OCR功能启用: {enable}")
    
    # 询问用户是否要更改OCR设置
    change = input("\n是否要更改OCR设置？(y/n): ")
    if change.lower() == 'y':
        # 询问OCR语言
        lang = input("\n请输入OCR语言 (ch/en, 直接回车保持不变): ")
        if lang and lang in ["ch", "en"]:
            language = lang
        
        # 询问OCR阈值
        thres = input("请输入OCR阈值 (0.0-1.0, 直接回车保持不变): ")
        if thres:
            try:
                thres_val = float(thres)
                if 0.0 <= thres_val <= 1.0:
                    threshold = thres_val
                else:
                    print("无效的阈值，必须在0.0到1.0之间")
            except ValueError:
                print("无效的阈值，必须是一个数字")
        
        # 询问是否启用OCR
        en = input("是否启用OCR功能？(y/n, 直接回车保持不变): ")
        if en:
            enable = (en.lower() == 'y')
        
        # 更新配置
        if "ocr" not in config:
            config["ocr"] = {}
        
        config["ocr"]["language"] = language
        config["ocr"]["threshold"] = threshold
        config["ocr"]["enable"] = enable
        
        print("\nOCR配置已更新:")
        print(f"OCR语言: {language}")
        print(f"OCR阈值: {threshold}")
        print(f"OCR功能启用: {enable}")
    
    return config

def configure_delay(config):
    """配置延迟设置"""
    print("\n=== 延迟配置 ===")
    
    # 显示当前延迟设置
    delay_config = config.get("delay", {})
    min_delay = delay_config.get("min", 0.5)
    max_delay = delay_config.get("max", 2.0)
    click_min = delay_config.get("click_min", 0.1)
    click_max = delay_config.get("click_max", 0.3)
    
    print(f"当前最小延迟: {min_delay}秒")
    print(f"当前最大延迟: {max_delay}秒")
    print(f"当前点击最小延迟: {click_min}秒")
    print(f"当前点击最大延迟: {click_max}秒")
    
    # 询问用户是否要更改延迟设置
    change = input("\n是否要更改延迟设置？(y/n): ")
    if change.lower() == 'y':
        # 询问最小延迟
        min_input = input("\n请输入最小延迟 (秒, 直接回车保持不变): ")
        if min_input:
            try:
                min_val = float(min_input)
                if min_val >= 0:
                    min_delay = min_val
                else:
                    print("无效的延迟，必须大于等于0")
            except ValueError:
                print("无效的延迟，必须是一个数字")
        
        # 询问最大延迟
        max_input = input("请输入最大延迟 (秒, 直接回车保持不变): ")
        if max_input:
            try:
                max_val = float(max_input)
                if max_val >= min_delay:
                    max_delay = max_val
                else:
                    print(f"无效的延迟，必须大于等于最小延迟 {min_delay}")
            except ValueError:
                print("无效的延迟，必须是一个数字")
        
        # 询问点击最小延迟
        click_min_input = input("请输入点击最小延迟 (秒, 直接回车保持不变): ")
        if click_min_input:
            try:
                click_min_val = float(click_min_input)
                if click_min_val >= 0:
                    click_min = click_min_val
                else:
                    print("无效的延迟，必须大于等于0")
            except ValueError:
                print("无效的延迟，必须是一个数字")
        
        # 询问点击最大延迟
        click_max_input = input("请输入点击最大延迟 (秒, 直接回车保持不变): ")
        if click_max_input:
            try:
                click_max_val = float(click_max_input)
                if click_max_val >= click_min:
                    click_max = click_max_val
                else:
                    print(f"无效的延迟，必须大于等于点击最小延迟 {click_min}")
            except ValueError:
                print("无效的延迟，必须是一个数字")
        
        # 更新配置
        if "delay" not in config:
            config["delay"] = {}
        
        config["delay"]["min"] = min_delay
        config["delay"]["max"] = max_delay
        config["delay"]["click_min"] = click_min
        config["delay"]["click_max"] = click_max
        
        print("\n延迟配置已更新:")
        print(f"最小延迟: {min_delay}秒")
        print(f"最大延迟: {max_delay}秒")
        print(f"点击最小延迟: {click_min}秒")
        print(f"点击最大延迟: {click_max}秒")
    
    return config

def main():
    """主函数"""
    print("PokeMMO自动化工具 - 配置工具")
    
    # 加载配置
    config_path = "config.json"
    config = load_config(config_path)
    
    if not config:
        print(f"警告: 无法加载配置文件 {config_path}，将创建新的配置")
        config = {
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
                "max": 2.0,
                "click_min": 0.1,
                "click_max": 0.3
            },
            "ocr": {
                "language": "ch",
                "threshold": 0.6,
                "enable": True
            },
            "hotkeys": {
                "start": "f9",
                "stop": "f10",
                "pause": "f11"
            },
            "debug": {
                "save_screenshots": True,
                "verbose_logging": False
            }
        }
    
    # 配置各个部分
    while True:
        print("\n=== 配置菜单 ===")
        print("1. 窗口配置")
        print("2. 热键配置")
        print("3. OCR配置")
        print("4. 延迟配置")
        print("5. 保存并退出")
        print("6. 退出（不保存）")
        
        choice = input("\n请选择 (1-6): ")
        
        if choice == '1':
            config = configure_window(config)
        elif choice == '2':
            config = configure_hotkeys(config)
        elif choice == '3':
            config = configure_ocr(config)
        elif choice == '4':
            config = configure_delay(config)
        elif choice == '5':
            # 保存并退出
            if save_config(config, config_path):
                print(f"\n配置已保存到 {config_path}")
            else:
                print(f"\n配置保存失败！")
            break
        elif choice == '6':
            # 退出不保存
            print("\n退出而不保存配置")
            break
        else:
            print("\n无效的选择，请重试")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序异常: {e}")
        import traceback
        traceback.print_exc() 