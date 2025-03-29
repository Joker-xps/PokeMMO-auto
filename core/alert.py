import pygame
import time
import threading
import os
from pydub import AudioSegment
from pydub.playback import play

class AlertManager:
    def __init__(self, ocr_manager, check_interval=5):
        """
        初始化报警管理器
        ocr_manager: OCRManager实例
        check_interval: 验证码检查间隔（秒）
        """
        self.ocr_manager = ocr_manager
        self.check_interval = check_interval
        self.captcha_keywords = ["验证码", "安全验证", "验证", "captcha", "CAPTCHA", "Captcha"]
        self.alert_running = False
        self.check_thread = None
        self.stop_event = threading.Event()
        
        # 初始化声音
        pygame.mixer.init()
    
    def start_captcha_check(self, callback=None):
        """
        启动验证码检查线程
        callback: 检测到验证码时的回调函数
        """
        if self.check_thread and self.check_thread.is_alive():
            return False
        
        self.stop_event.clear()
        self.check_thread = threading.Thread(
            target=self._captcha_check_loop,
            args=(callback,)
        )
        self.check_thread.daemon = True
        self.check_thread.start()
        return True
    
    def stop_captcha_check(self):
        """停止验证码检查"""
        if self.check_thread and self.check_thread.is_alive():
            self.stop_event.set()
            self.check_thread.join(timeout=1.0)
            return True
        return False
    
    def _captcha_check_loop(self, callback=None):
        """验证码检查循环"""
        while not self.stop_event.is_set():
            try:
                # 检查验证码
                if self.ocr_manager.check_captcha(self.captcha_keywords):
                    # 播放警报声音
                    self.play_alert()
                    
                    # 调用回调函数
                    if callback:
                        callback()
                    
                    # 停止检查，等待手动处理
                    break
            except Exception as e:
                print(f"验证码检查错误: {e}")
            
            # 等待下一次检查
            # 使用短间隔轮询以便及时响应停止请求
            for _ in range(int(self.check_interval * 2)):
                if self.stop_event.is_set():
                    break
                time.sleep(0.5)
    
    def play_alert(self, sound_file=None, repeat=3):
        """
        播放警报声音
        sound_file: 声音文件路径，None表示使用默认声音
        repeat: 重复次数
        """
        if self.alert_running:
            return
        
        self.alert_running = True
        
        try:
            if sound_file and os.path.exists(sound_file):
                # 播放指定声音文件
                for _ in range(repeat):
                    if self.stop_event.is_set():
                        break
                    sound = pygame.mixer.Sound(sound_file)
                    sound.play()
                    time.sleep(1.5)  # 等待播放完成
            else:
                # 播放内置蜂鸣声
                for _ in range(repeat):
                    if self.stop_event.is_set():
                        break
                    self._play_beep()
                    time.sleep(0.5)
        finally:
            self.alert_running = False
    
    def _play_beep(self, frequency=1000, duration=500):
        """
        播放蜂鸣声
        frequency: 频率（Hz）
        duration: 持续时间（毫秒）
        """
        try:
            # 使用pydub创建一个简单的蜂鸣声
            sample_rate = 44100
            samples = sample_rate * duration // 1000
            
            # 创建一个正弦波
            beep = AudioSegment.silent(duration=duration)
            beep = beep.overlay(AudioSegment.sine(frequency, duration=duration))
            
            # 播放声音
            play(beep)
        except Exception as e:
            print(f"播放蜂鸣声失败: {e}")
            # 备用方法：使用pygame直接播放
            try:
                pygame.mixer.Sound("resources/sounds/beep.wav").play()
            except:
                pass 