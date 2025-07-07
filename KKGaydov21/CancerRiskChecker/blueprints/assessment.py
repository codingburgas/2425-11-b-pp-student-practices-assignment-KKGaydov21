"""
Assessment blueprint for cancer risk evaluation
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from ..utils.helpers import create_gauge_chart, log_user_activity, flash_errors
from ..utils.ml_engine import cancer_predictor


assessment_bp = Blueprint('assessment', __name__)


@assessment_bp.route('/')
@login_required
def index():
    """Assessment form page."""
    from ..forms.assessment_forms import AssessmentForm
    form = AssessmentForm()
    return render_template('assessment/form.html', form=form)


@assessment_bp.route('/submit', methods=['POST'])
@login_required
def submit():
    """Handle assessment form submission."""
    from ..forms.assessment_forms import AssessmentForm
    from ..models.assessment import Assessment
    from ..app import db
    
    form = AssessmentForm()
    
    if form.validate_on_submit():
        try:
            # Extract features
            features = [
                form.radius_mean.data,
                form.texture_mean.data,
                form.perimeter_mean.data,
                form.area_mean.data,
                form.concave_points_mean.data,
                form.symmetry_mean.data
            ]
            
            # Validate input
            is_valid, message = cancer_predictor.validate_input(features)
            if not is_valid:
                flash(f"Invalid input: {message}", 'danger')
                return render_template('assessment/form.html', form=form)
            
            # Make prediction
            start_time = datetime.utcnow()
            result = cancer_predictor.predict(features)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
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
                    risk_level=result['risk_level'],
                    model_version=result.get('model_version', '2.0'),
                    processing_time=processing_time
                )
                
                db.session.add(assessment)
                
                # Update user statistics
                current_user.increment_assessments()
                
                db.session.commit()
                
                log_user_activity('assessment_completed', 
                                f'ID: {assessment.id}, Risk: {result["risk_level"]}')
                
                flash('Assessment completed successfully!', 'success')
                return redirect(url_for('assessment.result', assessment_id=assessment.id))
            else:
                flash('Error processing assessment. Please try again.', 'danger')
                
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during assessment. Please try again.', 'danger')
            print(f"Assessment error: {e}")
    else:
        flash_errors(form)
    
    return render_template('assessment/form.html', form=form)


@assessment_bp.route('/result/<int:assessment_id>')
@login_required
def result(assessment_id):
    """Display assessment results."""
    from ..models.assessment import Assessment
    
    assessment = Assessment.query.filter_by(
        id=assessment_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # Create gauge chart
    gauge_chart = create_gauge_chart(
        assessment.prediction_probability,
        "Malignancy Risk"
    )
    
    # Get recommendations
    recommendations = assessment.get_recommendations()
    
    return render_template('assessment/result.html', 
                         assessment=assessment,
                         gauge_chart=gauge_chart,
                         recommendations=recommendations)


@assessment_bp.route('/history')
@login_required
def history():
    """Display user's assessment history."""
    from ..models.assessment import Assessment
    
    page = request.args.get('page', 1, type=int)
    assessments = Assessment.query.filter_by(user_id=current_user.id)\
        .order_by(Assessment.timestamp.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('assessment/history.html', assessments=assessments)


@assessment_bp.route('/export/<format>')
@login_required
def export_history(format):
    """Export assessment history in various formats."""
    from ..models.assessment import Assessment
    import csv
    import io
    from flask import Response
    
    assessments = Assessment.query.filter_by(user_id=current_user.id)\
        .order_by(Assessment.timestamp.desc()).all()
    
    if format.lower() == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date', 'Risk Level', 'Probability (%)', 'Classification',
            'Radius Mean', 'Texture Mean', 'Perimeter Mean', 
            'Area Mean', 'Concave Points Mean', 'Symmetry Mean'
        ])
        
        # Write data
        for assessment in assessments:
            writer.writerow([
                assessment.timestamp.strftime('%Y-%m-%d %H:%M'),
                assessment.risk_level,
                f"{assessment.probability_percentage}%",
                assessment.prediction_text,
                assessment.radius_mean,
                assessment.texture_mean,
                assessment.perimeter_mean,
                assessment.area_mean,
                assessment.concave_points_mean,
                assessment.symmetry_mean
            ])
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=assessment_history.csv'
            }
        )
    
    flash('Export format not supported.', 'warning')
    return redirect(url_for('assessment.history'))


@assessment_bp.route('/delete/<int:assessment_id>', methods=['POST'])
@login_required
def delete_assessment(assessment_id):
    """Delete an assessment."""
    from ..models.assessment import Assessment
    from ..app import db
    
    assessment = Assessment.query.filter_by(
        id=assessment_id,
        user_id=current_user.id
    ).first_or_404()
    
    try:
        db.session.delete(assessment)
        
        # Update user statistics
        current_user.total_assessments = max(0, current_user.total_assessments - 1)
        
        db.session.commit()
        
        log_user_activity('assessment_deleted', f'ID: {assessment_id}')
        flash('Assessment deleted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error deleting assessment.', 'danger')
        print(f"Delete assessment error: {e}")
    
    return redirect(url_for('assessment.history'))