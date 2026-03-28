import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_prediction.settings')
import django
django.setup()

from adminapp.models import Dataset
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Get the latest dataset
data = Dataset.objects.all().order_by('-data_id').first()
if not data:
    print("No dataset found")
else:
    print(f"Testing XGBoost with dataset ID: {data.data_id}\n")
    
    try:
        file = str(data.data_set)
        file_path = './media/' + file
        df = pd.read_csv(file_path)
        
        df.rename(columns={"Unnamed: 0": "id"}, inplace=True)
        
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
        numeric_features = ["funding_total_usd", "avg_participants"]
        X_train[numeric_features] = scaler.fit_transform(X_train[numeric_features])
        X_test[numeric_features] = scaler.transform(X_test[numeric_features])
        
        xgb_model = XGBClassifier(
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
            n_estimators=50,
            learning_rate=0.1,
            max_depth=3,
            subsample=0.8,
            colsample_bytree=0.8
        )
        xgb_model.fit(X_train, y_train)
        
        y_pred = xgb_model.predict(X_test)
        y_pred_labels = label_encoder.inverse_transform(y_pred)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        context = {
            "Accuracy": round(accuracy * 100, 2),
            "Precision": round(precision * 100, 2),
            "Recall": round(recall * 100, 2),
            "F1_Score": round(f1 * 100, 2),
        }
        
        print("XGBoost Results:")
        print(f"  Accuracy: {context['Accuracy']}%")
        print(f"  Precision: {context['Precision']}%")
        print(f"  Recall: {context['Recall']}%")
        print(f"  F1 Score: {context['F1_Score']}%")
        print("\n✓ XGBoost working correctly!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
