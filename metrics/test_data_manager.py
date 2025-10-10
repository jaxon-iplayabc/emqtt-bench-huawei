# coding: utf-8
"""
测试数据管理器
用于保存和管理各个测试的数据，方便后续开发和分析
作者: Jaxon
日期: 2024-12-19
"""
import os
import json
import csv
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import pandas as pd

@dataclass
class TestData:
    """测试数据结构"""
    test_name: str
    test_type: str
    start_time: str
    end_time: str
    duration: float
    port: int
    success: bool
    error_message: Optional[str]
    metrics_file: Optional[str]
    continuous_data_file: Optional[str]
    config: Dict[str, Any]
    raw_metrics: List[Dict[str, Any]]
    performance_summary: Dict[str, Any]

class TestDataManager:
    """测试数据管理器"""
    
    def __init__(self, base_dir: str = "../test_data"):
        """
        初始化测试数据管理器
        
        Args:
            base_dir: 数据保存基础目录
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        self.metrics_dir = self.base_dir / "metrics"
        self.reports_dir = self.base_dir / "reports"
        self.raw_data_dir = self.base_dir / "raw_data"
        self.analysis_dir = self.base_dir / "analysis"
        self.database_dir = self.base_dir / "database"
        
        # 创建所有子目录
        for dir_path in [self.metrics_dir, self.reports_dir, self.raw_data_dir, 
                        self.analysis_dir, self.database_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 初始化数据库
        self.db_path = self.database_dir / "test_data.db"
        self._init_database()
    
    def _init_database(self):
        """初始化SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建测试结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                test_type TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration REAL NOT NULL,
                port INTEGER NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                metrics_file TEXT,
                continuous_data_file TEXT,
                config TEXT,
                performance_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建指标数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_result_id INTEGER,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_labels TEXT,
                timestamp TEXT NOT NULL,
                metric_type TEXT,
                help_text TEXT,
                FOREIGN KEY (test_result_id) REFERENCES test_results (id)
            )
        ''')
        
        # 创建持续数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS continuous_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_result_id INTEGER,
                timestamp TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                labels TEXT,
                FOREIGN KEY (test_result_id) REFERENCES test_results (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_test_data(self, test_data: TestData) -> str:
        """
        保存测试数据
        
        Args:
            test_data: 测试数据对象
            
        Returns:
            str: 保存的文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. 保存到数据库
        test_id = self._save_to_database(test_data)
        
        # 2. 保存原始数据到JSON文件
        json_file = self._save_raw_data(test_data, timestamp)
        
        # 3. 保存指标数据到CSV文件
        csv_file = self._save_metrics_to_csv(test_data, timestamp)
        
        # 4. 保存性能摘要
        summary_file = self._save_performance_summary(test_data, timestamp)
        
        # 5. 生成数据索引
        self._update_data_index(test_data, test_id, json_file, csv_file, summary_file)
        
        return json_file
    
    def _save_to_database(self, test_data: TestData) -> int:
        """保存到SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 插入测试结果
        cursor.execute('''
            INSERT INTO test_results (
                test_name, test_type, start_time, end_time, duration, port,
                success, error_message, metrics_file, continuous_data_file,
                config, performance_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            test_data.test_name,
            test_data.test_type,
            test_data.start_time,
            test_data.end_time,
            test_data.duration,
            test_data.port,
            test_data.success,
            test_data.error_message,
            test_data.metrics_file,
            test_data.continuous_data_file,
            json.dumps(test_data.config),
            json.dumps(test_data.performance_summary)
        ))
        
        test_id = cursor.lastrowid
        
        # 插入指标数据
        for metric in test_data.raw_metrics:
            cursor.execute('''
                INSERT INTO metrics_data (
                    test_result_id, metric_name, metric_value, metric_labels,
                    timestamp, metric_type, help_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_id,
                metric.get('name', ''),
                metric.get('value', 0),
                json.dumps(metric.get('labels', {})),
                metric.get('timestamp', ''),
                metric.get('metric_type', ''),
                metric.get('help_text', '')
            ))
        
        conn.commit()
        conn.close()
        
        return test_id
    
    def _save_raw_data(self, test_data: TestData, timestamp: str) -> str:
        """保存原始数据到JSON文件"""
        filename = f"{test_data.test_name.lower().replace(' ', '_')}_{timestamp}.json"
        filepath = self.raw_data_dir / filename
        
        # 转换为可序列化格式
        data_dict = asdict(test_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def _save_metrics_to_csv(self, test_data: TestData, timestamp: str) -> str:
        """保存指标数据到CSV文件"""
        filename = f"{test_data.test_name.lower().replace(' ', '_')}_metrics_{timestamp}.csv"
        filepath = self.metrics_dir / filename
        
        if test_data.raw_metrics:
            # 转换为DataFrame
            df = pd.DataFrame(test_data.raw_metrics)
            df.to_csv(filepath, index=False, encoding='utf-8')
        
        return str(filepath)
    
    def _save_performance_summary(self, test_data: TestData, timestamp: str) -> str:
        """保存性能摘要"""
        filename = f"{test_data.test_name.lower().replace(' ', '_')}_summary_{timestamp}.json"
        filepath = self.analysis_dir / filename
        
        summary_data = {
            'test_info': {
                'test_name': test_data.test_name,
                'test_type': test_data.test_type,
                'start_time': test_data.start_time,
                'end_time': test_data.end_time,
                'duration': test_data.duration,
                'success': test_data.success
            },
            'performance_summary': test_data.performance_summary,
            'config': test_data.config,
            'metrics_count': len(test_data.raw_metrics)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def _update_data_index(self, test_data: TestData, test_id: int, 
                          json_file: str, csv_file: str, summary_file: str):
        """更新数据索引"""
        index_file = self.base_dir / "data_index.json"
        
        # 读取现有索引
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        else:
            index_data = {'tests': [], 'last_updated': ''}
        
        # 添加新测试记录
        test_record = {
            'test_id': test_id,
            'test_name': test_data.test_name,
            'test_type': test_data.test_type,
            'timestamp': datetime.now().isoformat(),
            'success': test_data.success,
            'duration': test_data.duration,
            'files': {
                'json': json_file,
                'csv': csv_file,
                'summary': summary_file
            }
        }
        
        index_data['tests'].append(test_record)
        index_data['last_updated'] = datetime.now().isoformat()
        
        # 保存索引
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    def load_test_data(self, test_id: int) -> Optional[TestData]:
        """从数据库加载测试数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询测试结果
        cursor.execute('SELECT * FROM test_results WHERE id = ?', (test_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        # 查询指标数据
        cursor.execute('SELECT * FROM metrics_data WHERE test_result_id = ?', (test_id,))
        metrics = cursor.fetchall()
        
        conn.close()
        
        # 构建TestData对象
        test_data = TestData(
            test_name=result[1],
            test_type=result[2],
            start_time=result[3],
            end_time=result[4],
            duration=result[5],
            port=result[6],
            success=bool(result[7]),
            error_message=result[8],
            metrics_file=result[9],
            continuous_data_file=result[10],
            config=json.loads(result[11]) if result[11] else {},
            raw_metrics=[{
                'name': m[2],
                'value': m[3],
                'labels': json.loads(m[4]) if m[4] else {},
                'timestamp': m[5],
                'metric_type': m[6],
                'help_text': m[7]
            } for m in metrics],
            performance_summary=json.loads(result[12]) if result[12] else {}
        )
        
        return test_data
    
    def get_all_tests(self) -> List[Dict[str, Any]]:
        """获取所有测试记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, test_name, test_type, start_time, end_time, duration, 
                   success, port, created_at
            FROM test_results 
            ORDER BY created_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'id': r[0],
            'test_name': r[1],
            'test_type': r[2],
            'start_time': r[3],
            'end_time': r[4],
            'duration': r[5],
            'success': bool(r[6]),
            'port': r[7],
            'created_at': r[8]
        } for r in results]
    
    def export_test_data(self, test_ids: List[int], format: str = 'json') -> str:
        """
        导出测试数据
        
        Args:
            test_ids: 测试ID列表
            format: 导出格式 ('json', 'csv', 'excel')
            
        Returns:
            str: 导出文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filename = f"test_data_export_{timestamp}.json"
            filepath = self.analysis_dir / filename
            
            export_data = []
            for test_id in test_ids:
                test_data = self.load_test_data(test_id)
                if test_data:
                    export_data.append(asdict(test_data))
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            filename = f"test_data_export_{timestamp}.csv"
            filepath = self.analysis_dir / filename
            
            # 收集所有测试的基本信息
            all_tests = self.get_all_tests()
            filtered_tests = [t for t in all_tests if t['id'] in test_ids]
            
            df = pd.DataFrame(filtered_tests)
            df.to_csv(filepath, index=False, encoding='utf-8')
        
        elif format == 'excel':
            filename = f"test_data_export_{timestamp}.xlsx"
            filepath = self.analysis_dir / filename
            
            # 创建Excel文件，包含多个工作表
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 测试摘要
                all_tests = self.get_all_tests()
                filtered_tests = [t for t in all_tests if t['id'] in test_ids]
                df_summary = pd.DataFrame(filtered_tests)
                df_summary.to_excel(writer, sheet_name='Test Summary', index=False)
                
                # 每个测试的详细指标
                for test_id in test_ids:
                    test_data = self.load_test_data(test_id)
                    if test_data and test_data.raw_metrics:
                        df_metrics = pd.DataFrame(test_data.raw_metrics)
                        sheet_name = f"{test_data.test_name[:30]}"  # Excel工作表名称限制
                        df_metrics.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return str(filepath)
    
    def generate_data_report(self, report_dir: str = None) -> str:
        """生成数据报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 使用提供的report_dir或默认的analysis_dir
        target_dir = Path(report_dir) if report_dir else self.analysis_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = target_dir / f"data_report_{timestamp}.md"
        
        # 获取所有测试数据
        all_tests = self.get_all_tests()
        
        # 生成Markdown报告
        total_tests = len(all_tests)
        success_tests = len([t for t in all_tests if t['success']])
        failed_tests = len([t for t in all_tests if not t['success']])
        success_rate = (success_tests / total_tests * 100) if total_tests > 0 else 0
        
        report_content = f"""# 测试数据报告

## 数据概览

- **总测试数**: {total_tests}
- **成功测试数**: {success_tests}
- **失败测试数**: {failed_tests}
- **成功率**: {success_rate:.1f}%

## 测试类型统计

"""
        
        # 按测试类型统计
        test_types = {}
        for test in all_tests:
            test_type = test['test_type']
            if test_type not in test_types:
                test_types[test_type] = {'total': 0, 'success': 0}
            test_types[test_type]['total'] += 1
            if test['success']:
                test_types[test_type]['success'] += 1
        
        for test_type, stats in test_types.items():
            success_rate = stats['success'] / stats['total'] * 100
            report_content += f"- **{test_type}**: {stats['total']} 次测试，成功率 {success_rate:.1f}%\n"
        
        report_content += f"""
## 最近测试记录

| 测试名称 | 类型 | 开始时间 | 持续时间 | 状态 |
|---------|------|----------|----------|------|
"""
        
        # 显示最近10个测试
        recent_tests = sorted(all_tests, key=lambda x: x['created_at'], reverse=True)[:10]
        for test in recent_tests:
            status = "✅ 成功" if test['success'] else "❌ 失败"
            report_content += f"| {test['test_name']} | {test['test_type']} | {test['start_time']} | {test['duration']:.1f}s | {status} |\n"
        
        report_content += f"""
## 数据文件位置

- **原始数据**: `{self.raw_data_dir}`
- **指标数据**: `{self.metrics_dir}`
- **分析报告**: `{self.analysis_dir}`
- **数据库**: `{self.db_path}`

## 数据使用说明

1. **JSON文件**: 包含完整的测试数据，适合程序化处理
2. **CSV文件**: 包含指标数据，适合Excel分析
3. **数据库**: 支持复杂查询和数据分析
4. **索引文件**: `{self.base_dir}/data_index.json` 包含所有测试的索引信息

## 后续开发建议

1. 使用 `TestDataManager` 类加载历史数据进行分析
2. 利用数据库进行趋势分析和性能对比
3. 基于保存的配置数据重现测试环境
4. 使用持续数据文件进行时间序列分析
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_file)
    
    def cleanup_old_data(self, days: int = 30):
        """清理旧数据"""
        import time
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        # 清理文件
        for dir_path in [self.raw_data_dir, self.metrics_dir, self.analysis_dir]:
            for file_path in dir_path.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
        
        # 清理数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM test_results WHERE created_at < ?', 
                      (datetime.fromtimestamp(cutoff_time).isoformat(),))
        conn.commit()
        conn.close()
        
        print(f"已清理 {days} 天前的数据")
