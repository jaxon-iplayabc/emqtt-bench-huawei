#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Filter Test Script
Test the data filtering functionality in main.py
Author: Jaxon
Date: 2024-12-19
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import AutoDataCollector
from rich.console import Console

console = Console()

def test_data_filter():
    """Test data filtering functionality"""
    console.print("🧪 [bold blue]Data Filter Test[/bold blue]")
    console.print("=" * 60)
    
    # Create data collector instance
    collector = AutoDataCollector()
    
    # Test data directory
    test_data_dir = "test_data/raw_data"
    
    if not os.path.exists(test_data_dir):
        console.print(f"[red]❌ Test data directory not found: {test_data_dir}[/red]")
        return
    
    # Find test files
    test_files = [f for f in os.listdir(test_data_dir) if f.endswith('.json')]
    
    if not test_files:
        console.print(f"[yellow]⚠️ No test files found in {test_data_dir}[/yellow]")
        return
    
    console.print(f"[cyan]📁 Found {len(test_files)} test files[/cyan]")
    
    # Select first file for testing
    test_file = test_files[0]
    file_path = os.path.join(test_data_dir, test_file)
    
    console.print(f"[blue]🔍 Test file: {test_file}[/blue]")
    
    try:
        # Read test data
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        test_name = data.get('test_name', 'Unknown')
        raw_metrics = data.get('raw_metrics', [])
        
        console.print(f"[green]📊 Original data statistics:[/green]")
        console.print(f"[dim]  • Test name: {test_name}[/dim]")
        console.print(f"[dim]  • Original metrics count: {len(raw_metrics)}[/dim]")
        
        # Analyze original data
        zero_value_count = sum(1 for metric in raw_metrics if metric.get('value', 0) == 0)
        erlang_vm_count = sum(1 for metric in raw_metrics if metric.get('name', '').startswith('erlang_vm_'))
        
        console.print(f"[dim]  • Zero value metrics: {zero_value_count}[/dim]")
        console.print(f"[dim]  • Erlang VM metrics: {erlang_vm_count}[/dim]")
        
        # Execute data filtering
        console.print(f"\n[blue]🔍 Starting data filtering test...[/blue]")
        filtered_metrics = collector._filter_invalid_metrics(raw_metrics, test_name)
        
        # Analyze filtering results
        original_count = len(raw_metrics)
        filtered_count = len(filtered_metrics)
        removed_count = original_count - filtered_count
        reduction_percent = (removed_count / original_count * 100) if original_count > 0 else 0
        
        console.print(f"\n[green]📊 Filtering results:[/green]")
        console.print(f"[dim]  • Original metrics count: {original_count}[/dim]")
        console.print(f"[dim]  • Filtered metrics count: {filtered_count}[/dim]")
        console.print(f"[dim]  • Removed metrics count: {removed_count}[/dim]")
        console.print(f"[dim]  • Data reduction percentage: {reduction_percent:.1f}%[/dim]")
        
        # Analyze retained metric types
        retained_metrics = {}
        for metric in filtered_metrics:
            name = metric.get('name', '')
            if name not in retained_metrics:
                retained_metrics[name] = 0
            retained_metrics[name] += 1
        
        console.print(f"\n[cyan]📋 Retained metric types (top 10):[/cyan]")
        sorted_metrics = sorted(retained_metrics.items(), key=lambda x: x[1], reverse=True)
        for i, (name, count) in enumerate(sorted_metrics[:10], 1):
            console.print(f"[dim]  {i:2d}. {name}: {count} items[/dim]")
        
        # Test saving filtered data
        console.print(f"\n[blue]💾 Testing saving filtered data...[/blue]")
        
        # Create mock TestResult object
        class MockTestResult:
            def __init__(self, test_name, start_time, end_time, duration, port, success, error_message):
                self.test_name = test_name
                self.start_time = start_time
                self.end_time = end_time
                self.duration = duration
                self.port = port
                self.success = success
                self.error_message = error_message
        
        mock_result = MockTestResult(
            test_name=test_name,
            start_time=datetime.fromisoformat(data.get('start_time', '2024-01-01T00:00:00')),
            end_time=datetime.fromisoformat(data.get('end_time', '2024-01-01T00:01:00')),
            duration=data.get('duration', 60),
            port=data.get('port', 9090),
            success=data.get('success', True),
            error_message=data.get('error_message', None)
        )
        
        # Save filtered data
        filtered_file = collector._save_filtered_data(mock_result, filtered_metrics)
        
        if filtered_file:
            console.print(f"[green]✅ Filtered data saved: {filtered_file}[/green]")
            
            # Verify saved file
            if os.path.exists(filtered_file):
                with open(filtered_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                console.print(f"[cyan]📄 Saved file verification:[/cyan]")
                console.print(f"[dim]  • File size: {os.path.getsize(filtered_file)} bytes[/dim]")
                console.print(f"[dim]  • Filtered metrics count: {len(saved_data.get('filtered_metrics', []))}[/dim]")
                console.print(f"[dim]  • Filter info: {saved_data.get('filter_info', {})}[/dim]")
            else:
                console.print(f"[red]❌ Saved file does not exist: {filtered_file}[/red]")
        else:
            console.print(f"[red]❌ Failed to save filtered data[/red]")
        
        console.print(f"\n[green]🎉 Data filtering test completed![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Test failed: {e}[/red]")
        import traceback
        console.print(f"[dim]Detailed error info: {traceback.format_exc()}[/dim]")

if __name__ == "__main__":
    test_data_filter()
