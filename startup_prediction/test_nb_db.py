import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_prediction.settings')
import django
django.setup()

from adminapp.models import Dataset
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Get the latest dataset
data = Dataset.objects.all().order_by('-data_id').first()
if not data:
    print("No dataset found")
else:
    print(f"Testing NB with database save for dataset ID: {data.data_id}\n")
    
    try:
        file = str(data.data_set)
        file_path = './media/' + file
        df = pd.read_csv(file_path)
        
        if "Unnamed: 0" in df.columns:
            df = df.drop(columns=["Unnamed: 0"])
        
        # Drop non-numeric columns
        if "name" in df.columns:
            df = df.drop(columns=["name"])
        if "id" in df.columns:
            df = df.drop(columns=["id"])
        
        label_encoder = LabelEncoder()
        df["status"] = label_encoder.fit_transform(df["status"])
        
        X = df.drop(columns=["status"])
        y = df["status"]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        nb_model = GaussianNB()
        nb_model.fit(X_train_scaled, y_train)
        
        y_pred = nb_model.predict(X_test_scaled)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # Save to database
        data.nb_accuracy = round(accuracy * 100, 2)
        data.nb_precision = round(precision * 100, 2)
        data.nb_recall = round(recall * 100, 2)
        data.nb_f1_score = round(f1 * 100, 2)
        data.nb_algo = 'naive_bayes_classifier'
        data.save()
        
        print("Naive Bayes Results Saved to Database:")
        print(f"  ✓ Accuracy: {data.nb_accuracy}%")
        print(f"  ✓ Precision: {data.nb_precision}%")
        print(f"  ✓ Recall: {data.nb_recall}%")
        print(f"  ✓ F1 Score: {data.nb_f1_score}%")
        
        # Verify
        refreshed = Dataset.objects.get(data_id=data.data_id)
        print("\nVerified from Database:")
        print(f"  ✓ NB Accuracy: {refreshed.nb_accuracy}%")
        print(f"  ✓ NB Precision: {refreshed.nb_precision}%")
        print(f"  ✓ NB Recall: {refreshed.nb_recall}%")
        print(f"  ✓ NB F1 Score: {refreshed.nb_f1_score}%")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
