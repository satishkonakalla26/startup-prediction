import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_prediction.settings')
import django
django.setup()

from adminapp.models import Dataset
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Get the latest dataset
data = Dataset.objects.all().order_by('-data_id').first()
if not data:
    print("No dataset found")
else:
    print(f"Testing with dataset ID: {data.data_id}")
    
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
        
        # Train AdaBoost
        model = AdaBoostClassifier(n_estimators=100, random_state=0)
        model.fit(x_train, y_train)
        
        prediction = model.predict(x_test)
        Accuracy = accuracy_score(prediction, y_test)
        precision = precision_score(prediction, y_test, average='weighted')
        recall = recall_score(prediction, y_test, average='weighted')
        f1 = f1_score(prediction, y_test, average='weighted')
        
        print(f"Raw Accuracy: {Accuracy}")
        print(f"Result to save: {round(Accuracy * 100, 2)}")
        
        # Save to database
        data.ad_accuracy = round(Accuracy * 100, 2)
        data.ad_precision = round(precision * 100, 2)
        data.ad_recall = round(recall * 100, 2)
        data.ad_f1_score = round(f1 * 100, 2)
        data.ad_algo = 'ada_boost_classifier'
        data.save()
        
        print("✓ Results saved successfully!")
        
        # Verify
        refreshed = Dataset.objects.get(data_id=data.data_id)
        print(f"Verified - Ada Accuracy from DB: {refreshed.ad_accuracy}")
        print(f"Verified - Ada Precision from DB: {refreshed.ad_precision}")
        print(f"Verified - Ada Recall from DB: {refreshed.ad_recall}")
        print(f"Verified - Ada F1 Score from DB: {refreshed.ad_f1_score}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
