# PokeMMO 自动化工具

这是一个用于PokeMMO游戏的自动化工具，可以帮助玩家完成一些重复性的游戏任务。

## 功能特点

- 自动化操作
- 图像识别与模板匹配
- OCR文字识别
- 鼠标键盘操作模拟
- 验证码处理
- 热键控制

## 安装

1. 确保您已安装Python 3.8或更高版本
2. 克隆或下载本仓库
3. 安装依赖项：

```
pip install -r requirements.txt
```

## 配置

本工具提供两种配置方式：

### 1. 直接编辑配置文件

您可以直接编辑`config.json`文件来修改配置。配置文件内容示例：

```json
{
    "window": {
        "name": "PokeMMO",
        "use_partial_match": true,
        "auto_foreground": true
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
        "enable": true
    },
    "hotkeys": {
        "start": "f9",
        "stop": "f10",
        "pause": "f11"
    },
    "debug": {
        "save_screenshots": true,
        "verbose_logging": false
    }
}
```

### 2. 使用配置工具

更方便的方式是使用我们提供的配置工具：

```
python configure.py
```

这个工具提供了交互式界面，可以帮助您：
- 列出系统中所有可见窗口，轻松选择游戏窗口
- 配置窗口匹配方式（精确匹配或部分匹配）
- 设置热键
- 配置OCR功能
- 调整操作延迟

## 使用方法

1. 启动PokeMMO游戏
2. 运行示例：

```
python main.py [task_name]
```

其中`task_name`可以是：
- `fishing`: 自动钓鱼
- 更多任务正在开发中...

## 热键

- F9: 开始任务
- F10: 停止任务
- F11: 暂停/继续任务

## 常见问题

### 找不到游戏窗口

如果工具无法找到游戏窗口，请尝试以下解决方案：
1. 确保游戏已经启动
2. 使用配置工具查看当前系统窗口列表，找到正确的窗口名称
3. 启用窗口部分匹配功能
4. 检查游戏是否处于全屏模式，建议使用窗口模式

### 无法控制游戏

1. 确保工具有足够的权限
2. 尝试以管理员身份运行
3. 检查是否有其他程序干扰鼠标键盘操作

## 开发者

如需开发新任务或修改现有功能，请参考`docs`目录中的开发文档。

## 许可证

本项目使用MIT许可证。请查看LICENSE文件了解详情。 
