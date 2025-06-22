#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版图片重命名脚本
使用config.py中的配置，更容易使用
"""

import os
import sys
from pathlib import Path
from image_renamer_pool import ImageRenamer
import config

def main():
    # 检查API密钥是否已配置
    if config.GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        print("❌ 请先在config.py文件中设置你的Gemini API密钥！")
        print("1. 访问 https://makersuite.google.com/app/apikey 获取API密钥")
        print("2. 编辑config.py文件，将YOUR_API_KEY_HERE替换为你的实际API密钥")
        sys.exit(1)
    
    # 获取当前目录
    current_dir = os.getcwd()
    print(f"📁 当前工作目录: {current_dir}")
    
    # 询问用户选择
    print("\n请选择操作模式:")
    print("1. 试运行模式 (推荐) - 只预览重命名结果，不实际重命名")
    print("2. 实际重命名模式 - 真正重命名文件")
    print("3. 退出")
    
    while True:
        choice = input("\n请输入选择 (1/2/3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("❌ 无效选择，请输入1、2或3")
    
    if choice == '3':
        print("👋 再见！")
        sys.exit(0)
    
    dry_run = (choice == '1')
    mode_text = "试运行模式" if dry_run else "实际重命名模式"
    print(f"\n✅ 已选择: {mode_text}")
    
    # 询问处理文件数量限制
    print(f"\n是否限制处理文件数量？(建议首次使用时限制为10-20个文件进行测试)")
    limit_choice = input("输入最大文件数量，或按回车不限制: ").strip()

    max_files = None
    if limit_choice.isdigit():
        max_files = int(limit_choice)
        print(f"✅ 将最多处理 {max_files} 个文件")
    else:
        print("✅ 不限制文件数量")

    # 询问是否重新处理已处理过的文件
    force_reprocess = False
    print(f"\n是否重新处理已经重命名过的文件？")
    print("(程序会自动跳过已处理过的文件，除非选择强制重新处理)")
    reprocess_choice = input("是否强制重新处理？(y/N): ").strip().lower()
    if reprocess_choice == 'y':
        force_reprocess = True
        print("✅ 将重新处理所有文件")
    else:
        print("✅ 将跳过已处理过的文件")
    
    # 确认开始处理
    if dry_run:
        print(f"\n🔍 即将开始试运行，预览重命名结果...")
    else:
        print(f"\n⚠️  即将开始实际重命名文件！")
        confirm = input("确认继续吗？(y/N): ").strip().lower()
        if confirm != 'y':
            print("👋 操作已取消")
            sys.exit(0)
    
    try:
        # 创建重命名器
        print(f"\n🚀 正在初始化Gemini API...")
        base_url = getattr(config, 'GEMINI_BASE_URL', None)
        if base_url:
            print(f"🔗 使用自定义API端点: {base_url}")

        # 获取跳过配置
        supported_formats = getattr(config, 'SUPPORTED_FORMATS', {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'})
        skip_formats = getattr(config, 'SKIP_FORMATS', set())
        skip_patterns = getattr(config, 'SKIP_FILENAME_PATTERNS', [])
        skip_directories = getattr(config, 'SKIP_DIRECTORIES', set())

        # 显示跳过配置
        if skip_formats:
            print(f"⏭️  将跳过格式: {', '.join(skip_formats)}")
        if skip_patterns:
            print(f"⏭️  将跳过文件模式: {', '.join(skip_patterns)}")
        if skip_directories:
            print(f"⏭️  将跳过目录: {', '.join(skip_directories)}")

        renamer = ImageRenamer(
            config.GEMINI_API_KEY,
            config.GEMINI_MODEL,
            base_url,
            supported_formats=supported_formats,
            skip_formats=skip_formats,
            skip_patterns=skip_patterns,
            skip_directories=skip_directories
        )

        # 开始处理
        print(f"📸 开始处理图片文件...")
        renamer.process_directory(
            current_dir,
            dry_run=dry_run,
            max_files=max_files,
            delay=config.DEFAULT_DELAY,
            force_reprocess=force_reprocess
        )
        
        if dry_run:
            print(f"\n✅ 试运行完成！如果结果满意，可以选择实际重命名模式。")
        else:
            print(f"\n✅ 重命名完成！重命名历史已保存到 rename_history.json")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print(f"详细错误信息请查看 image_renamer.log 文件")

if __name__ == "__main__":
    main()
