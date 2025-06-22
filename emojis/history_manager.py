#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重命名历史管理工具
用于查看、清理和管理重命名历史记录
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

def load_history() -> List[Dict]:
    """加载重命名历史"""
    history_file = Path('rename_history.json')
    if not history_file.exists():
        print("❌ 未找到重命名历史文件 rename_history.json")
        return []
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 读取历史文件失败: {e}")
        return []

def save_history(history: List[Dict]):
    """保存重命名历史"""
    try:
        with open('rename_history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print("✅ 历史记录已保存")
    except Exception as e:
        print(f"❌ 保存历史文件失败: {e}")

def show_history(history: List[Dict], limit: int = None):
    """显示重命名历史"""
    if not history:
        print("📝 暂无重命名历史记录")
        return
    
    print(f"📋 重命名历史记录 (共 {len(history)} 条)")
    print("=" * 80)
    
    # 按时间倒序排列
    sorted_history = sorted(history, key=lambda x: x.get('timestamp', 0), reverse=True)
    
    if limit:
        sorted_history = sorted_history[:limit]
        print(f"显示最近 {limit} 条记录:")
    
    for i, record in enumerate(sorted_history, 1):
        timestamp = record.get('timestamp', 0)
        time_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        original = Path(record['original']).name
        new = Path(record['new']).name
        
        print(f"{i:3d}. [{time_str}]")
        print(f"     原文件: {original}")
        print(f"     新文件: {new}")
        print()

def show_statistics(history: List[Dict]):
    """显示统计信息"""
    if not history:
        print("📊 暂无统计数据")
        return
    
    print("📊 重命名统计信息")
    print("=" * 50)
    print(f"总重命名次数: {len(history)}")
    
    # 按目录统计
    dir_stats = {}
    for record in history:
        dir_path = str(Path(record['original']).parent)
        dir_stats[dir_path] = dir_stats.get(dir_path, 0) + 1
    
    print(f"涉及目录数: {len(dir_stats)}")
    print("\n各目录重命名次数:")
    for dir_path, count in sorted(dir_stats.items(), key=lambda x: x[1], reverse=True):
        dir_name = Path(dir_path).name or "根目录"
        print(f"  {dir_name}: {count} 个文件")
    
    # 时间统计
    if history:
        timestamps = [record.get('timestamp', 0) for record in history]
        earliest = min(timestamps)
        latest = max(timestamps)
        
        earliest_str = datetime.fromtimestamp(earliest).strftime('%Y-%m-%d %H:%M:%S')
        latest_str = datetime.fromtimestamp(latest).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n时间范围:")
        print(f"  最早: {earliest_str}")
        print(f"  最晚: {latest_str}")

def clean_invalid_records(history: List[Dict]) -> List[Dict]:
    """清理无效的历史记录（文件不存在）"""
    valid_records = []
    removed_count = 0
    
    for record in history:
        original_exists = Path(record['original']).exists()
        new_exists = Path(record['new']).exists()
        
        # 如果原文件和新文件都不存在，则认为是无效记录
        if not original_exists and not new_exists:
            removed_count += 1
            continue
        
        valid_records.append(record)
    
    print(f"🧹 清理完成: 移除 {removed_count} 条无效记录，保留 {len(valid_records)} 条有效记录")
    return valid_records

def clear_history():
    """清空重命名历史"""
    confirm = input("⚠️  确认要清空所有重命名历史吗？此操作不可恢复！(y/N): ").strip().lower()
    if confirm == 'y':
        save_history([])
        print("🗑️  重命名历史已清空")
    else:
        print("❌ 操作已取消")

def export_history(history: List[Dict], format_type: str = 'txt'):
    """导出重命名历史"""
    if not history:
        print("❌ 暂无历史记录可导出")
        return
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type == 'txt':
        filename = f"rename_history_export_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("重命名历史记录导出\n")
            f.write("=" * 50 + "\n\n")
            
            for i, record in enumerate(history, 1):
                time_str = datetime.fromtimestamp(record.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{i}. [{time_str}]\n")
                f.write(f"   原文件: {record['original']}\n")
                f.write(f"   新文件: {record['new']}\n\n")
        
        print(f"📄 历史记录已导出到: {filename}")
    
    elif format_type == 'csv':
        filename = f"rename_history_export_{timestamp}.csv"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("时间,原文件路径,新文件路径\n")
            for record in history:
                time_str = datetime.fromtimestamp(record.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')
                f.write(f'"{time_str}","{record["original"]}","{record["new"]}"\n')
        
        print(f"📊 历史记录已导出到: {filename}")

def main():
    parser = argparse.ArgumentParser(description='重命名历史管理工具')
    parser.add_argument('action', choices=['show', 'stats', 'clean', 'clear', 'export'], 
                       help='操作类型: show(显示历史), stats(统计信息), clean(清理无效记录), clear(清空历史), export(导出历史)')
    parser.add_argument('--limit', type=int, help='显示记录数量限制')
    parser.add_argument('--format', choices=['txt', 'csv'], default='txt', help='导出格式')
    
    args = parser.parse_args()
    
    # 加载历史记录
    history = load_history()
    
    if args.action == 'show':
        show_history(history, args.limit)
    
    elif args.action == 'stats':
        show_statistics(history)
    
    elif args.action == 'clean':
        cleaned_history = clean_invalid_records(history)
        if len(cleaned_history) != len(history):
            save_history(cleaned_history)
    
    elif args.action == 'clear':
        clear_history()
    
    elif args.action == 'export':
        export_history(history, args.format)

if __name__ == "__main__":
    main()
