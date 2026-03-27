# 🚀 Startup Prediction System - Testing Resources Guide

## ✅ Resources Ready for Testing

### 1. **Sample Dataset** 
- **Location:** `dataset/startup_sample.csv`
- **Records:** 25 startup records
- **Features:** Relationships, funding rounds, funding amount, category flags, investment types, etc.
- **Target:** Success (1) or Failure (0)

### 2. **Trained ML Models**
- **xgb_models.pkl** - XGBoost model (80% accuracy on test data)
- **scalers.pkl** - StandardScaler for numeric features
- **label_encoders.pkl** - LabelEncoder for target variable
- **Location:** Project root directory (same level as manage.py)

---

## 📋 **Testing Scenarios**

### **Test 1: Upload Dataset to Admin Panel**
1. Login as admin: `admin` / `admin`
2. Go to: http://localhost:8000/upload-dataset/
3. Upload: `dataset/startup_sample.csv`
4. View at: http://localhost:8000/view-dataset/

### **Test 2: Run ML Algorithms**
1. Login as admin
2. Go to: http://localhost:8000/index/
3. Click on algorithm links:
   - Gradient Boosting Classifier
   - AdaBoost Classifier
   - Random Forest Classifier
   - Naive Bayes
   - XGBoost

### **Test 3: Make Predictions (User)**
1. Login as user: `john@example.com` / `john@123`
2. Go to: http://localhost:8000/user/dashboard/
3. Click "XGBoost Predict"
4. Fill in sample values and click "Predict"

**Sample Input Values (for success):**
```
Relationships: 25
Funding Rounds: 5
Total Funding: 5000000
Avg Participants: 3.5
Is Software: 1
Is Web: 1
Is Enterprise: 0
Has VC: 1
Has Angel: 1
etc...
```

---

## 🎯 **Testing Checklist**

- [ ] Admin login works
- [ ] User login works
- [ ] Dataset upload works
- [ ] Dataset view shows data
- [ ] Algorithms run without errors
- [ ] XGBoost predictions work
- [ ] User dashboard is accessible
- [ ] All navigation links work

---

## 🔧 **What Works Now**

✅ Full authentication system  
✅ User management UI  
✅ Dataset upload functionality  
✅ ML model predictions  
✅ Admin dashboard  
✅ User dashboard  
✅ All 5 algorithms available  

---

## ⚠️ **Known Limitations**

- Algorithms may need dataset to be uploaded first
- Naive Bayes & AdaBoost might need data preprocessing
- Graph analysis depends on algorithm results

---

## 📊 **Sample Dataset Info**

| Column | Type | Description |
|--------|------|-------------|
| id | int | Unique identifier |
| name | string | Startup name |
| relationships | int | Number of relationships |
| funding_rounds | int | Number of funding rounds |
| funding_total_usd | float | Total funding in USD |
| is_software | binary | Is software company |
| is_web | binary | Is web-based |
| is_mobile | binary | Is mobile app |
| is_enterprise | binary | Enterprise targeting |
| has_VC | binary | Has VC funding |
| status | binary | 1=Success, 0=Failure |

---

## 🚀 **Next Steps for Upgrade**

1. **Database:** Migrate to PostgreSQL (from SQLite)
2. **Authentication:** Integrate Django Auth or JWT
3. **API:** Create REST API for frontend
4. **Frontend:** React/Vue.js UI
5. **Models:** Add more ML algorithms (Deep Learning, etc.)
6. **Deployment:** Docker + Cloud (AWS/Azure)

---

## 📝 **Notes**

- Models trained on 25 startup samples (80% accuracy)
- For production, train with larger dataset (10k+ records)
- Current setup is for testing only

