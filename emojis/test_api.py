#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连接测试脚本
用于测试Gemini API连接是否正常，包括自定义URL
"""

import sys
import argparse
from pathlib import Path
from image_renamer import ImageRenamer
import config

def test_api_connection(api_key: str, model: str = "gemini-2.0-flash-exp", base_url: str = None):
    """测试API连接"""
    print("🔍 测试API连接...")
    print(f"模型: {model}")
    if base_url:
        print(f"自定义URL: {base_url}")
    else:
        print("使用官方API端点")
    
    try:
        # 创建重命名器实例
        renamer = ImageRenamer(api_key, model, base_url)
        print("✅ API配置成功")
        
        # 查找测试图片
        current_dir = Path('.')
        test_images = []
        
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            test_images.extend(list(current_dir.glob(f'*{ext}')))
            test_images.extend(list(current_dir.glob(f'**/*{ext}')))
            if len(test_images) >= 1:
                break
        
        if not test_images:
            print("⚠️  未找到测试图片，请在当前目录放置一张图片进行测试")
            return False
        
        # 测试第一张图片
        test_image = test_images[0]
        print(f"📸 测试图片: {test_image.name}")
        
        description = renamer.analyze_image(test_image)
        
        if description:
            print(f"✅ API测试成功!")
            print(f"图片描述: {description}")
            return True
        else:
            print("❌ API测试失败: 未获得有效响应")
            return False
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='测试Gemini API连接')
    parser.add_argument('--api-key', help='Gemini API密钥 (如果不提供，将使用config.py中的配置)')
    parser.add_argument('--model', default='gemini-2.0-flash-exp', help='使用的模型名称')
    parser.add_argument('--base-url', help='自定义API基础URL')
    
    args = parser.parse_args()
    
    # 获取API密钥
    api_key = args.api_key
    if not api_key:
        if hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY != "YOUR_API_KEY_HERE":
            api_key = config.GEMINI_API_KEY
            print("📋 使用config.py中的API密钥")
        else:
            print("❌ 请提供API密钥:")
            print("1. 使用 --api-key 参数")
            print("2. 或在config.py中配置GEMINI_API_KEY")
            sys.exit(1)
    
    # 获取base_url
    base_url = args.base_url
    if not base_url and hasattr(config, 'GEMINI_BASE_URL'):
        base_url = config.GEMINI_BASE_URL
        if base_url:
            print("📋 使用config.py中的自定义URL")
    
    # 执行测试
    success = test_api_connection(api_key, args.model, base_url)
    
    if success:
        print("\n🎉 API连接测试通过！可以开始使用图片重命名功能。")
        sys.exit(0)
    else:
        print("\n💡 故障排除建议:")
        print("1. 检查API密钥是否正确")
        print("2. 检查网络连接")
        print("3. 如果使用代理，检查代理URL是否正确")
        print("4. 检查API配额是否充足")
        sys.exit(1)

if __name__ == "__main__":
    main()
