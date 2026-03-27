# Startup Success & Failure Prediction
## MCA Project — Aditya University | Prudhvi Raj Penki (23A91F0037)

---

## Project Structure

```
startup_prediction/
├── adminapp/
│   ├── models.py        ← Dataset model with algorithm metrics
│   ├── views.py         ← All admin views (login, users, dataset, algorithms)
│   └── urls.py          ← Admin URL routes
├── userapp/
│   ├── models.py        ← Predict model
│   ├── views.py         ← User login, prediction, profile, XGBoost predict
│   └── urls.py          ← User URL routes
├── mainapp/
│   └── models.py        ← User model
├── startup_prediction/
│   ├── settings.py      ← Django settings (DB, apps, media)
│   └── urls.py          ← Root URL configuration
├── templates/
│   ├── main_template/   ← Shared templates (login pages)
│   ├── admin_template/  ← Admin dashboard templates
│   └── user_template/   ← User dashboard templates
├── media/               ← Uploaded datasets & profile images
├── static/              ← CSS / JS / images
├── dataset/
│   └── startup_sucess.csv   ← Place your dataset here
├── requirements.txt
└── manage.py
```

---

## Setup Instructions

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create MySQL database
```sql
CREATE DATABASE startup_db;
```

### 3. Update settings.py
Edit `startup_prediction/settings.py` and set your MySQL password.

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Place the dataset
Copy `startup_sucess.csv` into the `dataset/` folder.

### 6. Place pre-trained model files in the project root
- `AdaBoostClassifier.pkl`
- `GradientBoostingClassifier.pkl`
- `RandomForestClassifier.pkl`
- `xgb_models.pkl`
- `scalers.pkl`
- `label_encoders.pkl`

### 7. Run the server
```bash
python manage.py runserver
```

### 8. Admin login
- URL: `http://127.0.0.1:8000/admin-login/`
- Username: `admin`
- Password: `admin`

---

## ML Models Used
| Model | Accuracy |
|---|---|
| XGBoost | ~79.49% |
| Naive Bayes | ~64.32% |
| AdaBoost | used for prediction |
| Gradient Boosting | compared in graph |
| Random Forest | compared in graph |
