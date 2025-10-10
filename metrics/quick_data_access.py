# coding: utf-8
"""
快速数据访问脚本
提供简单的命令行接口来访问测试数据
作者: Jaxon
日期: 2024-12-19
"""
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

from test_data_manager import TestDataManager

def show_help():
    """显示帮助信息"""
    print("""
📊 快速数据访问工具

用法:
  python quick_data_access.py <命令> [参数]

命令:
  list                    - 列出所有测试记录
  show <test_id>          - 显示特定测试详情
  export <format>         - 导出数据 (json/csv/excel)
  stats                   - 显示数据统计
  cleanup <days>          - 清理旧数据
  help                    - 显示此帮助信息

示例:
  python quick_data_access.py list
  python quick_data_access.py show 1
  python quick_data_access.py export json
  python quick_data_access.py stats
  python quick_data_access.py cleanup 30
""")

def list_tests():
    """列出所有测试"""
    data_manager = TestDataManager()
    all_tests = data_manager.get_all_tests()
    
    if not all_tests:
        print("⚠️ 暂无测试数据")
        return
    
    print(f"\n📋 测试记录 (共 {len(all_tests)} 条)")
    print("-" * 80)
    print(f"{'ID':<4} {'测试名称':<20} {'类型':<15} {'开始时间':<20} {'持续时间':<10} {'状态':<8}")
    print("-" * 80)
    
    for test in all_tests:
        status = "✅" if test['success'] else "❌"
        start_time = test['start_time'][:19] if len(test['start_time']) > 19 else test['start_time']
        print(f"{test['id']:<4} {test['test_name']:<20} {test['test_type']:<15} {start_time:<20} {test['duration']:<10.1f} {status:<8}")

def show_test(test_id: int):
    """显示测试详情"""
    data_manager = TestDataManager()
    test_data = data_manager.load_test_data(test_id)
    
    if not test_data:
        print(f"❌ 未找到测试ID {test_id}")
        return
    
    print(f"\n📊 测试详情 - {test_data.test_name}")
    print("=" * 60)
    print(f"测试名称: {test_data.test_name}")
    print(f"测试类型: {test_data.test_type}")
    print(f"开始时间: {test_data.start_time}")
    print(f"结束时间: {test_data.end_time}")
    print(f"持续时间: {test_data.duration:.1f} 秒")
    print(f"端口: {test_data.port}")
    print(f"成功状态: {'✅ 成功' if test_data.success else '❌ 失败'}")
    
    if test_data.error_message:
        print(f"错误信息: {test_data.error_message}")
    
    if test_data.performance_summary:
        print(f"\n📈 性能摘要:")
        for metric_name, stats in test_data.performance_summary.items():
            print(f"  {metric_name}: 数量={stats['count']}, 最小值={stats['min']:.2f}, 最大值={stats['max']:.2f}, 平均值={stats['avg']:.2f}")
    
    print(f"\n📊 原始指标数据: {len(test_data.raw_metrics)} 条")

def export_data(format_type: str):
    """导出数据"""
    data_manager = TestDataManager()
    all_tests = data_manager.get_all_tests()
    
    if not all_tests:
        print("⚠️ 暂无测试数据可导出")
        return
    
    # 获取所有测试ID
    test_ids = [test['id'] for test in all_tests]
    
    try:
        export_file = data_manager.export_test_data(test_ids, format_type)
        print(f"✅ 数据已导出到: {export_file}")
    except Exception as e:
        print(f"❌ 导出失败: {e}")

def show_stats():
    """显示数据统计"""
    data_manager = TestDataManager()
    all_tests = data_manager.get_all_tests()
    
    if not all_tests:
        print("⚠️ 暂无测试数据")
        return
    
    total_tests = len(all_tests)
    successful_tests = len([t for t in all_tests if t['success']])
    failed_tests = total_tests - successful_tests
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 数据统计")
    print("=" * 40)
    print(f"总测试数: {total_tests}")
    print(f"成功测试: {successful_tests}")
    print(f"失败测试: {failed_tests}")
    print(f"成功率: {success_rate:.1f}%")
    
    # 按测试类型统计
    test_types = {}
    for test in all_tests:
        test_type = test['test_type']
        if test_type not in test_types:
            test_types[test_type] = {'total': 0, 'success': 0}
        test_types[test_type]['total'] += 1
        if test['success']:
            test_types[test_type]['success'] += 1
    
    if test_types:
        print(f"\n📈 按测试类型统计:")
        for test_type, stats in test_types.items():
            success_rate = stats['success'] / stats['total'] * 100
            print(f"  {test_type}: {stats['total']} 次测试, 成功率 {success_rate:.1f}%")

def cleanup_data(days: int):
    """清理旧数据"""
    data_manager = TestDataManager()
    
    try:
        data_manager.cleanup_old_data(days)
        print(f"✅ 已清理 {days} 天前的数据")
    except Exception as e:
        print(f"❌ 清理失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help":
        show_help()
    elif command == "list":
        list_tests()
    elif command == "show":
        if len(sys.argv) < 3:
            print("❌ 请提供测试ID")
            return
        try:
            test_id = int(sys.argv[2])
            show_test(test_id)
        except ValueError:
            print("❌ 测试ID必须是数字")
    elif command == "export":
        format_type = sys.argv[2] if len(sys.argv) > 2 else "json"
        if format_type not in ["json", "csv", "excel"]:
            print("❌ 支持的格式: json, csv, excel")
            return
        export_data(format_type)
    elif command == "stats":
        show_stats()
    elif command == "cleanup":
        if len(sys.argv) < 3:
            print("❌ 请提供保留天数")
            return
        try:
            days = int(sys.argv[2])
            cleanup_data(days)
        except ValueError:
            print("❌ 天数必须是数字")
    else:
        print(f"❌ 未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main()
