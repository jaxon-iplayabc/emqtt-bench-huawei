#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Auto Filter Functionality
Test the automatic data filtering after test completion
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_auto_filter():
    """Test automatic filtering functionality"""
    print("Testing automatic data filtering functionality...")
    
    # Check if test_data/raw_data directory exists
    raw_data_dir = "test_data/raw_data"
    if not os.path.exists(raw_data_dir):
        print("❌ Raw data directory not found: {}".format(raw_data_dir))
        return False
    
    # Find raw data files
    raw_data_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.json')]
    
    if not raw_data_files:
        print("❌ No raw data files found in {}".format(raw_data_dir))
        return False
    
    print("✅ Found {} raw data files".format(len(raw_data_files)))
    
    # Check if filtered_data directory exists
    filtered_data_dir = "test_data/filtered_data"
    if not os.path.exists(filtered_data_dir):
        print("📁 Creating filtered_data directory...")
        os.makedirs(filtered_data_dir, exist_ok=True)
    
    # Simulate filtering process
    total_original = 0
    total_filtered = 0
    total_removed = 0
    
    for file in raw_data_files:
        file_path = os.path.join(raw_data_dir, file)
        print("\n🔍 Processing file: {}".format(file))
        
        try:
            # Read raw data
            import codecs
            with codecs.open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            raw_metrics = data.get('raw_metrics', [])
            test_name = data.get('test_name', 'Unknown')
            
            print("  📊 Original metrics: {}".format(len(raw_metrics)))
            total_original += len(raw_metrics)
            
            # Simulate filtering (remove zero values and Erlang VM metrics)
            filtered_metrics = []
            for metric in raw_metrics:
                name = metric.get('name', '')
                value = metric.get('value', 0)
                
                # Keep non-zero values and non-Erlang VM metrics
                if (value != 0 and 
                    not name.startswith('erlang_vm_') and
                    not name in ['connection_idle', 'recv', 'connect_fail', 'pub_fail']):
                    filtered_metrics.append(metric)
            
            print("  🧹 Filtered metrics: {}".format(len(filtered_metrics)))
            total_filtered += len(filtered_metrics)
            
            removed_count = len(raw_metrics) - len(filtered_metrics)
            total_removed += removed_count
            
            reduction_percent = (removed_count / len(raw_metrics) * 100) if len(raw_metrics) > 0 else 0
            print("  ❌ Removed metrics: {} ({:.1f}%)".format(removed_count, reduction_percent))
            
            # Create filtered data structure
            filtered_data = {
                "test_name": test_name,
                "test_type": data.get('test_type', 'Unknown'),
                "start_time": data.get('start_time', ''),
                "end_time": data.get('end_time', ''),
                "duration": data.get('duration', 0),
                "port": data.get('port', 0),
                "success": data.get('success', False),
                "error_message": data.get('error_message', None),
                "config": data.get('config', {}),
                "filtered_metrics": filtered_metrics,
                "filter_info": {
                    "original_count": len(raw_metrics),
                    "filtered_count": len(filtered_metrics),
                    "removed_count": removed_count,
                    "filter_timestamp": datetime.now().isoformat(),
                    "source_file": file
                }
            }
            
            # Save filtered data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filtered_filename = "filtered_{}_{}.json".format(test_name, timestamp)
            filtered_path = os.path.join(filtered_data_dir, filtered_filename)
            
            import codecs
            with codecs.open(filtered_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False)
            
            print("  💾 Saved filtered data: {}".format(filtered_path))
            
        except Exception as e:
            print("  ❌ Error processing {}: {}".format(file, e))
            return False
    
    # Display overall statistics
    total_reduction_percent = (total_removed / total_original * 100) if total_original > 0 else 0
    
    print("\n📊 Overall Filtering Statistics:")
    print("  • Total original metrics: {}".format(total_original))
    print("  • Total filtered metrics: {}".format(total_filtered))
    print("  • Total removed metrics: {}".format(total_removed))
    print("  • Overall reduction: {:.1f}%".format(total_reduction_percent))
    print("  • Filtered data location: {}".format(filtered_data_dir))
    
    return True

if __name__ == "__main__":
    success = test_auto_filter()
    if success:
        print("\n✅ Auto filter test completed successfully!")
    else:
        print("\n❌ Auto filter test failed!")
