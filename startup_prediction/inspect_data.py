import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_prediction.settings')
import django
django.setup()

from adminapp.models import Dataset
import pandas as pd

# Get the latest dataset
data = Dataset.objects.all().order_by('-data_id').first()
if data:
    file = str(data.data_set)
    df = pd.read_csv('./media/' + file)
    print("Dataset info:")
    print(df.info())
    print("\nFirst few rows:")
    print(df.head(2))
    print("\nColumn dtypes:")
    print(df.dtypes)
