"""
PokeMMO 自动化工具

这个项目提供了一套针对 PokeMMO 游戏的自动化操作工具，
使用计算机视觉和AI技术实现各种游戏任务的自动化。
"""

from core import GameWindow, ImageManager, OCRManager, InputManager, AlertManager
from utils import *
from main import PokeMMOAutoBot

__version__ = '0.1.0'
__author__ = 'User'
__all__ = [
    'GameWindow', 'ImageManager', 'OCRManager', 'InputManager', 'AlertManager',
    'PokeMMOAutoBot'
] 