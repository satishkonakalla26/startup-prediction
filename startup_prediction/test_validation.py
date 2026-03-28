"""Test dataset validation for algorithms"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_prediction.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

import pandas as pd
from adminapp.models import Dataset

# Test 1: Check dataset columns
print("=" * 60)
print("TESTING DATASET VALIDATION")
print("=" * 60)

# Get all datasets
all_datasets = Dataset.objects.all().order_by('data_id')
print(f"\nTotal datasets in database: {all_datasets.count()}\n")

for data in all_datasets:
    file_path = f'./media/{str(data.data_set)}'
    print(f"Dataset ID: {data.data_id}")
    print(f"  Filename: {data.data_set}")
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {df.columns.tolist()}")
        
        has_status = 'status' in df.columns
        print(f"  Has 'status' column: {has_status}")
        
        if has_status:
            print(f"  ✅ This dataset WILL WORK with algorithms")
        else:
            print(f"  ❌ This dataset WILL FAIL - missing 'status' column")
    else:
        print(f"  ⚠️  File not found at {file_path}")
    
    print(f"  GB Results saved: {data.gb_accuracy is not None}")
    print()

print("\n" + "=" * 60)
print("CONCLUSION:")
print("=" * 60)
print("✅ Old datasets (with 'status' column) will work")
print("❌ New datasets (without 'status' column) will show error message")
print("   Error: 'Dataset format error: \"status\" column not found...'")
print("=" * 60)
