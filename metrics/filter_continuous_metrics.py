#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持续指标文件过滤器
专门用于过滤持续指标文件中的无效数据
作者: Jaxon
日期: 2025-01-01
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from test_specific_filter import TestSpecificFilter
from rich.console import Console

console = Console()

def main():
    """主函数"""
    console.print("持续指标文件过滤器")
    console.print("=" * 50)
    console.print("此工具将自动过滤持续指标文件中的无效数据")
    console.print("根据测试类型智能过滤，例如：")
    console.print("  • 连接测试中移除pub相关指标")
    console.print("  • 发布测试中移除sub相关指标")
    console.print("  • 订阅测试中移除pub相关指标")
    console.print("  • 广播测试中移除无意义指标")
    console.print("")
    
    # 自动继续操作（非交互式）
    console.print("自动开始过滤操作...")
    
    # 创建过滤器实例
    test_filter = TestSpecificFilter()
    
    # 自动过滤所有持续指标文件
    console.print("开始扫描持续指标文件...")
    filtered_files = test_filter.auto_filter_all_continuous_files("metrics/reports")
    
    if filtered_files:
        console.print("过滤完成！")
        console.print("处理结果:")
        console.print(f"  • 成功处理文件数: {len(filtered_files)}")
        console.print("  • 过滤后文件保存在: metrics/reports/filtered/")
        console.print("")
        console.print("过滤后的文件列表:")
        for file_path in filtered_files:
            console.print(f"  • {os.path.basename(file_path)}")
        
        console.print("")
        console.print("所有持续指标文件已成功过滤！")
        console.print("提示: 过滤后的文件保留了关键性能指标，移除了无效数据")
    else:
        console.print("没有找到需要过滤的持续指标文件")
        console.print("请确保以下位置存在持续指标文件:")
        console.print("  • metrics/reports/continuous_metrics_*.json")

if __name__ == "__main__":
    main()
