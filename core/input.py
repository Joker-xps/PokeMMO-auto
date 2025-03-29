import pyautogui
import random
import time
import win32api
import win32con
import keyboard

class InputManager:
    def __init__(self, game_window):
        """
        初始化输入管理器
        game_window: GameWindow实例
        """
        self.game_window = game_window
        pyautogui.FAILSAFE = False  # 禁用故障安全，谨慎使用
    
    def press_key(self, key, delay=None):
        """
        按下并释放按键
        key: 按键名称，如'a', 'enter', 'esc'等
        delay: 按键按下后的延迟时间，None为随机延迟
        """
        # 设置窗口为前台
        self.game_window.set_foreground()
        
        # 随机延迟
        if delay is None:
            delay = self.game_window.random_delay(0.05, 0.15)
        
        # 按下并释放按键
        pyautogui.press(key)
        
        # 延迟
        time.sleep(delay)
    
    def key_down(self, key):
        """
        按下按键不释放
        key: 按键名称，如'w', 'a', 's', 'd'等
        """
        # 设置窗口为前台
        self.game_window.set_foreground()
        
        # 按下按键
        pyautogui.keyDown(key)
    
    def key_up(self, key):
        """
        释放按键
        key: 按键名称，如'w', 'a', 's', 'd'等
        """
        # 释放按键
        pyautogui.keyUp(key)
    
    def type_text(self, text, interval=None):
        """
        输入文本
        text: 要输入的文本
        interval: 按键间隔时间，None为随机间隔
        """
        # 设置窗口为前台
        self.game_window.set_foreground()
        
        # 随机间隔
        if interval is None:
            interval = self.game_window.random_delay(0.05, 0.15)
        
        # 输入文本
        pyautogui.write(text, interval=interval)
    
    def press_hotkey(self, *keys):
        """
        按下热键组合
        *keys: 按键组合，如'ctrl', 'c'表示Ctrl+C
        """
        # 设置窗口为前台
        self.game_window.set_foreground()
        
        # 按下热键组合
        pyautogui.hotkey(*keys)
        
        # 随机延迟
        time.sleep(self.game_window.random_delay(0.1, 0.2))
    
    def mouse_move(self, x, y, duration=None, human_like=True):
        """
        移动鼠标到指定位置
        x, y: 目标坐标
        duration: 移动持续时间，None为随机时间
        human_like: 是否模拟人类移动轨迹
        """
        # 设置窗口为前台
        self.game_window.set_foreground()
        
        # 将客户区坐标转换为屏幕坐标
        screen_x, screen_y = self.game_window.client_to_screen(x, y)
        
        # 随机持续时间
        if duration is None:
            duration = self.game_window.random_delay(0.1, 0.3)
        
        # 人性化移动轨迹
        if human_like:
            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()
            
            # 生成轨迹点
            points = self._generate_human_like_mouse_path(
                current_x, current_y, screen_x, screen_y
            )
            
            # 移动鼠标
            time_per_point = duration / len(points)
            for point_x, point_y in points:
                pyautogui.moveTo(point_x, point_y, duration=time_per_point)
        else:
            # 直接移动
            pyautogui.moveTo(screen_x, screen_y, duration=duration)
    
    def _generate_human_like_mouse_path(self, start_x, start_y, end_x, end_y, deviation_factor=50):
        """
        生成模拟人类移动轨迹的路径点
        start_x, start_y: 起始坐标
        end_x, end_y: 结束坐标
        deviation_factor: 轨迹偏移因子
        """
        # 计算距离
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        
        # 根据距离决定采样点数量
        num_points = max(10, int(distance / 15))
        
        # 生成路径点
        points = []
        for i in range(num_points + 1):
            # 计算当前位置的理想坐标（直线插值）
            t = i / num_points
            ideal_x = start_x + (end_x - start_x) * t
            ideal_y = start_y + (end_y - start_y) * t
            
            # 添加随机偏移（偏移越来越小）
            remaining = 1 - t
            offset_factor = deviation_factor * (remaining ** 2)
            offset_x = random.gauss(0, 1) * offset_factor
            offset_y = random.gauss(0, 1) * offset_factor
            
            # 计算实际坐标
            actual_x = round(ideal_x + offset_x)
            actual_y = round(ideal_y + offset_y)
            
            # 添加到路径点
            points.append((actual_x, actual_y))
        
        # 确保最后一个点是目标点
        points[-1] = (end_x, end_y)
        
        return points
    
    def scroll(self, clicks, x=None, y=None):
        """
        滚动鼠标滚轮
        clicks: 滚动量，正值向上滚动，负值向下滚动
        x, y: 滚动位置，None表示当前鼠标位置
        """
        # 设置窗口为前台
        self.game_window.set_foreground()
        
        if x is not None and y is not None:
            # 将客户区坐标转换为屏幕坐标
            screen_x, screen_y = self.game_window.client_to_screen(x, y)
            
            # 移动鼠标到指定位置
            pyautogui.moveTo(screen_x, screen_y, 
                             duration=self.game_window.random_delay(0.1, 0.2))
        
        # 滚动鼠标滚轮
        pyautogui.scroll(clicks)
        
        # 随机延迟
        time.sleep(self.game_window.random_delay(0.1, 0.2))
    
    def register_hotkey(self, hotkey, callback):
        """
        注册热键回调函数
        hotkey: 热键组合，如'ctrl+shift+p'
        callback: 回调函数
        """
        keyboard.add_hotkey(hotkey, callback)
    
    def unregister_hotkey(self, hotkey):
        """
        取消注册热键
        hotkey: 热键组合，如'ctrl+shift+p'
        """
        keyboard.remove_hotkey(hotkey) 