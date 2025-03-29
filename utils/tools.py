import time
import random
import os
import cv2
import numpy as np
import json

def random_delay(min_time, max_time):
    """生成随机延时"""
    delay = random.uniform(min_time, max_time)
    time.sleep(delay)
    return delay

def load_config(config_path):
    """加载配置文件"""
    if not os.path.exists(config_path):
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return {}

def save_config(config, config_path):
    """保存配置文件"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False

def create_directory(directory):
    """创建目录（如果不存在）"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False

def get_all_templates(templates_dir):
    """获取所有模板图像文件"""
    templates = {}
    
    if not os.path.exists(templates_dir):
        return templates
    
    # 遍历模板目录
    for root, dirs, files in os.walk(templates_dir):
        # 计算相对路径（相对于模板目录）
        rel_path = os.path.relpath(root, templates_dir)
        if rel_path == '.':
            rel_path = ''
        
        # 处理当前目录下的所有图像文件
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                # 文件完整路径
                file_path = os.path.join(root, file)
                
                # 模板名称（不含扩展名）
                template_name = os.path.splitext(file)[0]
                
                # 如果在子目录中，添加目录名前缀
                if rel_path:
                    template_name = f"{rel_path.replace(os.path.sep, '_')}_{template_name}"
                
                templates[template_name] = file_path
    
    return templates

def save_screenshot(image, filename=None, directory='screenshots'):
    """保存截图"""
    # 创建截图目录
    create_directory(directory)
    
    # 生成文件名
    if filename is None:
        filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
    
    # 确保文件名有扩展名
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filename += '.png'
    
    # 完整路径
    filepath = os.path.join(directory, filename)
    
    # 保存图像
    try:
        cv2.imwrite(filepath, image)
        return filepath
    except Exception as e:
        print(f"保存截图失败: {e}")
        return None

def resize_image(image, width=None, height=None):
    """调整图像大小"""
    # 如果两个尺寸都没指定，返回原图
    if width is None and height is None:
        return image
    
    # 获取原始尺寸
    h, w = image.shape[:2]
    
    # 如果只指定一个尺寸，按比例计算另一个
    if width is None:
        aspect_ratio = height / h
        width = int(w * aspect_ratio)
    elif height is None:
        aspect_ratio = width / w
        height = int(h * aspect_ratio)
    
    # 调整图像大小
    resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    return resized

def crop_image(image, x, y, width, height):
    """裁剪图像"""
    # 获取图像尺寸
    h, w = image.shape[:2]
    
    # 确保裁剪区域在图像内
    x = max(0, min(x, w))
    y = max(0, min(y, h))
    width = max(1, min(width, w - x))
    height = max(1, min(height, h - y))
    
    # 裁剪图像
    cropped = image[y:y+height, x:x+width]
    return cropped

def highlight_region(image, x, y, width, height, color=(0, 255, 0), thickness=2):
    """在图像上高亮显示区域"""
    # 复制图像
    highlighted = image.copy()
    
    # 绘制矩形
    cv2.rectangle(highlighted, (x, y), (x + width, y + height), color, thickness)
    return highlighted 