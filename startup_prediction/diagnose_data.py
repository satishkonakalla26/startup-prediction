import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_prediction.settings')
import django
django.setup()

from adminapp.models import Dataset
import pandas as pd
from sklearn.model_selection import train_test_split

# Get the latest dataset
data = Dataset.objects.all().order_by('-data_id').first()
if data:
    file = str(data.data_set)
    df_data = pd.read_csv('./media/' + file)
    
    print(f"Dataset: {file}")
    print(f"Total records: {len(df_data)}")
    print(f"Status distribution:")
    print(df_data['status'].value_counts())
    print(f"\nData shape after cleanup:")
    
    if 'name' in df_data.columns:
        df_data = df_data.drop(columns=['name'])
    if 'id' in df_data.columns:
        df_data = df_data.drop(columns=['id'])
    
    X = df_data.drop(['status'], axis=1)
    y = df_data['status']
    
    print(f"Features (X): {X.shape}")
    print(f"Target (y): {y.shape}")
    
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    print(f"\nTrain size: {len(x_train)}")
    print(f"Test size: {len(x_test)}")
    print(f"Test set distribution:")
    print(y_test.value_counts())
