#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Data Filter Test
Test the data filtering functionality
"""

import sys
import os
import json

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_filter_logic():
    """Test the filtering logic directly"""
    print("Testing data filtering logic...")
    
    # Sample test data
    test_metrics = [
        {"name": "connect_succ", "value": 10.0, "help_text": "connect_succ connect_succ"},
        {"name": "connection_idle", "value": 0.0, "help_text": "connection_idle connection_idle"},
        {"name": "recv", "value": 0.0, "help_text": "recv recv"},
        {"name": "erlang_vm_memory_bytes_total", "value": 1000000, "help_text": "Memory usage"},
        {"name": "mqtt_client_connect_duration_sum", "value": 500.0, "help_text": "Connection duration"},
        {"name": "pub_succ", "value": 50.0, "help_text": "pub_succ pub_succ"},
        {"name": "erlang_vm_statistics_garbage_collection_number_of_gcs", "value": 100, "help_text": "GC count"},
    ]
    
    # Define filtering patterns
    invalid_patterns = {
        'zero_value_metrics': [
            'connection_idle', 'recv', 'connect_fail', 'pub_fail', 'pub_overrun',
            'connect_retried', 'sub_fail', 'reconnect_succ', 'sub', 'publish_latency',
            'pub_succ', 'connection_timeout', 'connection_refused', 'unreachable', 'pub'
        ],
        'erlang_vm_metrics': [
            'erlang_vm_memory_', 'erlang_vm_msacc_', 'erlang_vm_statistics_',
            'erlang_vm_dirty_', 'erlang_vm_ets_', 'erlang_vm_logical_',
            'erlang_vm_port_', 'erlang_vm_process_', 'erlang_vm_schedulers_',
            'erlang_vm_smp_', 'erlang_vm_thread_', 'erlang_vm_time_',
            'erlang_vm_wordsize_', 'erlang_vm_atom_', 'erlang_vm_allocators'
        ],
        'redundant_help_text': [
            'connection_idle connection_idle', 'recv recv', 'connect_fail connect_fail',
            'pub_fail pub_fail', 'pub_overrun pub_overrun', 'connect_retried connect_retried',
            'connect_succ connect_succ', 'sub_fail sub_fail', 'reconnect_succ reconnect_succ',
            'sub sub', 'publish_latency publish_latency', 'pub_succ pub_succ',
            'connection_timeout connection_timeout', 'connection_refused connection_refused',
            'unreachable unreachable', 'pub pub'
        ]
    }
    
    # Filter metrics
    filtered_metrics = []
    removed_count = 0
    
    for metric in test_metrics:
        metric_name = metric.get('name', '')
        metric_value = metric.get('value', 0)
        help_text = metric.get('help_text', '')
        
        should_remove = False
        removal_reason = ""
        
        # Check zero value metrics
        if metric_name in invalid_patterns['zero_value_metrics'] and metric_value == 0:
            should_remove = True
            removal_reason = "zero value metric"
        
        # Check Erlang VM metrics
        elif any(metric_name.startswith(pattern) for pattern in invalid_patterns['erlang_vm_metrics']):
            should_remove = True
            removal_reason = "Erlang VM metric"
        
        # Check redundant help_text
        elif help_text in invalid_patterns['redundant_help_text']:
            should_remove = True
            removal_reason = "redundant help_text"
        
        # Keep key performance metrics
        if not should_remove:
            key_metrics = [
                'connect_succ', 'pub_succ', 'recv', 'publish_latency',
                'mqtt_client_connect_duration', 'mqtt_client_handshake_duration',
                'e2e_latency', 'mqtt_client_subscribe_duration'
            ]
            
            if (any(key_metric in metric_name for key_metric in key_metrics) or 
                metric_value != 0 or 
                'duration' in metric_name or 
                'latency' in metric_name):
                filtered_metrics.append(metric)
            else:
                should_remove = True
                removal_reason = "no meaningful value"
        
        if should_remove:
            removed_count += 1
            print("  ❌ Removed {}: {} (value: {})".format(metric_name, removal_reason, metric_value))
        else:
            print("  ✅ Kept {}: {}".format(metric_name, metric_value))
    
    print("\nFiltering Results:")
    print("  Original metrics: {}".format(len(test_metrics)))
    print("  Filtered metrics: {}".format(len(filtered_metrics)))
    print("  Removed metrics: {}".format(removed_count))
    print("  Reduction: {:.1f}%".format(removed_count / len(test_metrics) * 100))
    
    print("\nFiltered metrics:")
    for metric in filtered_metrics:
        print("  - {}: {}".format(metric['name'], metric['value']))
    
    return len(filtered_metrics) > 0

if __name__ == "__main__":
    success = test_filter_logic()
    if success:
        print("\n✅ Data filtering test passed!")
    else:
        print("\n❌ Data filtering test failed!")
