from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
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

def home(req):
    """Home page with login buttons"""
    return render(req, 'main_template/home.html')

def admin_login(req):
    if req.method == "POST":
        username = req.POST.get("username")
        password = req.POST.get("password")
        remember_me = req.POST.get("remember")
        
        if username == "admin" and password == "admin":
            req.session['admin_logged_in'] = True
            messages.success(req, 'Successfully logged in')
            
            response = redirect('index')
            
            # Set "Remember me" cookie for 30 days
            if remember_me:
                response.set_cookie('admin_username', username, max_age=30*24*60*60, httponly=True)
                response.set_cookie('admin_remembered', 'true', max_age=30*24*60*60, httponly=True)
            else:
                # Remove cookie if unchecked
                response.delete_cookie('admin_username')
                response.delete_cookie('admin_remembered')
            
            return response
        else:
            messages.warning(req, 'Incorrect Details')
            return redirect('admin_login')
    
    # Check if there's a remembered login
    context = {}
    if req.COOKIES.get('admin_remembered') == 'true':
        context['remembered_username'] = req.COOKIES.get('admin_username', '')
        context['is_remembered'] = True
    
    return render(req, 'main_template/admin-login.html', context)


def admin_logout(request):
    if 'admin_logged_in' in request.session:
        del request.session['admin_logged_in']
    messages.info(request, 'You have been logged out!')
    return redirect('admin_login')


def check_admin_auth(view_func):
    """Decorator to check admin authentication"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_logged_in'):
            messages.warning(request, 'Please login as admin first')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ──────────────────────────────────────────────────────────────────────────────
# API ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@check_admin_auth
def get_stats(request):
    """API endpoint to get dashboard statistics"""
    try:
        accepted = User.objects.filter(status='accepted').count()
        pending = User.objects.filter(status='pending').count()
        rejected = User.objects.filter(status='rejected').count()
        total = User.objects.count()
        
        return JsonResponse({
            'accepted': accepted,
            'pending': pending,
            'rejected': rejected,
            'total': total
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ──────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────

@check_admin_auth
def index(req):
    return render(req, 'admin_template/index.html')


# ──────────────────────────────────────────────────────────────────────────────
# USER MANAGEMENT
# ──────────────────────────────────────────────────────────────────────────────

@check_admin_auth
def pending_users(req):
    users_pending = User.objects.filter(status="pending")
    userpen = {"pending_users": users_pending}
    return render(req, 'admin_template/pending-users.html', userpen)


@check_admin_auth
def all_users(req):
    users_all = User.objects.filter(
        Q(status="accepted") | Q(status="restricted") | Q(status="rejected")
    )
    return render(req, 'admin_template/all-users.html', {"alluser": users_all})


@check_admin_auth
def accept(request, id):
    status_update = User.objects.get(user_id=id)
    status_update.status = "accepted"
    status_update.save()
    messages.info(request, 'Status has been accepted')
    return redirect('pending_users')


@check_admin_auth
def reject(request, id):
    status_reject = User.objects.get(user_id=id)
    status_reject.status = "rejected"
    status_reject.save()
    messages.info(request, 'Status has been rejected')
    return redirect('pending_users')


@check_admin_auth
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


@check_admin_auth
def remove(request, id):
    status_delete = User.objects.get(user_id=id)
    status_delete.delete()
    messages.warning(request, 'User has been removed from database')
    return redirect('all_users')


# ──────────────────────────────────────────────────────────────────────────────
# DATASET
# ──────────────────────────────────────────────────────────────────────────────

@check_admin_auth
def upload_dataset(req):
    if req.method == 'POST':
        dataset = req.FILES['file']
        print(dataset, 'dataset')
        data = Dataset.objects.create(data_set=dataset)
        return redirect('view_dataset')
    return render(req, 'admin_template/upload-dataset.html')


@check_admin_auth
def view_dataset(req):
    data = Dataset.objects.all().order_by('-data_id').first()
    if not data:
        return render(req, 'admin_template/view-dataset.html', {'i': None, 't': None, 'error': 'No dataset uploaded yet'})
    
    try:
        file = str(data.data_set)
        df = pd.read_csv('./media/' + file)
        table = df.to_html(table_id='data_table')
        return render(req, 'admin_template/view-dataset.html', {'i': data, 't': table})
    except Exception as e:
        return render(req, 'admin_template/view-dataset.html', {'i': data, 't': None, 'error': str(e)})


# ──────────────────────────────────────────────────────────────────────────────
# ALGORITHM PAGES (render)
# ──────────────────────────────────────────────────────────────────────────────

@check_admin_auth
def gradient_boosting_classifier(req):
    data = Dataset.objects.all().order_by('-data_id').first()
    context = {'data': data}
    return render(req, 'admin_template/algorithm-gradient-boosting-classifier.html', context)


@check_admin_auth
def ada_boost_classifier(req):
    data = Dataset.objects.all().order_by('-data_id').first()
    context = {'data': data}
    return render(req, 'admin_template/algorithm-ada-boost-classifier.html', context)


@check_admin_auth
def random_forest_classifier(req):
    data = Dataset.objects.all().order_by('-data_id').first()
    context = {'data': data}
    return render(req, 'admin_template/algorithm-random-forest-classifier.html', context)


@check_admin_auth
def NB_alg(req):
    data = Dataset.objects.all().order_by('-data_id').first()
    context = {'data': data}
    return render(req, 'admin_template/NB_alg.html', context)


@check_admin_auth
def XGB_alg(req):
    data = Dataset.objects.all().order_by('-data_id').first()
    context = {'data': data}
    return render(req, 'admin_template/XGB_alg.html', context)


# ──────────────────────────────────────────────────────────────────────────────
# GRAPH ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

@check_admin_auth
def graph_analasis(req):
    try:
        data = Dataset.objects.all().order_by('-data_id').first()
        gbc_a = data.gb_accuracy if data.gb_accuracy else 0
        gbc_p = data.gb_precision if data.gb_precision else 0
        gbc_r = data.gb_recall if data.gb_recall else 0
        gbc_f = data.gb_f1_score if data.gb_f1_score else 0
        rfc_a = data.rf_accuracy if data.rf_accuracy else 0
        rfc_p = data.rf_precision if data.rf_precision else 0
        rfc_r = data.rf_recall if data.rf_recall else 0
        rfc_f = data.rf_f1_score if data.rf_f1_score else 0
        ada_a = data.ad_accuracy if data.ad_accuracy else 0
        ada_p = data.ad_precision if data.ad_precision else 0
        ada_r = data.ad_recall if data.ad_recall else 0
        ada_f = data.ad_f1_score if data.ad_f1_score else 0
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

@check_admin_auth
def gbc_runalgo(req, id):
    try:
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.preprocessing import LabelEncoder
        
        # Check if dataset exists
        try:
            data = Dataset.objects.get(data_id=id)
        except Dataset.DoesNotExist:
            messages.error(req, f'Dataset with ID {id} not found. Please upload a dataset first.')
            return redirect('algorithm1')
        
        file = str(data.data_set)
        df_data = pd.read_csv('./media/' + file)
        
        # Check if 'status' column exists
        if 'status' not in df_data.columns:
            messages.error(req, 'Dataset format error: "status" column not found. This algorithm requires a startup prediction dataset with a "status" column.')
            return redirect('algorithm1')
        
        # Drop non-numeric columns
        if 'name' in df_data.columns:
            df_data = df_data.drop(columns=['name'])
        if 'id' in df_data.columns:
            df_data = df_data.drop(columns=['id'])
        
        X = df_data.drop(['status'], axis=1)
        y = df_data['status']
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        
        # Train the model
        model = GradientBoostingClassifier(n_estimators=100, random_state=0)
        model.fit(x_train, y_train)
        
        prediction = model.predict(x_test)
        Accuracy  = accuracy_score(prediction, y_test)
        precision = precision_score(prediction, y_test, average='weighted')
        recal     = recall_score(prediction, y_test, average='weighted')
        f_score   = f1_score(prediction, y_test, average='weighted')
        data.gb_accuracy  = round(Accuracy * 100, 2)
        data.gb_precision = round(precision * 100, 2)
        data.gb_recall    = round(recal * 100, 2)
        data.gb_f1_score  = round(f_score * 100, 2)
        data.gb_algo      = 'gradient_boosting_classifier'
        data.save()
        messages.success(req, 'Gradient Boosting analysis completed successfully')
        return redirect('algorithm1')
    except Exception as e:
        messages.error(req, f'Error running algorithm: {str(e)}')
        return redirect('algorithm1')


@check_admin_auth
def ada_runalgo(req, id):
    try:
        from sklearn.ensemble import AdaBoostClassifier
        from sklearn.preprocessing import LabelEncoder
        
        # Check if dataset exists
        try:
            data = Dataset.objects.get(data_id=id)
        except Dataset.DoesNotExist:
            messages.error(req, f'Dataset with ID {id} not found. Please upload a dataset first.')
            return redirect('algorithm2')
        
        file = str(data.data_set)
        df_data = pd.read_csv('./media/' + file)
        
        # Check if 'status' column exists
        if 'status' not in df_data.columns:
            messages.error(req, 'Dataset format error: "status" column not found. This algorithm requires a startup prediction dataset with a "status" column.')
            return redirect('algorithm2')
        
        # Drop non-numeric columns
        if 'name' in df_data.columns:
            df_data = df_data.drop(columns=['name'])
        if 'id' in df_data.columns:
            df_data = df_data.drop(columns=['id'])
        
        X = df_data.drop(['status'], axis=1)
        y = df_data['status']
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        
        # Train the model
        model = AdaBoostClassifier(n_estimators=100, random_state=0)
        model.fit(x_train, y_train)
        
        prediction = model.predict(x_test)
        Accuracy  = accuracy_score(prediction, y_test)
        precision = precision_score(prediction, y_test, average='weighted')
        recal     = recall_score(prediction, y_test, average='weighted')
        f_score   = f1_score(prediction, y_test, average='weighted')
        data.ad_accuracy  = round(Accuracy * 100, 2)
        data.ad_precision = round(precision * 100, 2)
        data.ad_recall    = round(recal * 100, 2)
        data.ad_f1_score  = round(f_score * 100, 2)
        data.ad_algo      = 'ada_boost_classifier'
        data.save()
        messages.success(req, 'AdaBoost analysis completed successfully')
        return redirect('algorithm2')
    except Exception as e:
        messages.error(req, f'Error running algorithm: {str(e)}')
        return redirect('algorithm2')


@check_admin_auth
def rfc_runalgo(req, id):
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder
        
        # Check if dataset exists
        try:
            data = Dataset.objects.get(data_id=id)
        except Dataset.DoesNotExist:
            messages.error(req, f'Dataset with ID {id} not found. Please upload a dataset first.')
            return redirect('algorithm3')
        
        file = str(data.data_set)
        df_data = pd.read_csv('./media/' + file)
        
        # Check if 'status' column exists
        if 'status' not in df_data.columns:
            messages.error(req, 'Dataset format error: "status" column not found. This algorithm requires a startup prediction dataset with a "status" column.')
            return redirect('algorithm3')
        
        # Drop non-numeric columns
        if 'name' in df_data.columns:
            df_data = df_data.drop(columns=['name'])
        if 'id' in df_data.columns:
            df_data = df_data.drop(columns=['id'])
        
        X = df_data.drop(['status'], axis=1)
        y = df_data['status']
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        
        # Train the model
        model = RandomForestClassifier(n_estimators=100, random_state=0)
        model.fit(x_train, y_train)
        
        prediction = model.predict(x_test)
        Accuracy  = accuracy_score(prediction, y_test)
        precision = precision_score(prediction, y_test, average='weighted')
        recal     = recall_score(prediction, y_test, average='weighted')
        f_score   = f1_score(prediction, y_test, average='weighted')
        data.rf_accuracy  = round(Accuracy * 100, 2)
        data.rf_precision = round(precision * 100, 2)
        data.rf_recall    = round(recal * 100, 2)
        data.rf_f1_score  = round(f_score * 100, 2)
        data.rf_algo      = 'random_forest_classifier'
        data.save()
        messages.success(req, 'Random Forest analysis completed successfully')
        return redirect('algorithm3')
    except Exception as e:
        messages.error(req, f'Error running algorithm: {str(e)}')
        return redirect('algorithm3')


# ──────────────────────────────────────────────────────────────────────────────
# NAIVE BAYES BUTTON
# ──────────────────────────────────────────────────────────────────────────────

@check_admin_auth
def NB_btn(request):
    try:
        import os
        import joblib
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder, StandardScaler
        from sklearn.naive_bayes import GaussianNB
        
        # Get the latest uploaded dataset
        data = Dataset.objects.all().order_by('-data_id').first()
        if not data:
            messages.error(request, 'No dataset uploaded. Please upload a dataset first.')
            return redirect('NB_alg')
        
        file = str(data.data_set)
        file_path = './media/' + file
        
        if not os.path.exists(file_path):
            messages.error(request, f'Dataset file not found at {file_path}')
            return redirect('NB_alg')
        
        df = pd.read_csv(file_path)

        # Check if 'status' column exists
        if 'status' not in df.columns:
            messages.error(request, 'Dataset format error: "status" column not found. This algorithm requires a startup prediction dataset with a "status" column.')
            return redirect('NB_alg')

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

        # Save to database
        data.nb_accuracy  = round(accuracy * 100, 2)
        data.nb_precision = round(precision * 100, 2)
        data.nb_recall    = round(recall * 100, 2)
        data.nb_f1_score  = round(f1 * 100, 2)
        data.nb_algo      = 'naive_bayes_classifier'
        data.save()

        context = {
            "Accuracy":  round(accuracy  * 100, 2),
            "Precision": round(precision * 100, 2),
            "Recall":    round(recall    * 100, 2),
            "F1_Score":  round(f1        * 100, 2),
        }
        messages.success(request, 'Naive Bayes analysis completed successfully')
        return redirect('NB_alg')
    except Exception as e:
        messages.error(request, f'Error running Naive Bayes: {str(e)}')
        return redirect('NB_alg')


# ──────────────────────────────────────────────────────────────────────────────
# XGBOOST BUTTON
# ──────────────────────────────────────────────────────────────────────────────

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


@check_admin_auth
def XGB_btn(request):
    try:
        import os
        import joblib
        from xgboost import XGBClassifier
        
        # Get the latest uploaded dataset
        data = Dataset.objects.all().order_by('-data_id').first()
        if not data:
            messages.error(request, 'No dataset uploaded. Please upload a dataset first.')
            return redirect('XGB_alg')
        
        file = str(data.data_set)
        file_path = './media/' + file
        
        if not os.path.exists(file_path):
            messages.error(request, f'Dataset file not found at {file_path}')
            return redirect('XGB_alg')
        
        df = pd.read_csv(file_path)

        # Check if 'status' column exists
        if 'status' not in df.columns:
            messages.error(request, 'Dataset format error: "status" column not found. This algorithm requires a startup prediction dataset with a "status" column.')
            return redirect('XGB_alg')

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

        # Save to database
        data.xgb_accuracy  = round(accuracy * 100, 2)
        data.xgb_precision = round(precision * 100, 2)
        data.xgb_recall    = round(recall * 100, 2)
        data.xgb_f1_score  = round(f1 * 100, 2)
        data.xgb_algo      = 'xgboost_classifier'
        data.save()

        context = {
            "Accuracy":  round(accuracy  * 100, 2),
            "Precision": round(precision * 100, 2),
            "Recall":    round(recall    * 100, 2),
            "F1_Score":  round(f1        * 100, 2),
        }
        messages.success(request, 'XGBoost analysis completed successfully')
        return redirect('XGB_alg')
    except Exception as e:
        messages.error(request, f'Error running XGBoost: {str(e)}')
        return redirect('XGB_alg')
