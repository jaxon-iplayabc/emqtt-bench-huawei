#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用工具函数
提供安全的数学运算和数据处理功能
作者: Jaxon
日期: 2024-12-19
"""

import os
import re
from typing import Union, Any, Optional
from pathlib import Path


def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: float = 0.0) -> float:
    """
    安全除法，避免除零错误
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 当分母为0时的默认值
        
    Returns:
        除法结果或默认值
    """
    try:
        if denominator == 0 or denominator is None:
            return default
        return float(numerator) / float(denominator)
    except (TypeError, ValueError, ZeroDivisionError):
        return default


def safe_percentage(numerator: Union[int, float], denominator: Union[int, float], default: float = 0.0) -> float:
    """
    安全计算百分比
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 当分母为0时的默认值
        
    Returns:
        百分比值 (0-100)
    """
    return safe_divide(numerator, denominator, default) * 100


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全转换为浮点数
    
    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        
    Returns:
        浮点数值
    """
    try:
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            # 移除单位和其他非数字字符
            numbers = re.findall(r'-?\d+\.?\d*', value)
            return float(numbers[0]) if numbers else default
        return default
    except (ValueError, TypeError):
        return default


def validate_file_path(file_path: Union[str, Path]) -> bool:
    """
    验证文件路径是否有效
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否有效
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except (OSError, TypeError):
        return False


def validate_url(url: str) -> bool:
    """
    验证URL是否有效
    
    Args:
        url: URL字符串
        
    Returns:
        是否有效
    """
    try:
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    except (TypeError, AttributeError):
        return False


def ensure_directory(directory: Union[str, Path]) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
        
    Returns:
        是否成功
    """
    try:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False


def clean_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(illegal_chars, '_', filename)
    
    # 限制长度
    if len(cleaned) > 255:
        cleaned = cleaned[:255]
    
    return cleaned


def format_duration(seconds: float) -> str:
    """
    格式化持续时间
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def format_bytes(bytes_value: int) -> str:
    """
    格式化字节数
    
    Args:
        bytes_value: 字节数
        
    Returns:
        格式化的字节字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f}{unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f}PB"


def safe_get_nested(data: dict, keys: list, default: Any = None) -> Any:
    """
    安全获取嵌套字典的值
    
    Args:
        data: 字典数据
        keys: 键路径列表
        default: 默认值
        
    Returns:
        值或默认值
    """
    try:
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    except (TypeError, KeyError, AttributeError):
        return default


def validate_metrics_data(metrics: dict) -> bool:
    """
    验证指标数据是否有效
    
    Args:
        metrics: 指标数据字典
        
    Returns:
        是否有效
    """
    if not isinstance(metrics, dict):
        return False
    
    # 检查是否包含基本的指标键
    basic_keys = ['connect_succ', 'connect_fail']
    return any(key in metrics for key in basic_keys)


def calculate_performance_score(success_rate: float, avg_latency: float, max_latency: float = 1000.0) -> float:
    """
    计算性能评分
    
    Args:
        success_rate: 成功率 (0-100)
        avg_latency: 平均延迟 (毫秒)
        max_latency: 最大可接受延迟 (毫秒)
        
    Returns:
        性能评分 (0-100)
    """
    # 成功率权重 60%，延迟权重 40%
    success_score = success_rate
    latency_score = max(0, 100 - (avg_latency / max_latency) * 100)
    
    return (success_score * 0.6) + (latency_score * 0.4)


def get_performance_grade(score: float) -> str:
    """
    根据评分获取性能等级
    
    Args:
        score: 性能评分 (0-100)
        
    Returns:
        性能等级 (A-F)
    """
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'
