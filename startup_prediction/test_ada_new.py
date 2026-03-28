import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_prediction.settings')
import django
django.setup()

from adminapp.models import Dataset
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Get the latest dataset (new one)
data = Dataset.objects.all().order_by('-data_id').first()
if not data:
    print("No dataset found")
else:
    print(f"Testing AdaBoost with new dataset ID: {data.data_id}")
    print(f"Dataset file: {data.data_set}\n")
    
    try:
        file = str(data.data_set)
        df_data = pd.read_csv('./media/' + file)
        
        print(f"Dataset shape: {df_data.shape}")
        print(f"Columns: {df_data.columns.tolist()}")
        print(f"Status values: {df_data['status'].unique()}")
        
        # Drop non-numeric columns
        if 'name' in df_data.columns:
            df_data = df_data.drop(columns=['name'])
        if 'id' in df_data.columns:
            df_data = df_data.drop(columns=['id'])
        
        X = df_data.drop(['status'], axis=1)
        y = df_data['status']
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        
        print(f"\nTrain size: {len(x_train)}, Test size: {len(x_test)}")
        
        # Train the model
        model = AdaBoostClassifier(n_estimators=100, random_state=0)
        model.fit(x_train, y_train)
        
        prediction = model.predict(x_test)
        Accuracy  = accuracy_score(prediction, y_test)
        precision = precision_score(prediction, y_test, average='weighted')
        recal     = recall_score(prediction, y_test, average='weighted')
        f_score   = f1_score(prediction, y_test, average='weighted')
        
        print(f"\nResults:")
        print(f"  Accuracy: {round(Accuracy * 100, 2)}%")
        print(f"  Precision: {round(precision * 100, 2)}%")
        print(f"  Recall: {round(recal * 100, 2)}%")
        print(f"  F1 Score: {round(f_score * 100, 2)}%")
        
        # Save to database
        data.ad_accuracy  = round(Accuracy * 100, 2)
        data.ad_precision = round(precision * 100, 2)
        data.ad_recall    = round(recal * 100, 2)
        data.ad_f1_score  = round(f_score * 100, 2)
        data.ad_algo      = 'ada_boost_classifier'
        data.save()
        
        print("\n✓ Results saved to database!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
