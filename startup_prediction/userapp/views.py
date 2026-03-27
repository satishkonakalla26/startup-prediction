from django.shortcuts import render, redirect
from django.contrib import messages
from mainapp.models import User
import pandas as pd
from pickle import load
from userapp.models import *
import joblib
import os
from pathlib import Path

# Get the project base directory
BASE_DIR = Path(__file__).resolve().parent.parent


# ──────────────────────────────────────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────────────────────────────────────

def user_login(req):
    if req.method == "POST":
        email    = req.POST.get("email")
        password = req.POST.get("password")
        print(email, password)
        try:
            user = User.objects.get(Email=email, Password=password)
            if user.status == "pending":
                messages.info(req, 'Your account is on pending approval')
                return redirect('user_login')
            if user.status == "rejected":
                messages.warning(req, 'Your account has been rejected')
                return redirect('user_login')
            if user.status == "restricted":
                messages.warning(req, 'Your account has been restricted')
                return redirect('user_login')
            req.session["user_id"] = user.user_id
            messages.success(req, 'Logged in successfully :)')
            return redirect('dashboard')
        except Exception:
            messages.warning(req, 'Incorrect details')
            return redirect('user_login')
    return render(req, 'main_template/user-login.html')


def user_logout(request):
    messages.info(request, 'You have been logged out :( ')
    return redirect('user_login')


def user_register(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        phone = request.POST.get("phone")
        city = request.POST.get("city")
        state = request.POST.get("state")
        
        # Validation
        if not fullname or not email or not password or not phone:
            messages.warning(request, 'Please fill all required fields')
            return redirect('user_register')
        
        if password != confirm_password:
            messages.warning(request, 'Passwords do not match')
            return redirect('user_register')
        
        if len(password) < 6:
            messages.warning(request, 'Password must be at least 6 characters')
            return redirect('user_register')
        
        # Check if email already exists
        if User.objects.filter(Email=email).exists():
            messages.warning(request, 'Email already registered')
            return redirect('user_register')
        
        # Create new user with 'pending' status
        try:
            user = User.objects.create(
                Fullname=fullname,
                Email=email,
                Password=password,
                Phone=phone,
                city=city,
                state=state,
                status='pending'
            )
            messages.success(request, 'Registration successful! Awaiting admin approval.')
            return redirect('user_login')
        except Exception as e:
            messages.warning(request, f'Registration failed: {str(e)}')
            return redirect('user_register')
    
    return render(request, 'main_template/user-register.html')


# ──────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────

def user_dashboard(request):
    return render(request, 'user_template/user-dashboard.html')


# ──────────────────────────────────────────────────────────────────────────────
# PREDICTION
# ──────────────────────────────────────────────────────────────────────────────

def prediction(request):
    """Handle analysis predictions using XGBoost model"""
    prediction_result = None
    error_message = None

    if xgb_model is None:
        error_message = "ML models not loaded. Please train the model first."
        return render(request, 'user_template/startup-prediction.html',
                      {'error_message': error_message})

    if request.method == "POST":
        try:
            # Collect input data from form
            input_data = {
                "relationships":    int(request.POST.get("relationships", 0)),
                "funding_rounds":   int(request.POST.get("funding_rounds", 0)),
                "funding_total_usd": float(request.POST.get("funding_total_usd", 0.0)),
                "is_software":      1 if request.POST.get("is_software") else 0,
                "is_web":           1 if request.POST.get("is_web") else 0,
                "is_mobile":        1 if request.POST.get("is_mobile") else 0,
                "is_enterprise":    1 if request.POST.get("is_enterprise") else 0,
                "is_advertising":   1 if request.POST.get("is_advertising") else 0,
                "is_gamesvideo":    1 if request.POST.get("is_gamesvideo") else 0,
                "is_ecommerce":     1 if request.POST.get("is_ecommerce") else 0,
                "is_biotech":       1 if request.POST.get("is_biotech") else 0,
                "is_consulting":    1 if request.POST.get("is_consulting") else 0,
                "is_othercategory": 1 if request.POST.get("is_othercategory") else 0,
                "has_VC":           1 if request.POST.get("has_VC") else 0,
                "has_angel":        1 if request.POST.get("has_angel") else 0,
                "has_roundA":       1 if request.POST.get("has_roundA") else 0,
                "has_roundB":       1 if request.POST.get("has_roundB") else 0,
                "has_roundC":       1 if request.POST.get("has_roundC") else 0,
                "has_roundD":       1 if request.POST.get("has_roundD") else 0,
                "avg_participants": float(request.POST.get("avg_participants", 0.0)),
                "is_top500":        1 if request.POST.get("is_top500") else 0,
            }

            # Create DataFrame with proper column order
            input_df = pd.DataFrame([input_data])
            
            # Ensure columns are in the correct order
            expected_cols = ['relationships', 'funding_rounds', 'funding_total_usd', 'is_software', 
                           'is_web', 'is_mobile', 'is_enterprise', 'is_advertising', 'is_gamesvideo', 
                           'is_ecommerce', 'is_biotech', 'is_consulting', 'is_othercategory', 
                           'has_VC', 'has_angel', 'has_roundA', 'has_roundB', 'has_roundC', 
                           'has_roundD', 'avg_participants', 'is_top500']
            input_df = input_df[expected_cols]

            # Scale numeric features
            numeric_features = ["funding_total_usd", "avg_participants"]
            input_df[numeric_features] = scaler.transform(input_df[numeric_features])

            # Make prediction
            prediction_prob = xgb_model.predict_proba(input_df)
            prediction = xgb_model.predict(input_df)
            predicted_label = label_encoder.inverse_transform(prediction)[0]
            
            # Get confidence score
            confidence = (max(prediction_prob[0]) * 100)
            
            # Format result with details
            if predicted_label == 1:
                prediction_result = f"""✅ <strong>SUCCESS PREDICTION</strong>
                
This startup has characteristics indicating a high likelihood of success!

💡 Key Insights:
• Industry Focus: {sum([input_data['is_' + cat] for cat in ['software', 'web', 'mobile', 'enterprise']])} positive categories identified
• Funding: {input_data['funding_rounds']} rounds with ${input_data['funding_total_usd']:,.0f} total
• Investor Support: {'VC' if input_data['has_VC'] else 'No VC'} | {'Angel' if input_data['has_angel'] else 'No Angel'}
• Network: {input_data['relationships']} business relationships

<strong>Confidence: {confidence:.1f}%</strong>

📊 Recommendation: This startup shows strong potential for growth and success. Focus on maintaining investor relationships and market positioning."""
            else:
                prediction_result = f"""⚠️ <strong>FAILURE PREDICTION</strong>
                
This startup shows characteristics that may lead to failure. Consider these improvements:

🔍 Areas of Concern:
• Industry Focus: Limited category diversity
• Funding Rounds: Only {input_data['funding_rounds']} rounds (industry avg: 3-5)
• Investor Backing: {'No VC backing' if not input_data['has_VC'] else 'Has VC'} | {'No Angel investors' if not input_data['has_angel'] else 'Has Angels'}
• Business Network: {input_data['relationships']} relationships (should aim for 5+)

💡 Recommendations:
✓ Increase funding rounds to attract more capital
✓ Build stronger business relationships
✓ Consider different industry verticals
✓ Seek venture capital and angel investor support

<strong>Confidence: {confidence:.1f}%</strong>

📈 Success Path: Focus on diversification and relationship building."""

        except Exception as e:
            error_message = f"Error during analysis: {str(e)}"
            return render(request, 'user_template/startup-prediction.html',
                          {'error_message': error_message})

    return render(request, 'user_template/startup-prediction.html',
                  {'prediction_result': prediction_result})


# ──────────────────────────────────────────────────────────────────────────────
# USER PROFILE
# ──────────────────────────────────────────────────────────────────────────────

def user_profile(request):
    userid = request.session["user_id"]
    usser  = User.objects.get(user_id=userid)
    context = {"i": usser}

    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email    = request.POST.get("email")
        phone    = request.POST.get("phone")
        password = request.POST.get("password")
        city     = request.POST.get("city")
        industry = request.POST.get("industry")
        state    = request.POST.get("state")

        if len(request.FILES) != 0:
            image = request.FILES["img"]
            usser.image = image

        usser.Fullname = fullname
        usser.Email    = email
        usser.Phone    = phone
        usser.Password = password
        usser.city     = city
        usser.industry = industry
        usser.state    = state
        usser.save()
        messages.info(request, 'Details Updated!')
        return redirect('user_profile')

    return render(request, 'user_template/user-profile.html', context)


# ──────────────────────────────────────────────────────────────────────────────
# XGBoost PREDICTION (new startup predict view)
# ──────────────────────────────────────────────────────────────────────────────

# Load trained model and preprocessing objects
try:
    xgb_model     = joblib.load(os.path.join(BASE_DIR, "xgb_models.pkl"))
    scaler        = joblib.load(os.path.join(BASE_DIR, "scalers.pkl"))
    label_encoder = joblib.load(os.path.join(BASE_DIR, "label_encoders.pkl"))
except FileNotFoundError:
    xgb_model     = None
    scaler        = None
    label_encoder = None


def predict_startup(request):
    prediction_result = None

    if xgb_model is None:
        prediction_result = "ML models not loaded. Please train the model first."
        return render(request, 'user_template/predict_startup.html',
                      {'prediction_result': prediction_result})

    if request.method == "POST":
        try:
            # Get user from session
            userid = request.session.get("user_id")
            user_obj = None
            if userid:
                user_obj = User.objects.get(user_id=userid)

            # Collect input data (WITHOUT id field, as model wasn't trained with it)
            input_data = {
                "relationships":    int(request.POST.get("relationships", 0)),
                "funding_rounds":   int(request.POST.get("funding_rounds", 0)),
                "funding_total_usd": float(request.POST.get("funding_total_usd", 0.0)),
                "is_software":      int(request.POST.get("is_software", 0)),
                "is_web":           int(request.POST.get("is_web", 0)),
                "is_mobile":        int(request.POST.get("is_mobile", 0)),
                "is_enterprise":    int(request.POST.get("is_enterprise", 0)),
                "is_advertising":   int(request.POST.get("is_advertising", 0)),
                "is_gamesvideo":    int(request.POST.get("is_gamesvideo", 0)),
                "is_ecommerce":     int(request.POST.get("is_ecommerce", 0)),
                "is_biotech":       int(request.POST.get("is_biotech", 0)),
                "is_consulting":    int(request.POST.get("is_consulting", 0)),
                "is_othercategory": int(request.POST.get("is_othercategory", 0)),
                "has_VC":           int(request.POST.get("has_VC", 0)),
                "has_angel":        int(request.POST.get("has_angel", 0)),
                "has_roundA":       int(request.POST.get("has_roundA", 0)),
                "has_roundB":       int(request.POST.get("has_roundB", 0)),
                "has_roundC":       int(request.POST.get("has_roundC", 0)),
                "has_roundD":       int(request.POST.get("has_roundD", 0)),
                "avg_participants": float(request.POST.get("avg_participants", 0.0)),
                "is_top500":        int(request.POST.get("is_top500", 0)),
            }

            # Create DataFrame with proper column order (matching training data)
            input_df = pd.DataFrame([input_data])
            
            # Ensure columns are in the correct order
            expected_cols = ['relationships', 'funding_rounds', 'funding_total_usd', 'is_software', 
                           'is_web', 'is_mobile', 'is_enterprise', 'is_advertising', 'is_gamesvideo', 
                           'is_ecommerce', 'is_biotech', 'is_consulting', 'is_othercategory', 
                           'has_VC', 'has_angel', 'has_roundA', 'has_roundB', 'has_roundC', 
                           'has_roundD', 'avg_participants', 'is_top500']
            input_df = input_df[expected_cols]

            # Scale numeric features
            numeric_features = ["funding_total_usd", "avg_participants"]
            input_df[numeric_features] = scaler.transform(input_df[numeric_features])

            # Make prediction
            prediction       = xgb_model.predict(input_df)
            predicted_label  = label_encoder.inverse_transform(prediction)[0]
            
            # Format result
            predicted_result_text = "SUCCESS" if predicted_label == 1 else "FAILURE"
            if predicted_label == 1:
                prediction_result = f"✅ SUCCESS - This startup is likely to succeed!"
            else:
                prediction_result = f"⚠️ FAILURE - This startup may face challenges."

            # Save prediction to database
            prediction_record = Predict(
                user=user_obj,
                company_name=request.POST.get("company_name", ""),
                relationships=input_data["relationships"],
                funding_rounds=input_data["funding_rounds"],
                funding_total_usd=input_data["funding_total_usd"],
                Vc=input_data["has_VC"],
                Angel=input_data["has_angel"],
                a=input_data["has_roundA"],
                b=input_data["has_roundB"],
                c=input_data["has_roundC"],
                d=input_data["has_roundD"],
                Participents=input_data["avg_participants"],
                top=input_data["is_top500"],
                Software=input_data["is_software"],
                Web=input_data["is_web"],
                Mobile=input_data["is_mobile"],
                enterprise=input_data["is_enterprise"],
                Advertising=input_data["is_advertising"],
                Games=input_data["is_gamesvideo"],
                commerce=input_data["is_ecommerce"],
                Biotech=input_data["is_biotech"],
                Consulting=input_data["is_consulting"],
                Other=input_data["is_othercategory"],
                result=predicted_result_text
            )
            prediction_record.save()

        except Exception as e:
            prediction_result = f"Error: {str(e)}"

    return render(request, 'user_template/predict_startup.html',
                  {'prediction_result': prediction_result})


# ──────────────────────────────────────────────────────────────────────────────
# RESOURCES PAGE
# ──────────────────────────────────────────────────────────────────────────────

def resources(request):
    """Display learning resources and information about startup success factors"""
    resources_data = {
        'factors': [
            {
                'title': 'Funding Rounds',
                'description': 'Multiple funding rounds indicate investor confidence and indicate better chances of success.',
                'impact': 'High'
            },
            {
                'title': 'Relationships',
                'description': 'The number of business relationships and connections is crucial for growth.',
                'impact': 'Medium'
            },
            {
                'title': 'Total Funding Amount',
                'description': 'Higher funding amounts provide more resources for operations and scaling.',
                'impact': 'High'
            },
            {
                'title': 'Venture Capital Support',
                'description': 'Backing from VC firms significantly increases startup success rate.',
                'impact': 'High'
            },
            {
                'title': 'Angel Investors',
                'description': 'Early support from angel investors provides both capital and mentorship.',
                'impact': 'Medium'
            },
            {
                'title': 'Industry Category',
                'description': 'Being in Software, Web, or Mobile categories has higher success rates.',
                'impact': 'Medium'
            }
        ],
        'tips': [
            'Focus on building a strong business network',
            'Seek multiple rounds of funding',
            'Target venture capital funding',
            'Build a product in high-growth industries',
            'Optimize participant diversity in your rounds',
            'Maintain quality relationships with investors'
        ]
    }
    return render(request, 'user_template/resources.html', {'resources': resources_data})


# ──────────────────────────────────────────────────────────────────────────────
# MY PREDICTIONS - PREDICTION HISTORY
# ──────────────────────────────────────────────────────────────────────────────

def my_predictions(request):
    """Display user's prediction history"""
    userid = request.session.get("user_id")
    
    if not userid:
        messages.warning(request, 'Please log in to view predictions')
        return redirect('user_login')
    
    try:
        user_obj = User.objects.get(user_id=userid)
    except User.DoesNotExist:
        messages.warning(request, 'User not found')
        return redirect('user_login')
    
    # Fetch prediction history for the logged-in user
    predictions_list = Predict.objects.filter(user=user_obj).order_by('-created_at')
    
    context = {
        'predictions': predictions_list,
        'total_predictions': predictions_list.count(),
        'success_predictions': predictions_list.filter(result='SUCCESS').count(),
        'failure_predictions': predictions_list.filter(result='FAILURE').count(),
    }
    
    return render(request, 'user_template/my-predictions.html', context)
