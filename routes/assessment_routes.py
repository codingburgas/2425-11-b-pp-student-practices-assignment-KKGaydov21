from flask import Blueprint, request, jsonify, session
from auth import auth_manager
import numpy as np
import json
import plotly.graph_objects as go
import plotly.utils
from models.logistic_regression import LogisticRegression
from data.database import save_survey_response, get_user_history, get_assessment_statistics
import pickle
import os

assessment_bp = Blueprint('assessment', __name__)

# Load trained model and scaler
def load_trained_model():
    """Load the trained logistic regression model"""
    try:
        if os.path.exists('models/trained_model.pkl') and os.path.exists('models/scaler.pkl'):
            with open('models/trained_model.pkl', 'rb') as f:
                model = pickle.load(f)
            with open('models/scaler.pkl', 'rb') as f:
                scaler = pickle.load(f)
            return model, scaler
        else:
            # Train model if not exists
            import pandas as pd
            from data.utils import load_and_preprocess_data
            
            print("Training new model...")
            data = pd.read_csv('attached_assets/Cancer_Data_1750145449492.csv')
            X, y, feature_names, scaler = load_and_preprocess_data(data)
            
            model = LogisticRegression(learning_rate=0.01, max_iterations=1000, tolerance=1e-6)
            loss_history = model.fit(X, y)
            
            # Save model and scaler
            os.makedirs('models', exist_ok=True)
            with open('models/trained_model.pkl', 'wb') as f:
                pickle.dump(model, f)
            with open('models/scaler.pkl', 'wb') as f:
                pickle.dump(scaler, f)
            
            return model, scaler
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None

# Load model at startup
model, scaler = load_trained_model()

@assessment_bp.route('/predict', methods=['POST'])
@auth_manager.require_auth
def predict():
    """Handle prediction request"""
    try:
        data = request.get_json()
        
        # Extract features from form data
        features = [
            data.get('radius_mean', 0),
            data.get('texture_mean', 0),
            data.get('perimeter_mean', 0),
            data.get('area_mean', 0),
            data.get('smoothness_mean', 0),
            data.get('compactness_mean', 0),
            data.get('concavity_mean', 0),
            data.get('concave_points_mean', 0),
            data.get('symmetry_mean', 0),
            data.get('fractal_dimension_mean', 0),
            data.get('radius_se', 0),
            data.get('texture_se', 0),
            data.get('perimeter_se', 0),
            data.get('area_se', 0),
            data.get('smoothness_se', 0),
            data.get('compactness_se', 0),
            data.get('concavity_se', 0),
            data.get('concave_points_se', 0),
            data.get('symmetry_se', 0),
            data.get('fractal_dimension_se', 0),
            data.get('radius_worst', 0),
            data.get('texture_worst', 0),
            data.get('perimeter_worst', 0),
            data.get('area_worst', 0),
            data.get('smoothness_worst', 0),
            data.get('compactness_worst', 0),
            data.get('concavity_worst', 0),
            data.get('concave_points_worst', 0),
            data.get('symmetry_worst', 0),
            data.get('fractal_dimension_worst', 0)
        ]
        
        # Check if model and scaler are loaded
        if model is None or scaler is None:
            return jsonify({'error': 'Model not loaded properly'}), 500
        
        # Prepare input data
        input_data = np.array([features])
        input_scaled = scaler.transform(input_data)
        
        # Make prediction
        probability = model.predict_proba(input_scaled)[0]
        prediction = model.predict(input_scaled)[0]
        
        # Determine risk level
        if probability < 0.3:
            risk_level = "Very Low"
        elif probability < 0.5:
            risk_level = "Low"
        elif probability < 0.7:
            risk_level = "Moderate"
        else:
            risk_level = "High"
        
        # Save to database
        survey_data = {f'feature_{i}': features[i] for i in range(len(features))}
        prediction_result = {
            'probability': probability,
            'prediction': int(prediction),
            'risk_level': risk_level
        }
        
        try:
            survey_id = save_survey_response(survey_data, prediction_result, session['user_id'])
        except Exception as e:
            survey_id = None
            print(f"Database save error: {e}")
        
        # Create gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = probability * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Malignancy Risk (%)", 'font': {'size': 24, 'color': '#2d3748'}},
            delta = {'reference': 50, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': "#2d3748"},
                'bar': {'color': "#667eea", 'thickness': 0.8},
                'steps': [
                    {'range': [0, 30], 'color': "#c6f6d5"},
                    {'range': [30, 50], 'color': "#bee3f8"},
                    {'range': [50, 70], 'color': "#fbb6ce"},
                    {'range': [70, 100], 'color': "#fed7d7"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        
        fig_gauge.update_layout(
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': "#2d3748", 'family': "Arial"}
        )
        
        gauge_json = json.dumps(fig_gauge, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({
            'probability': float(probability),
            'prediction': int(prediction),
            'risk_level': risk_level,
            'survey_id': survey_id,
            'gauge_chart': gauge_json
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/history')
@auth_manager.require_auth
def history():
    """Get user history"""
    try:
        user_id = session.get('user_id')
        history = get_user_history(user_id, limit=20)
        
        history_data = []
        for assessment in history:
            history_data.append({
                'id': assessment.id,
                'date': assessment.timestamp.strftime('%Y-%m-%d %H:%M'),
                'risk_level': assessment.risk_level,
                'probability': assessment.prediction_probability,
                'prediction': 'Malignant' if assessment.prediction_class == 1 else 'Benign'
            })
        
        return jsonify(history_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/analytics')
def analytics():
    """Get analytics data"""
    try:
        stats = get_assessment_statistics()
        
        analytics_data = {
            'total_assessments': stats.get('total_assessments', 0),
            'malignant_count': stats.get('malignant_count', 0),
            'benign_count': stats.get('benign_count', 0),
            'average_risk': stats.get('average_risk', 0),
            'recent_assessments': stats.get('total_assessments', 0)
        }
        
        return jsonify(analytics_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500