import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_prediction.settings')
import django
django.setup()

from adminapp.models import Dataset

# Get all datasets
datasets = Dataset.objects.all().order_by('-data_id')
print(f"Total datasets: {datasets.count()}")
for d in datasets[:3]:
    print(f"\nDataset ID: {d.data_id}")
    print(f"  File: {d.data_set}")
    print(f"  GB Accuracy: {d.gb_accuracy}")
    print(f"  Ada Accuracy: {d.ad_accuracy}")
    print(f"  RF Accuracy: {d.rf_accuracy}")
