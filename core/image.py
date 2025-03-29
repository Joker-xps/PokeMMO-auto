import cv2
import numpy as np
import win32gui
import win32ui
import win32con
import random
import time
from PIL import Image

class ImageManager:
    def __init__(self, game_window):
        self.game_window = game_window
    
    def capture_screen(self, region=None):
        """捕获游戏窗口屏幕"""
        hwnd = self.game_window.hwnd
        if not hwnd:
            self.game_window.find_window()
            hwnd = self.game_window.hwnd
        
        # 获取窗口尺寸
        client_rect = self.game_window.get_client_rect()
        width = client_rect['width']
        height = client_rect['height']
        
        # 定义捕获区域
        if region:
            x, y, w, h = region
            # 确保区域在窗口内
            x = max(0, min(x, width))
            y = max(0, min(y, height))
            w = max(1, min(w, width - x))
            h = max(1, min(h, height - y))
        else:
            x, y, w, h = 0, 0, width, height
        
        # 创建设备上下文
        hdc = win32gui.GetDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hdc)
        save_dc = mfc_dc.CreateCompatibleDC()
        
        # 创建位图对象
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(save_bitmap)
        
        # 复制屏幕到位图
        save_dc.BitBlt((0, 0), (w, h), mfc_dc, (x, y), win32con.SRCCOPY)
        
        # 转换位图为图像数据
        bmp_info = save_bitmap.GetInfo()
        bmp_str = save_bitmap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmp_info['bmWidth'], bmp_info['bmHeight']),
            bmp_str, 'raw', 'BGRX', 0, 1)
        
        # 释放资源
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hdc)
        
        # 转换为numpy数组/OpenCV格式
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return cv_img
    
    def find_template(self, template_path, threshold=0.8, region=None, multiple=False):
        """
        在屏幕上查找模板图像
        template_path: 模板图像路径
        threshold: 匹配阈值
        region: 搜索区域 (x, y, width, height)
        multiple: 是否查找多个匹配
        """
        # 截取屏幕
        screen = self.capture_screen(region)
        # 保存截图
        cv2.imwrite("screenshot.png", screen)
        
        # 读取模板图像
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise FileNotFoundError(f"找不到模板图像: {template_path}")
        
        # 模板匹配
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        
        # 获取匹配结果
        if multiple:
            locations = np.where(result >= threshold)
            if len(locations[0]) == 0:
                return None
            
            # 合并重叠的区域
            h, w = template.shape[:2]
            rectangles = []
            for point in zip(*locations[::-1]):
                rectangles.append([point[0], point[1], point[0] + w, point[1] + h])
            
            rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.5)
            
            if len(rectangles) == 0:
                return None
            
            matches = []
            for rect in rectangles:
                x1, y1, x2, y2 = rect
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                # 如果指定了区域，调整坐标
                if region:
                    center_x += region[0]
                    center_y += region[1]
                
                matches.append((center_x, center_y, result[y1, x1]))
            
            return matches
        else:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val < threshold:
                return None
            
            # 计算中心点
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            # 如果指定了区域，调整坐标
            if region:
                center_x += region[0]
                center_y += region[1]
            
            return (center_x, center_y, max_val)
    
    def find_color(self, target_color, tolerance=5, region=None, multiple=False):
        """
        在屏幕上查找特定颜色
        target_color: 目标RGB颜色元组 (R, G, B)
        tolerance: 颜色容差
        region: 搜索区域 (x, y, width, height)
        multiple: 是否查找多个匹配
        """
        # 截取屏幕
        screen = self.capture_screen(region)
        
        # 转换为BGR颜色格式(OpenCV使用BGR)
        target_bgr = (target_color[2], target_color[1], target_color[0])
        
        # 创建上下阈值
        lower = np.array([max(0, c - tolerance) for c in target_bgr])
        upper = np.array([min(255, c + tolerance) for c in target_bgr])
        
        # 创建掩码
        mask = cv2.inRange(screen, lower, upper)
        
        # 查找颜色位置
        if multiple:
            coords = np.column_stack(np.where(mask > 0))
            if len(coords) == 0:
                return None
            
            matches = []
            for coord in coords:
                y, x = coord
                
                # 如果指定了区域，调整坐标
                if region:
                    x += region[0]
                    y += region[1]
                
                matches.append((x, y))
            
            return matches
        else:
            if cv2.countNonZero(mask) == 0:
                return None
            
            # 查找第一个匹配点
            y, x = np.unravel_index(mask.argmax(), mask.shape)
            
            # 如果指定了区域，调整坐标
            if region:
                x += region[0]
                y += region[1]
            
            return (x, y)
    
    def click_position(self, position, random_offset=5, right_click=False, double_click=False):
        """
        点击指定位置
        position: (x, y) 坐标元组
        random_offset: 随机偏移量，模拟人工点击
        right_click: 是否右键点击
        double_click: 是否双击
        """
        import pyautogui
        pyautogui.FAILSAFE = False  # 禁用故障安全，慎用
        
        if not position:
            return False
        
        x, y = position[:2]  # 只取前两个值，忽略可能的置信度等其他值
        
        # 添加随机偏移
        if random_offset > 0:
            x += random.randint(-random_offset, random_offset)
            y += random.randint(-random_offset, random_offset)
        
        # 确保点击在窗口内
        client_rect = self.game_window.get_client_rect()
        x = max(0, min(x, client_rect['width']))
        y = max(0, min(y, client_rect['height']))
        
        # 将窗口客户区坐标转换为屏幕坐标
        screen_x, screen_y = self.game_window.client_to_screen(x, y)
        
        # 设置窗口为前台
        self.game_window.set_foreground()
        
        # 移动鼠标（添加人性化的移动）
        current_x, current_y = pyautogui.position()
        pyautogui.moveTo(
            screen_x, screen_y, 
            duration=self.game_window.random_delay(0.1, 0.3)
        )
        
        # 执行点击
        if right_click:
            pyautogui.rightClick()
        elif double_click:
            pyautogui.doubleClick()
        else:
            pyautogui.click()
        
        # 随机延迟
        time.sleep(self.game_window.random_delay(0.1, 0.3))
        return True 

# 如果直接运行此文件，使用以下代码进行测试
if __name__ == "__main__":
    from core.window import GameWindow
    game_window = GameWindow("PokeMMO")
    img_manager = ImageManager(game_window)
    screen = img_manager.capture_screen()
    cv2.imwrite("screenshot.png", screen)
    print("已保存截图到screenshot.png")
