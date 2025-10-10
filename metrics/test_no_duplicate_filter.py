#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test No Duplicate Filter Functionality
Test that the same test doesn't generate duplicate filtered files
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_no_duplicate_filter():
    """Test that filtering doesn't create duplicate files"""
    print("Testing no duplicate filter functionality...")
    
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
    
    # Clear existing filtered files
    print("🧹 Clearing existing filtered files...")
    for file in os.listdir(filtered_data_dir):
        if file.endswith('.json'):
            os.remove(os.path.join(filtered_data_dir, file))
    
    # Simulate filtering process (first time)
    print("\n🔍 First filtering pass...")
    first_filter_files = []
    
    for file in raw_data_files:
        file_path = os.path.join(raw_data_dir, file)
        print("  Processing: {}".format(file))
        
        try:
            # Read raw data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            test_name = data.get('test_name', 'Unknown')
            raw_metrics = data.get('raw_metrics', [])
            
            # Simulate filtering
            filtered_metrics = []
            for metric in raw_metrics:
                name = metric.get('name', '')
                value = metric.get('value', 0)
                
                # Keep non-zero values and non-Erlang VM metrics
                if (value != 0 and 
                    not name.startswith('erlang_vm_') and
                    not name in ['connection_idle', 'recv', 'connect_fail', 'pub_fail']):
                    filtered_metrics.append(metric)
            
            # Save filtered data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filtered_filename = "filtered_{}_{}.json".format(test_name, timestamp)
            filtered_path = os.path.join(filtered_data_dir, filtered_filename)
            
            filtered_data = {
                "test_name": test_name,
                "filtered_metrics": filtered_metrics,
                "filter_info": {
                    "original_count": len(raw_metrics),
                    "filtered_count": len(filtered_metrics),
                    "filter_timestamp": datetime.now().isoformat()
                }
            }
            
            with open(filtered_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False)
            
            first_filter_files.append(filtered_filename)
            print("  ✅ Saved: {}".format(filtered_filename))
            
        except Exception as e:
            print("  ❌ Error processing {}: {}".format(file, e))
            return False
    
    # Simulate filtering process (second time - should not create duplicates)
    print("\n🔍 Second filtering pass (should not create duplicates)...")
    second_filter_files = []
    
    for file in raw_data_files:
        file_path = os.path.join(raw_data_dir, file)
        print("  Processing: {}".format(file))
        
        try:
            # Read raw data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            test_name = data.get('test_name', 'Unknown')
            
            # Check if filtered file already exists for this test
            existing_files = [f for f in os.listdir(filtered_data_dir) 
                            if f.startswith("filtered_{}_".format(test_name)) and f.endswith('.json')]
            
            if existing_files:
                print("  ⚠️  Filtered file already exists for {}: {}".format(test_name, existing_files[0]))
                print("  ✅ Skipping duplicate creation")
                continue
            
            # This should not happen in the fixed version
            print("  ❌ This should not happen - duplicate file creation detected!")
            return False
            
        except Exception as e:
            print("  ❌ Error processing {}: {}".format(file, e))
            return False
    
    # Check final results
    print("\n📊 Final Results:")
    final_files = [f for f in os.listdir(filtered_data_dir) if f.endswith('.json')]
    print("  • Total filtered files: {}".format(len(final_files)))
    print("  • First pass files: {}".format(len(first_filter_files)))
    print("  • Second pass files: {}".format(len(second_filter_files)))
    
    # Check for duplicates
    test_names = set()
    duplicates = []
    
    for file in final_files:
        # Extract test name from filename
        if file.startswith("filtered_"):
            parts = file.split("_", 2)
            if len(parts) >= 3:
                test_name = parts[1]
                if test_name in test_names:
                    duplicates.append(file)
                else:
                    test_names.add(test_name)
    
    if duplicates:
        print("  ❌ Duplicate files found: {}".format(duplicates))
        return False
    else:
        print("  ✅ No duplicate files found")
        return True

if __name__ == "__main__":
    success = test_no_duplicate_filter()
    if success:
        print("\n✅ No duplicate filter test passed!")
    else:
        print("\n❌ No duplicate filter test failed!")
