import cv2
import numpy as np
import time
import os
import traceback
from paddleocr import PaddleOCR

class OCRManager:
    def __init__(self, game_window, image_manager, lang='ch'):
        """
        初始化OCR管理器
        game_window: GameWindow实例
        image_manager: ImageManager实例
        lang: 语言，'ch'为中文，'en'为英文
        """
        self.game_window = game_window
        self.image_manager = image_manager
        self.ocr = None
        self.last_result = None
        self.initialized = False
        self.lang = lang
        
        # 延迟初始化PaddleOCR以避免卡住主线程
        self._init_ocr()
    
    def _init_ocr(self):
        """初始化PaddleOCR模型"""
        try:
            print(f"正在初始化PaddleOCR({self.lang})，这可能需要一些时间...")
            self.ocr = PaddleOCR(use_angle_cls=True, lang=self.lang, show_log=False)
            self.initialized = True
            print("PaddleOCR初始化完成")
        except Exception as e:
            print(f"PaddleOCR初始化失败: {e}")
            traceback.print_exc()
            print("OCR功能将不可用")
    
    def _ensure_initialized(self):
        """确保OCR已初始化"""
        if not self.initialized and self.ocr is None:
            try:
                self._init_ocr()
            except Exception as e:
                print(f"无法初始化OCR: {e}")
                return False
        return self.initialized
    
    def recognize_text(self, region=None, threshold=0.6):
        """
        识别指定区域的文字
        region: 识别区域 (x, y, width, height)，None表示整个窗口
        threshold: 置信度阈值
        返回: [(文本, 坐标, 置信度), ...]
        """
        if not self._ensure_initialized():
            print("OCR未初始化，无法执行文本识别")
            return []
        
        try:
            # 捕获屏幕
            screen = self.image_manager.capture_screen(region)
            
            # 保存截图用于调试
            debug_dir = "debug_ocr"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            cv2.imwrite(os.path.join(debug_dir, f"ocr_input_{time.strftime('%Y%m%d_%H%M%S')}.png"), screen)
            
            # 进行OCR识别
            result = self.ocr.ocr(screen, cls=True)
            self.last_result = result
            
            # 处理识别结果
            text_results = []
            if result is not None and len(result) > 0:
                for line in result:
                    for item in line:
                        # 解析结果
                        box = item[0]  # 文字区域坐标 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                        text = item[1][0]  # 识别的文字
                        confidence = item[1][1]  # 置信度
                        
                        # 计算中心点坐标
                        center_x = int(sum(point[0] for point in box) / 4)
                        center_y = int(sum(point[1] for point in box) / 4)
                        
                        # 如果指定了区域，调整坐标
                        if region:
                            center_x += region[0]
                            center_y += region[1]
                        
                        # 过滤低置信度结果
                        if confidence >= threshold:
                            text_results.append((text, (center_x, center_y), confidence))
            
            return text_results
        
        except Exception as e:
            print(f"OCR识别失败: {e}")
            traceback.print_exc()
            return []
    
    def find_text(self, target_text, region=None, threshold=0.6, case_sensitive=False):
        """
        在屏幕上查找指定文字
        target_text: 要查找的文字
        region: 搜索区域 (x, y, width, height)
        threshold: 置信度阈值
        case_sensitive: 是否区分大小写
        返回: (center_x, center_y, confidence) 或 None
        """
        if not self._ensure_initialized():
            print("OCR未初始化，无法执行文本查找")
            return None
        
        try:
            # 识别文字
            text_results = self.recognize_text(region, threshold)
            
            # 查找匹配文字
            best_match = None
            highest_confidence = threshold
            
            for text, coords, confidence in text_results:
                # 检查文字是否匹配
                if (case_sensitive and target_text == text) or \
                   (not case_sensitive and target_text.lower() == text.lower()):
                    # 选择置信度最高的匹配
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_match = (coords[0], coords[1], confidence)
            
            return best_match
        
        except Exception as e:
            print(f"文本查找失败: {e}")
            traceback.print_exc()
            return None
    
    def click_text(self, target_text, region=None, threshold=0.6, case_sensitive=False, right_click=False):
        """
        查找并点击文字
        target_text: 要查找的文字
        region: 搜索区域 (x, y, width, height)
        threshold: 置信度阈值
        case_sensitive: 是否区分大小写
        right_click: 是否右键点击
        返回: 是否成功点击
        """
        if not self._ensure_initialized():
            print("OCR未初始化，无法执行点击文本")
            return False
        
        try:
            # 查找文字
            text_position = self.find_text(target_text, region, threshold, case_sensitive)
            
            # 如果找到文字，点击它
            if text_position:
                return self.image_manager.click_position(text_position, right_click=right_click)
            
            return False
        
        except Exception as e:
            print(f"点击文本失败: {e}")
            traceback.print_exc()
            return False
    
    def check_captcha(self, captcha_keywords=None, region=None):
        """
        检查是否出现验证码
        captcha_keywords: 验证码关键词列表，如 ["验证码", "安全验证", "captcha"]
        region: 搜索区域 (x, y, width, height)
        返回: 是否检测到验证码
        """
        if not self._ensure_initialized():
            print("OCR未初始化，无法执行验证码检查")
            return False
        
        if captcha_keywords is None:
            captcha_keywords = ["验证码", "安全验证", "验证", "captcha", "CAPTCHA", "Captcha"]
        
        try:
            # 识别文字
            text_results = self.recognize_text(region, threshold=0.6)
            
            # 检查是否包含验证码关键词
            for text, coords, confidence in text_results:
                for keyword in captcha_keywords:
                    if keyword in text:
                        print(f"检测到疑似验证码关键词: '{text}'")
                        return True
            
            return False
        
        except Exception as e:
            print(f"验证码检查失败: {e}")
            traceback.print_exc()
            return False 