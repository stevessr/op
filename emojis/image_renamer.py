#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片重命名工具 - 使用Gemini API识别图片内容并重命名
"""

import os
import sys
import time
import json
import logging
import requests
import fnmatch
from pathlib import Path
from typing import List, Dict, Optional
import google.generativeai as genai
from PIL import Image
import argparse
import base64
import io

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_renamer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImageRenamer:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp", base_url: Optional[str] = None,
                 supported_formats: set = None, skip_formats: set = None,
                 skip_patterns: list = None, skip_directories: set = None):
        """
        初始化图片重命名器

        Args:
            api_key: Gemini API密钥
            model_name: 使用的模型名称
            base_url: 自定义API基础URL，用于代理或其他端点
            supported_formats: 支持的图片格式
            skip_formats: 跳过的图片格式
            skip_patterns: 跳过的文件名模式
            skip_directories: 跳过的目录名
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url
        self.setup_gemini()

        # 图片格式配置
        self.supported_formats = supported_formats or {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        self.skip_formats = skip_formats or set()
        self.skip_patterns = skip_patterns or []
        self.skip_directories = skip_directories or set()

        # 重命名历史记录
        self.rename_history = []
        self.processed_files = set()  # 已处理文件的集合
        self.load_rename_history()
        
    def setup_gemini(self):
        """配置Gemini API"""
        try:
            # 配置API密钥
            genai.configure(api_key=self.api_key)

            # 如果设置了自定义base_url，修改环境变量或使用其他方法
            if self.base_url:
                # 设置环境变量来覆盖默认端点
                import os
                os.environ['GOOGLE_AI_STUDIO_API_ENDPOINT'] = self.base_url
                logger.info(f"设置自定义API端点: {self.base_url}")

            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"成功配置Gemini API，使用模型: {self.model_name}")

        except Exception as e:
            logger.error(f"配置Gemini API失败: {e}")
            raise
    
    def is_image_file(self, file_path: Path) -> bool:
        """检查文件是否为支持的图片格式"""
        return file_path.suffix.lower() in self.supported_formats

    def should_skip_file(self, file_path: Path) -> tuple[bool, str]:
        """
        检查文件是否应该跳过

        Args:
            file_path: 文件路径

        Returns:
            (是否跳过, 跳过原因)
        """
        # 检查文件格式是否在跳过列表中
        if file_path.suffix.lower() in self.skip_formats:
            return True, f"跳过格式: {file_path.suffix}"

        # 检查文件名是否匹配跳过模式
        for pattern in self.skip_patterns:
            if fnmatch.fnmatch(file_path.name.lower(), pattern.lower()):
                return True, f"匹配跳过模式: {pattern}"

        # 检查是否在跳过的目录中
        for part in file_path.parts:
            if part.lower() in {d.lower() for d in self.skip_directories}:
                return True, f"在跳过目录中: {part}"

        return False, ""
    
    def get_all_images(self, root_dir: str) -> List[Path]:
        """获取指定目录及其子目录中的所有图片文件"""
        root_path = Path(root_dir)
        images = []
        skipped_files = []

        for file_path in root_path.rglob('*'):
            if file_path.is_file() and self.is_image_file(file_path):
                # 检查是否应该跳过
                should_skip, skip_reason = self.should_skip_file(file_path)
                if should_skip:
                    skipped_files.append((file_path, skip_reason))
                    continue

                images.append(file_path)

        logger.info(f"找到 {len(images)} 个图片文件")
        if skipped_files:
            logger.info(f"跳过 {len(skipped_files)} 个文件:")
            for file_path, reason in skipped_files[:10]:  # 只显示前10个
                logger.info(f"  - {file_path.name}: {reason}")
            if len(skipped_files) > 10:
                logger.info(f"  ... 还有 {len(skipped_files) - 10} 个文件被跳过")

        return images
    
    def analyze_image(self, image_path: Path) -> Optional[str]:
        """
        使用Gemini API分析图片内容

        Args:
            image_path: 图片文件路径

        Returns:
            图片描述文本，如果失败返回None
        """
        try:
            # 如果使用自定义URL，使用直接HTTP请求
            if self.base_url:
                return self._analyze_image_with_custom_url(image_path)
            else:
                return self._analyze_image_with_official_api(image_path)

        except Exception as e:
            logger.error(f"分析图片失败 {image_path}: {e}")
            return None

    def _analyze_image_with_official_api(self, image_path: Path) -> Optional[str]:
        """使用官方API分析图片"""
        # 打开并处理图片
        with Image.open(image_path) as img:
            # 如果图片太大，调整大小以节省API调用成本
            max_size = (1024, 1024)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # 构建提示词
            prompt = """请分析这张图片的内容，并用简洁的中文描述图片的主要内容。
            要求：
            1. 描述要简洁明了，适合作为文件名
            2. 如果是表情包或emoji，请描述表情或情绪
            3. 如果是动漫角色，请描述角色特征
            4. 如果是游戏截图，请描述游戏内容
            5. 避免使用特殊字符，只使用中文、英文字母和数字
            6. 长度控制在20个字符以内

            请直接返回描述文本，不要包含其他内容。"""

            # 调用Gemini API
            response = self.model.generate_content([prompt, img])

            if response.text:
                # 清理描述文本，移除不适合文件名的字符
                description = self.clean_filename(response.text.strip())
                logger.info(f"图片 {image_path.name} 分析结果: {description}")
                return description
            else:
                logger.warning(f"API返回空结果: {image_path}")
                return None

    def _analyze_image_with_custom_url(self, image_path: Path) -> Optional[str]:
        """使用自定义URL分析图片"""
        # 读取并编码图片
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # 转换为base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 获取图片MIME类型
        mime_type = f"image/{image_path.suffix[1:].lower()}"
        if mime_type == "image/jpg":
            mime_type = "image/jpeg"

        # 构建请求数据
        prompt = """请分析这张图片的内容，并用简洁的中文描述图片的主要内容。
        要求：
        1. 描述要简洁明了，适合作为文件名
        2. 如果是表情包或emoji，请描述表情或情绪
        3. 如果是动漫角色，请描述角色特征
        4. 如果是游戏截图，请描述游戏内容
        5. 避免使用特殊字符，只使用中文、英文字母和数字
        6. 长度控制在20个字符以内

        请直接返回描述文本，不要包含其他内容。"""

        # 构建请求体（兼容多种API格式）
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_base64
                        }
                    }
                ]
            }]
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        # 构建URL
        url = f"{self.base_url.rstrip('/')}/v1beta/models/{self.model_name}:generateContent"

        # 发送请求
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0].get('content', {})
                parts = content.get('parts', [])
                if parts and 'text' in parts[0]:
                    text = parts[0]['text'].strip()
                    description = self.clean_filename(text)
                    logger.info(f"图片 {image_path.name} 分析结果: {description}")
                    return description

        logger.warning(f"自定义API返回错误: {response.status_code} - {response.text}")
        return None
    
    def clean_filename(self, text: str) -> str:
        """清理文件名，移除不合法字符"""
        # 移除或替换不合法的文件名字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            text = text.replace(char, '')
        
        # 移除多余的空格和换行
        text = ' '.join(text.split())
        
        # 限制长度
        if len(text) > 50:
            text = text[:50]
        
        return text.strip()
    
    def generate_new_filename(self, original_path: Path, description: str) -> str:
        """
        生成新的文件名
        
        Args:
            original_path: 原始文件路径
            description: 图片描述
            
        Returns:
            新的文件名
        """
        # 获取原始文件扩展名
        extension = original_path.suffix
        
        # 如果描述为空，使用原始文件名
        if not description:
            return original_path.name
        
        # 生成新文件名
        new_name = f"{description}{extension}"
        
        # 检查是否与原文件名相同
        if new_name == original_path.name:
            return original_path.name
        
        return new_name
    
    def rename_image(self, image_path: Path, new_name: str, dry_run: bool = False) -> bool:
        """
        重命名图片文件
        
        Args:
            image_path: 原始图片路径
            new_name: 新文件名
            dry_run: 是否为试运行模式
            
        Returns:
            是否成功重命名
        """
        try:
            new_path = image_path.parent / new_name
            
            # 检查新文件名是否已存在
            if new_path.exists() and new_path != image_path:
                # 添加数字后缀避免冲突
                base_name = new_path.stem
                extension = new_path.suffix
                counter = 1
                
                while new_path.exists():
                    new_name_with_counter = f"{base_name}_{counter}{extension}"
                    new_path = image_path.parent / new_name_with_counter
                    counter += 1
                
                new_name = new_path.name
            
            if dry_run:
                logger.info(f"[试运行] {image_path.name} -> {new_name}")
                return True
            else:
                # 执行重命名
                image_path.rename(new_path)
                logger.info(f"重命名成功: {image_path.name} -> {new_name}")
                
                # 记录重命名历史
                rename_record = {
                    'original': str(image_path),
                    'new': str(new_path),
                    'timestamp': time.time()
                }
                self.rename_history.append(rename_record)

                # 更新已处理文件集合
                self.processed_files.add(str(image_path.resolve()))
                self.processed_files.add(str(new_path.resolve()))

                return True
                
        except Exception as e:
            logger.error(f"重命名失败 {image_path}: {e}")
            return False
    
    def process_directory(self, directory: str, dry_run: bool = False,
                         max_files: Optional[int] = None, delay: float = 1.0,
                         force_reprocess: bool = False):
        """
        处理目录中的所有图片

        Args:
            directory: 目录路径
            dry_run: 是否为试运行模式
            max_files: 最大处理文件数量
            delay: API调用间隔（秒）
            force_reprocess: 是否强制重新处理已处理过的文件
        """
        logger.info(f"开始处理目录: {directory}")
        logger.info(f"试运行模式: {dry_run}")
        
        # 获取所有图片文件
        images = self.get_all_images(directory)
        
        if max_files:
            images = images[:max_files]
            logger.info(f"限制处理文件数量: {max_files}")
        
        success_count = 0
        error_count = 0
        skipped_count = 0

        for i, image_path in enumerate(images, 1):
            logger.info(f"处理进度: {i}/{len(images)} - {image_path.name}")

            try:
                # 检查文件是否已经被处理过（除非强制重新处理）
                if not force_reprocess and self.is_file_processed(image_path):
                    logger.info(f"跳过文件（已处理过）: {image_path.name}")
                    skipped_count += 1
                    continue

                # 分析图片内容
                description = self.analyze_image(image_path)

                if description:
                    # 生成新文件名
                    new_name = self.generate_new_filename(image_path, description)

                    # 检查是否需要重命名（文件名是否有变化）
                    if new_name == image_path.name:
                        logger.info(f"跳过文件（文件名无需更改）: {image_path.name}")
                        skipped_count += 1
                        continue

                    # 重命名文件
                    if self.rename_image(image_path, new_name, dry_run):
                        success_count += 1
                    else:
                        error_count += 1
                else:
                    logger.warning(f"跳过文件（无法分析）: {image_path.name}")
                    error_count += 1
                
                # API调用间隔
                if delay > 0 and i < len(images):
                    time.sleep(delay)
                    
            except KeyboardInterrupt:
                logger.info("用户中断处理")
                break
            except Exception as e:
                logger.error(f"处理文件时出错 {image_path}: {e}")
                error_count += 1
        
        logger.info(f"处理完成! 成功: {success_count}, 失败: {error_count}, 跳过: {skipped_count}")

        # 保存重命名历史
        if not dry_run and self.rename_history:
            self.save_rename_history()
    
    def load_rename_history(self):
        """加载重命名历史记录"""
        try:
            history_file = Path('rename_history.json')
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.rename_history = json.load(f)

                # 构建已处理文件集合
                for record in self.rename_history:
                    # 添加原始文件路径（标准化路径）
                    original_path = Path(record['original']).resolve()
                    self.processed_files.add(str(original_path))

                    # 添加重命名后的文件路径
                    new_path = Path(record['new']).resolve()
                    self.processed_files.add(str(new_path))

                logger.info(f"加载重命名历史: {len(self.rename_history)} 条记录")
                logger.info(f"已处理文件数量: {len(self.processed_files)}")
            else:
                logger.info("未找到重命名历史文件，将创建新的历史记录")
        except Exception as e:
            logger.error(f"加载重命名历史失败: {e}")
            self.rename_history = []
            self.processed_files = set()

    def is_file_processed(self, file_path: Path) -> bool:
        """检查文件是否已经被处理过"""
        try:
            # 标准化文件路径
            normalized_path = str(file_path.resolve())
            return normalized_path in self.processed_files
        except Exception as e:
            logger.warning(f"检查文件处理状态失败 {file_path}: {e}")
            return False

    def save_rename_history(self):
        """保存重命名历史记录"""
        try:
            history_file = Path('rename_history.json')
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.rename_history, f, ensure_ascii=False, indent=2)
            logger.info(f"重命名历史已保存到: {history_file}")
        except Exception as e:
            logger.error(f"保存重命名历史失败: {e}")

def main():
    parser = argparse.ArgumentParser(description='使用Gemini API识别图片内容并重命名')
    parser.add_argument('directory', help='要处理的目录路径')
    parser.add_argument('--api-key', required=True, help='Gemini API密钥')
    parser.add_argument('--model', default='gemini-2.0-flash-exp', help='使用的模型名称')
    parser.add_argument('--base-url', help='自定义API基础URL，用于代理或其他端点')
    parser.add_argument('--dry-run', action='store_true', help='试运行模式，不实际重命名')
    parser.add_argument('--max-files', type=int, help='最大处理文件数量')
    parser.add_argument('--delay', type=float, default=1.0, help='API调用间隔（秒）')
    parser.add_argument('--force-reprocess', action='store_true', help='强制重新处理已处理过的文件')
    parser.add_argument('--skip-formats', nargs='*', help='跳过的图片格式，如: --skip-formats .gif .svg')
    parser.add_argument('--skip-patterns', nargs='*', help='跳过的文件名模式，如: --skip-patterns thumb* *_backup.*')
    parser.add_argument('--skip-dirs', nargs='*', help='跳过的目录名，如: --skip-dirs thumbnails backup')
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.exists(args.directory):
        logger.error(f"目录不存在: {args.directory}")
        sys.exit(1)
    
    try:
        # 准备跳过配置
        skip_formats = set(args.skip_formats) if args.skip_formats else set()
        skip_patterns = args.skip_patterns or []
        skip_directories = set(args.skip_dirs) if args.skip_dirs else set()

        # 创建重命名器实例
        renamer = ImageRenamer(
            args.api_key,
            args.model,
            args.base_url,
            skip_formats=skip_formats,
            skip_patterns=skip_patterns,
            skip_directories=skip_directories
        )

        # 处理目录
        renamer.process_directory(
            args.directory,
            dry_run=args.dry_run,
            max_files=args.max_files,
            delay=args.delay,
            force_reprocess=args.force_reprocess
        )
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
