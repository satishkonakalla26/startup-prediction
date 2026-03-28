import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_prediction.settings')
import django
django.setup()

from adminapp.models import Dataset
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier, AdaBoostClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Get the latest dataset
data = Dataset.objects.all().order_by('-data_id').first()
if not data:
    print("No dataset found")
else:
    print(f"Testing all 3 algorithms with dataset ID: {data.data_id}\n")
    
    algorithms = [
        ('Gradient Boosting', 'gb', GradientBoostingClassifier(n_estimators=100, random_state=0)),
        ('AdaBoost', 'ad', AdaBoostClassifier(n_estimators=100, random_state=0)),
        ('Random Forest', 'rf', RandomForestClassifier(n_estimators=100, random_state=0)),
    ]
    
    try:
        file = str(data.data_set)
        df_data = pd.read_csv('./media/' + file)
        
        # Drop non-numeric columns
        if 'name' in df_data.columns:
            df_data = df_data.drop(columns=['name'])
        if 'id' in df_data.columns:
            df_data = df_data.drop(columns=['id'])
        
        X = df_data.drop(['status'], axis=1)
        y = df_data['status']
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        
        for algo_name, prefix, model in algorithms:
            print(f"Training {algo_name}...")
            model.fit(x_train, y_train)
            
            prediction = model.predict(x_test)
            accuracy = accuracy_score(prediction, y_test)
            precision = precision_score(prediction, y_test, average='weighted')
            recall = recall_score(prediction, y_test, average='weighted')
            f1 = f1_score(prediction, y_test, average='weighted')
            
            # Save to database
            setattr(data, f'{prefix}_accuracy', round(accuracy * 100, 2))
            setattr(data, f'{prefix}_precision', round(precision * 100, 2))
            setattr(data, f'{prefix}_recall', round(recall * 100, 2))
            setattr(data, f'{prefix}_f1_score', round(f1 * 100, 2))
            setattr(data, f'{prefix}_algo', f'{algo_name.lower().replace(" ", "_")}')
            
            print(f"  ✓ Accuracy: {round(accuracy * 100, 2)}%")
            print(f"  ✓ Precision: {round(precision * 100, 2)}%")
            print(f"  ✓ Recall: {round(recall * 100, 2)}%")
            print(f"  ✓ F1 Score: {round(f1 * 100, 2)}%\n")
        
        data.save()
        print("✓ All results saved to database!")
        
        # Verify
        refreshed = Dataset.objects.get(data_id=data.data_id)
        print("\nDatabase verification:")
        print(f"  GB: {refreshed.gb_accuracy}%")
        print(f"  Ada: {refreshed.ad_accuracy}%")
        print(f"  RF: {refreshed.rf_accuracy}%")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
