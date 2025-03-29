import win32gui
import win32con
import win32api
import time
import random
import ctypes

class GameWindow:
    def __init__(self, window_name="PokeMMO", use_partial_match=True):
        self.window_name = window_name
        self.use_partial_match = use_partial_match
        self.hwnd = None
        self.rect = None
        self.find_window()
    
    def find_window(self):
        """查找并获取游戏窗口句柄"""
        # 尝试直接通过完整窗口名查找
        self.hwnd = win32gui.FindWindow(None, self.window_name)
        
        # 如果找不到，且允许部分匹配，则尝试部分匹配
        if not self.hwnd and self.use_partial_match:
            self.hwnd = self._find_window_by_partial_title(self.window_name)
            
        if self.hwnd:
            self.update_window_rect()
            print(f"找到窗口: {self.window_name}，句柄: {self.hwnd}")
            return self.hwnd
        else:
            print(f"警告：未找到窗口: {self.window_name}")
            return None
    
    def _find_window_by_partial_title(self, partial_title):
        """通过部分标题查找窗口"""
        result = []
        
        def enum_windows_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if partial_title.lower() in window_title.lower():
                    results.append((hwnd, window_title))
            return True
        
        win32gui.EnumWindows(enum_windows_callback, result)
        
        if result:
            # 打印找到的所有匹配窗口，以便调试
            for hwnd, title in result:
                print(f"找到匹配窗口: '{title}', 句柄: {hwnd}")
            # 返回第一个匹配的窗口句柄
            return result[0][0]
        
        return None
    
    def update_window_rect(self):
        """更新窗口位置和大小信息"""
        if not self.hwnd:
            self.find_window()
            if not self.hwnd:
                return None
        
        try:
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            self.rect = {
                'left': left,
                'top': top,
                'right': right,
                'bottom': bottom,
                'width': right - left,
                'height': bottom - top,
                'center_x': (right + left) // 2,
                'center_y': (bottom + top) // 2
            }
            return self.rect
        except Exception as e:
            print(f"获取窗口位置失败: {e}")
            return None
    
    def set_foreground(self):
        """将游戏窗口设置为前台窗口"""
        if not self.hwnd:
            self.hwnd = self.find_window()
            if not self.hwnd:
                print("警告: 无法设置前台窗口 - 未找到窗口")
                return False
        
        try:
            # 检查窗口是否仍然有效
            if not win32gui.IsWindow(self.hwnd):
                print("警告: 窗口句柄已失效，尝试重新查找窗口")
                self.hwnd = self.find_window()
                if not self.hwnd:
                    return False
            
            # 如果窗口最小化，先恢复
            if win32gui.IsIconic(self.hwnd):
                try:
                    win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                    time.sleep(0.1)  # 等待窗口恢复
                except Exception as e:
                    print(f"恢复窗口失败: {e}")
            
            # 尝试不同的方式来设置前台窗口
            try:
                # 方法1: 直接设置前台窗口
                result = win32gui.SetForegroundWindow(self.hwnd)
                
                # 如果成功设置，等待窗口激活
                time.sleep(self.random_delay(0.1, 0.3))
                return True
            except Exception as e:
                print(f"SetForegroundWindow失败: {e}")
                
                try:
                    # 方法2: 使用另一种方式
                    shell = ctypes.windll.user32
                    shell.SetForegroundWindow(self.hwnd)
                    time.sleep(0.1)
                    return True
                except Exception as e:
                    print(f"尝试备用方法设置前台窗口失败: {e}")
                    return False
        
        except Exception as e:
            print(f"设置前台窗口时出现错误: {e}")
            return False
    
    def client_to_screen(self, x, y):
        """将客户区坐标转换为屏幕坐标"""
        if not self.hwnd:
            self.find_window()
            if not self.hwnd:
                print("警告: 无法转换坐标 - 未找到窗口")
                return (x, y)  # 返回原始坐标
        
        try:
            # 获取窗口客户区坐标
            left, top, _, _ = win32gui.GetClientRect(self.hwnd)
            # 将客户区坐标转换为屏幕坐标
            screen_x, screen_y = win32gui.ClientToScreen(self.hwnd, (left + x, top + y))
            return screen_x, screen_y
        except Exception as e:
            print(f"坐标转换失败: {e}")
            # 如果转换失败，尝试使用窗口坐标
            if self.rect:
                return self.rect['left'] + x, self.rect['top'] + y
            return (x, y)  # 返回原始坐标
    
    def get_client_rect(self):
        """获取客户区尺寸"""
        if not self.hwnd:
            self.find_window()
            if not self.hwnd:
                print("警告: 无法获取客户区 - 未找到窗口")
                # 返回默认值
                return {
                    'left': 0,
                    'top': 0,
                    'right': 800,
                    'bottom': 600,
                    'width': 800,
                    'height': 600
                }
        
        try:
            left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
            return {
                'left': left,
                'top': top,
                'right': right,
                'bottom': bottom,
                'width': right - left,
                'height': bottom - top
            }
        except Exception as e:
            print(f"获取客户区失败: {e}")
            # 返回默认值或窗口大小
            if self.rect:
                return {
                    'left': 0,
                    'top': 0,
                    'right': self.rect['width'],
                    'bottom': self.rect['height'],
                    'width': self.rect['width'],
                    'height': self.rect['height']
                }
            return {
                'left': 0,
                'top': 0,
                'right': 800,
                'bottom': 600,
                'width': 800,
                'height': 600
            }
    
    def is_window_valid(self):
        """检查窗口是否有效"""
        if not self.hwnd:
            return False
        
        try:
            return win32gui.IsWindow(self.hwnd)
        except:
            return False
    
    @staticmethod
    def random_delay(min_time, max_time):
        """生成随机延时"""
        return random.uniform(min_time, max_time)

# 如果直接运行此文件，使用以下代码进行测试
if __name__ == "__main__":
    # 测试窗口查找
    window = GameWindow("PokeMMO", use_partial_match=True)
    print(f"窗口句柄: {window.hwnd}")
    print(f"窗口位置: {window.rect}")
    
    # 设置窗口前台
    if window.hwnd:
        print("尝试设置窗口为前台...")
        result = window.set_foreground()
        print(f"设置结果: {result}")
    
    # 获取客户区信息
    client_rect = window.get_client_rect()
    print(f"客户区: {client_rect}")
    
    # 测试坐标转换
    if window.hwnd:
        x, y = 100, 100
        screen_x, screen_y = window.client_to_screen(x, y)
        print(f"客户区坐标 ({x}, {y}) 转换为屏幕坐标: ({screen_x}, {screen_y})")
    
    
