from django.shortcuts import render, redirect
from django.contrib import messages
from mainapp.models import User
from pickle import load
from django.db.models import Q
from adminapp.models import *
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, recall_score, precision_score,
    auc, roc_auc_score, roc_curve
)


# ──────────────────────────────────────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────────────────────────────────────

def admin_login(req):
    if req.method == "POST":
        username = req.POST.get("username")
        password = req.POST.get("password")
        if username == "admin" and password == "admin":
            messages.success(req, 'Successfully logged in')
            return redirect('index')
        else:
            messages.warning(req, 'Incorrect Details')
            return redirect('admin_login')
    return render(req, 'main_template/admin-login.html')


def admin_logout(request):
    messages.info(request, 'You have been logged out!')
    return redirect('admin_login')


# ──────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────

def index(req):
    return render(req, 'admin_template/index.html')


# ──────────────────────────────────────────────────────────────────────────────
# USER MANAGEMENT
# ──────────────────────────────────────────────────────────────────────────────

def pending_users(req):
    users_pending = User.objects.filter(status="pending")
    userpen = {"pending_users": users_pending}
    return render(req, 'admin_template/pending-users.html', userpen)


def all_users(req):
    users_all = User.objects.filter(
        Q(status="accepted") | Q(status="restricted") | Q(status="rejected")
    )
    return render(req, 'admin_template/all-users.html', {"alluser": users_all})


def accept(request, id):
    status_update = User.objects.get(user_id=id)
    status_update.status = "accepted"
    status_update.save()
    messages.info(request, 'Status has been accepted')
    return redirect('pending_users')


def reject(request, id):
    status_reject = User.objects.get(user_id=id)
    status_reject.status = "rejected"
    status_reject.save()
    messages.info(request, 'Status has been rejected')
    return redirect('pending_users')


def change_status(request, id):
    status_change = User.objects.get(user_id=id)
    if status_change.status == "accepted":
        status_change.status = "restricted"
        status_change.save()
        messages.info(request, 'Status has been changed to restricted')
    else:
        status_change.status = "accepted"
        status_change.save()
        messages.info(request, 'Status has been changed to accepted')
    return redirect('all_users')


def remove(request, id):
    status_delete = User.objects.get(user_id=id)
    status_delete.delete()
    messages.warning(request, 'User has been removed from database')
    return redirect('all_users')


# ──────────────────────────────────────────────────────────────────────────────
# DATASET
# ──────────────────────────────────────────────────────────────────────────────

def upload_dataset(req):
    if req.method == 'POST':
        dataset = req.FILES['file']
        print(dataset, 'dataset')
        data = Dataset.objects.create(data_set=dataset)
        return redirect('view_dataset')
    return render(req, 'admin_template/upload-dataset.html')


def view_dataset(req):
    data = Dataset.objects.all().order_by('-data_id').first()
    file = str(data.data_set)
    df = pd.read_csv('./media/' + file)
    print(df)
    table = df.to_html(table_id='data_table')
    print(table)
    return render(req, 'admin_template/view-dataset.html', {'i': data, 't': table})


# ──────────────────────────────────────────────────────────────────────────────
# ALGORITHM PAGES (render)
# ──────────────────────────────────────────────────────────────────────────────

def gradient_boosting_classifier(req):
    data = Dataset.objects.all().order_by('-data_id').first()
    context = {'data': data}
    return render(req, 'admin_template/algorithm-gradient-boosting-classifier.html', context)


def ada_boost_classifier(req):
    data = Dataset.objects.all().order_by('-data_id').first()
    context = {'data': data}
    return render(req, 'admin_template/algorithm-ada-boost-classifier.html', context)


def random_forest_classifier(req):
    data = Dataset.objects.all().order_by('-data_id').first()
    context = {'data': data}
    return render(req, 'admin_template/algorithm-random-forest-classifier.html', context)


def NB_alg(req):
    return render(req, 'admin_template/NB_alg.html')


def XGB_alg(req):
    return render(req, 'admin_template/XGB_alg.html')


# ──────────────────────────────────────────────────────────────────────────────
# GRAPH ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

def graph_analasis(req):
    try:
        data = Dataset.objects.all().order_by('-data_id').first()
        gbc_a = data.gb_accuracy * 100
        gbc_p = data.gb_precision * 100
        gbc_r = data.gb_recall * 100
        gbc_f = data.gb_f1_score * 100
        rfc_a = data.rf_accuracy * 100
        rfc_p = data.rf_precision * 100
        rfc_r = data.rf_recall * 100
        rfc_f = data.rf_f1_score * 100
        ada_a = data.ad_accuracy * 100
        ada_p = data.ad_precision * 100
        ada_r = data.ad_recall * 100
        ada_f = data.ad_f1_score * 100
        context = {
            'gbc_a': gbc_a, 'gbc_p': gbc_p, 'gbc_r': gbc_r, 'gbc_f': gbc_f,
            'rfc_a': rfc_a, 'rfc_p': rfc_p, 'rfc_r': rfc_r, 'rfc_f': rfc_f,
            'ada_a': ada_a, 'ada_p': ada_p, 'ada_r': ada_r, 'ada_f': ada_f,
        }
        return render(req, 'admin_template/graph-analasis.html', context)
    except Exception:
        messages.warning(req, 'Run all 3 algorithms to compare values')
        return redirect('view_dataset')


# ──────────────────────────────────────────────────────────────────────────────
# ALGORITHM RUN BUTTONS
# ──────────────────────────────────────────────────────────────────────────────

def gbc_runalgo(req, id):
    data = Dataset.objects.get(data_id=id)
    model = load(open('GradientBoostingClassifier.pkl', 'rb'))
    file = str(data.data_set)
    df_data = pd.read_csv('./media/' + file, index_col=0)
    X = df_data.drop(['status'], axis=1)
    Y = pd.get_dummies(df_data['status'])
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    prediction = model.predict(x_test)
    Accuracy  = accuracy_score(prediction, y_test)
    precision = precision_score(prediction, y_test, average='macro')
    recal     = recall_score(prediction, y_test, average='macro')
    f_score   = f1_score(prediction, y_test, average='macro')
    print(Accuracy, precision, recal, f_score)
    data.gb_accuracy  = Accuracy
    data.gb_precision = precision
    data.gb_recall    = recal
    data.gb_f1_score  = f_score
    data.gb_algo      = 'gradient_boosting_classifier'
    data.save()
    return redirect('algorithm1')


def ada_runalgo(req, id):
    data = Dataset.objects.get(data_id=id)
    model = load(open('AdaBoostClassifier.pkl', 'rb'))
    file = str(data.data_set)
    df_data = pd.read_csv('./media/' + file, index_col=0)
    X = df_data.drop(['status'], axis=1)
    Y = pd.get_dummies(df_data['status'])
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    prediction = model.predict(x_test)
    Accuracy  = accuracy_score(prediction, y_test)
    precision = precision_score(prediction, y_test, average='macro')
    recal     = recall_score(prediction, y_test, average='macro')
    f_score   = f1_score(prediction, y_test, average='macro')
    print(Accuracy, precision, recal, f_score)
    data.ad_accuracy  = Accuracy
    data.ad_precision = precision
    data.ad_recall    = recal
    data.ad_f1_score  = f_score
    data.ad_algo      = 'ada_boost_classifier'
    data.save()
    return redirect('algorithm2')


def rfc_runalgo(req, id):
    data = Dataset.objects.get(data_id=id)
    model = load(open('RandomForestClassifier.pkl', 'rb'))
    file = str(data.data_set)
    df_data = pd.read_csv('./media/' + file, index_col=0)
    X = df_data.drop(['status'], axis=1)
    Y = pd.get_dummies(df_data['status'])
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    prediction = model.predict(x_test)
    Accuracy  = accuracy_score(prediction, y_test)
    precision = precision_score(prediction, y_test, average='macro')
    recal     = recall_score(prediction, y_test, average='macro')
    f_score   = f1_score(prediction, y_test, average='macro')
    print(Accuracy, precision, recal, f_score)
    data.rf_accuracy  = Accuracy
    data.rf_precision = precision
    data.rf_recall    = recal
    data.rf_f1_score  = f_score
    data.rf_algo      = 'random_forest_classifier'
    data.save()
    return redirect('algorithm3')


# ──────────────────────────────────────────────────────────────────────────────
# NAIVE BAYES BUTTON
# ──────────────────────────────────────────────────────────────────────────────

def NB_btn(request):
    import pandas as pd
    import joblib
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.naive_bayes import GaussianNB
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    file_path = "dataset/startup_sucess.csv"
    df = pd.read_csv(file_path)

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    label_encoder = LabelEncoder()
    df["status"] = label_encoder.fit_transform(df["status"])

    X = df.drop(columns=["status"])
    y = df["status"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    nb_model = GaussianNB()
    nb_model.fit(X_train_scaled, y_train)

    joblib.dump(nb_model,      "naive_bayes_model.pkl")
    joblib.dump(scaler,        "scaler.pkl")
    joblib.dump(label_encoder, "label_encoder.pkl")

    y_pred = nb_model.predict(X_test_scaled)

    accuracy  = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall    = recall_score(y_test, y_pred, average='weighted')
    f1        = f1_score(y_test, y_pred, average='weighted')

    context = {
        "Accuracy":  round(accuracy  * 100, 2),
        "Precision": round(precision * 100, 2),
        "Recall":    round(recall    * 100, 2),
        "F1_Score":  round(f1        * 100, 2),
    }
    return render(request, 'admin_template/NB_alg.html', context)


# ──────────────────────────────────────────────────────────────────────────────
# XGBOOST BUTTON
# ──────────────────────────────────────────────────────────────────────────────

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def XGB_btn(request):
    file_path = "dataset/startup_sucess.csv"
    df = pd.read_csv(file_path)

    df.rename(columns={"Unnamed: 0": "id"}, inplace=True)

    label_encoder = LabelEncoder()
    df["status"] = label_encoder.fit_transform(df["status"])

    X = df.drop(columns=["status"])
    y = df["status"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    numeric_features = ["funding_total_usd", "avg_participants"]
    X_train[numeric_features] = scaler.fit_transform(X_train[numeric_features])
    X_test[numeric_features]  = scaler.transform(X_test[numeric_features])

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

    joblib.dump(xgb_model,     "xgb_models.pkl")
    joblib.dump(scaler,        "scalers.pkl")
    joblib.dump(label_encoder, "label_encoders.pkl")

    y_pred = xgb_model.predict(X_test)
    y_pred_labels = label_encoder.inverse_transform(y_pred)

    accuracy  = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall    = recall_score(y_test, y_pred, average='weighted')
    f1        = f1_score(y_test, y_pred, average='weighted')

    print(f"Accuracy:  {accuracy  * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall:    {recall    * 100:.2f}%")
    print(f"F1 Score:  {f1        * 100:.2f}%")

    context = {
        "Accuracy":  round(accuracy  * 100, 2),
        "Precision": round(precision * 100, 2),
        "Recall":    round(recall    * 100, 2),
        "F1_Score":  round(f1        * 100, 2),
    }
    return render(request, 'admin_template/XGB_alg.html', context)
