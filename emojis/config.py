#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件 - 设置API密钥和其他参数
"""

# Gemini API配置
GEMINI_API_KEY = ""  # 请替换为你的实际API密钥
GEMINI_MODEL = "gemini-2.5-flash-lite-preview-06-17"  # 使用的模型
GEMINI_BASE_URL = "http://127.0.0.1:8889"  # 自定义API基础URL，如果使用代理请设置，例如: "https://your-proxy.com/v1"

# 处理配置
DEFAULT_DELAY = 0  # API调用间隔（秒）
MAX_IMAGE_SIZE = (1024, 1024)  # 图片最大尺寸，超过会自动缩放
MAX_FILENAME_LENGTH = 50  # 文件名最大长度

# 支持的图片格式
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

# 跳过的图片格式（这些格式的文件将被忽略，不进行重命名）
SKIP_FORMATS = {'.gif'}  # 例如：跳过GIF动图，因为可能处理效果不佳

# 跳过的文件名模式（支持通配符）
SKIP_FILENAME_PATTERNS = [
    # 'thumb*',      # 跳过缩略图
    # '*_backup.*',  # 跳过备份文件
    # 'temp_*',      # 跳过临时文件
]

# 跳过的目录名（这些目录中的文件将被忽略）
SKIP_DIRECTORIES = {
    # 'thumbnails',  # 跳过缩略图目录
    # 'backup',      # 跳过备份目录
    # 'temp',        # 跳过临时目录
    # '.git',        # 跳过git目录
}

# 提示词模板
PROMPT_TEMPLATE = """请分析这张图片的内容，并用简洁的中文描述图片的主要内容。
要求：
1. 描述要简洁明了，适合作为文件名
2. 如果是表情包或emoji，请描述表情或情绪
3. 如果是动漫角色，请描述角色特征
4. 如果是游戏截图，请描述游戏内容
5. 避免使用特殊字符，只使用中文、英文字母和数字
6. 长度控制在20个字符以内

请直接返回描述文本，不要包含其他内容。"""
