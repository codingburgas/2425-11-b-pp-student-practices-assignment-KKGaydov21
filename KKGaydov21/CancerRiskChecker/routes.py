from CancerRiskChecker.app import app
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json
import plotly.graph_objects as go
import plotly.utils
from app import app, db
from models import User, Assessment
from forms.assessment_forms import AssessmentForm
from ml_model import cancer_model


@app.route('/')
def index():
    return render_template('index.html')




@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's recent assessments
    recent_assessments = Assessment.query.filter_by(user_id=current_user.id)\
        .order_by(Assessment.timestamp.desc()).limit(10).all()
    
    # Get statistics
    total_assessments = Assessment.query.filter_by(user_id=current_user.id).count()
    
    risk_distribution = db.session.query(
        Assessment.risk_level,
        db.func.count(Assessment.id).label('count')
    ).filter_by(user_id=current_user.id).group_by(Assessment.risk_level).all()
    
    return render_template('dashboard.html', 
                         recent_assessments=recent_assessments,
                         total_assessments=total_assessments,
                         risk_distribution=risk_distribution)


@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    form = AssessmentForm()
    
    if form.validate_on_submit():
        # Extract features
        features = [
            form.radius_mean.data,
            form.texture_mean.data,
            form.perimeter_mean.data,
            form.area_mean.data,
            form.concave_points_mean.data,
            form.symmetry_mean.data
        ]
        
        # Make prediction
        result = cancer_model.predict(features)
        
        if result:
            # Save assessment to database
            assessment = Assessment(
                user_id=current_user.id,
                radius_mean=form.radius_mean.data,
                texture_mean=form.texture_mean.data,
                perimeter_mean=form.perimeter_mean.data,
                area_mean=form.area_mean.data,
                concave_points_mean=form.concave_points_mean.data,
                symmetry_mean=form.symmetry_mean.data,
                prediction_probability=result['probability'],
                prediction_class=result['prediction'],
                risk_level=result['risk_level']
            )
            
            db.session.add(assessment)
            
            # Update user statistics
            current_user.total_assessments += 1
            current_user.last_assessment = datetime.utcnow()
            
            db.session.commit()
            
            return redirect(url_for('result', assessment_id=assessment.id))
        else:
            flash('Error processing assessment. Please try again.', 'danger')
    
    return render_template('assessment.html', form=form)


@app.route('/result/<int:assessment_id>')
@login_required
def result(assessment_id):
    assessment = Assessment.query.filter_by(id=assessment_id, user_id=current_user.id).first_or_404()
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=assessment.prediction_probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Malignancy Risk (%)", 'font': {'size': 24, 'color': '#2d3748'}},
        delta={'reference': 50, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge={
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
    
    fig.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#2d3748", 'family': "Arial"}
    )
    
    gauge_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('result.html', assessment=assessment, gauge_chart=gauge_json)


@app.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    assessments = Assessment.query.filter_by(user_id=current_user.id)\
        .order_by(Assessment.timestamp.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('history.html', assessments=assessments)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
