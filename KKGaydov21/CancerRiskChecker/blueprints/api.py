"""
API blueprint for REST endpoints and AJAX requests
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from ..utils.helpers import login_required_json, log_user_activity
from ..utils.ml_engine import cancer_predictor


api_bp = Blueprint('api', __name__)


@api_bp.route('/predict', methods=['POST'])
@login_required_json
def predict():
    """API endpoint for cancer risk prediction."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract features
        required_features = [
            'radius_mean', 'texture_mean', 'perimeter_mean',
            'area_mean', 'concave_points_mean', 'symmetry_mean'
        ]
        
        features = []
        for feature in required_features:
            if feature not in data:
                return jsonify({'error': f'Missing feature: {feature}'}), 400
            features.append(float(data[feature]))
        
        # Validate input
        is_valid, message = cancer_predictor.validate_input(features)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Make prediction
        result = cancer_predictor.predict(features)
        
        if result:
            log_user_activity('api_prediction', f'Risk: {result["risk_level"]}')
            return jsonify({
                'success': True,
                'prediction': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({'error': 'Prediction failed'}), 500
            
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        print(f"API prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/assessments', methods=['GET'])
@login_required_json
def get_assessments():
    """API endpoint to get user's assessments."""
    from ..models.assessment import Assessment
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)  # Max 50 per page
        
        assessments = Assessment.query.filter_by(user_id=current_user.id)\
            .order_by(Assessment.timestamp.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'assessments': [assessment.to_dict() for assessment in assessments.items],
            'total': assessments.total,
            'pages': assessments.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        print(f"API get assessments error: {e}")
        return jsonify({'error': 'Failed to retrieve assessments'}), 500


@api_bp.route('/assessments/<int:assessment_id>', methods=['GET'])
@login_required_json
def get_assessment(assessment_id):
    """API endpoint to get a specific assessment."""
    from ..models.assessment import Assessment
    
    try:
        assessment = Assessment.query.filter_by(
            id=assessment_id,
            user_id=current_user.id
        ).first()
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        return jsonify(assessment.to_dict())
        
    except Exception as e:
        print(f"API get assessment error: {e}")
        return jsonify({'error': 'Failed to retrieve assessment'}), 500


@api_bp.route('/assessments/<int:assessment_id>', methods=['DELETE'])
@login_required_json
def delete_assessment(assessment_id):
    """API endpoint to delete an assessment."""
    from ..models.assessment import Assessment
    from ..app import db
    
    try:
        assessment = Assessment.query.filter_by(
            id=assessment_id,
            user_id=current_user.id
        ).first()
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        db.session.delete(assessment)
        current_user.total_assessments = max(0, current_user.total_assessments - 1)
        db.session.commit()
        
        log_user_activity('api_assessment_deleted', f'ID: {assessment_id}')
        return jsonify({'message': 'Assessment deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"API delete assessment error: {e}")
        return jsonify({'error': 'Failed to delete assessment'}), 500


@api_bp.route('/statistics', methods=['GET'])
@login_required_json
def get_statistics():
    """API endpoint for user statistics."""
    try:
        from ..models.assessment import Assessment
        from ..app import db
        from datetime import timedelta
        
        # Calculate various statistics
        total_assessments = current_user.total_assessments
        
        # Last 30 days
        last_30_days = datetime.utcnow() - timedelta(days=30)
        recent_count = Assessment.query.filter(
            Assessment.user_id == current_user.id,
            Assessment.timestamp >= last_30_days
        ).count()
        
        # Average risk
        avg_risk = db.session.query(
            db.func.avg(Assessment.prediction_probability)
        ).filter_by(user_id=current_user.id).scalar()
        
        # Risk distribution
        risk_distribution = dict(current_user.get_risk_distribution())
        
        # Latest assessment
        latest_assessment = Assessment.query.filter_by(user_id=current_user.id)\
            .order_by(Assessment.timestamp.desc()).first()
        
        stats = {
            'total_assessments': total_assessments,
            'assessments_last_30_days': recent_count,
            'average_risk_percentage': round(avg_risk * 100, 1) if avg_risk else 0,
            'risk_distribution': risk_distribution,
            'latest_assessment': latest_assessment.to_dict() if latest_assessment else None,
            'member_since': current_user.created_at.isoformat(),
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"API statistics error: {e}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500


@api_bp.route('/model/info', methods=['GET'])
@login_required_json
def get_model_info():
    """API endpoint for ML model information."""
    try:
        # Load model to get metadata
        cancer_predictor.load_model()
        
        feature_importance = cancer_predictor.get_feature_importance()
        
        model_info = {
            'version': cancer_predictor.version,
            'feature_names': cancer_predictor.feature_names,
            'feature_importance': feature_importance,
            'model_type': 'Logistic Regression',
            'input_features': 6,
            'risk_levels': ['Very Low', 'Low', 'Moderate', 'High']
        }
        
        return jsonify(model_info)
        
    except Exception as e:
        print(f"API model info error: {e}")
        return jsonify({'error': 'Failed to retrieve model information'}), 500


@api_bp.route('/validate', methods=['POST'])
@login_required_json
def validate_input():
    """API endpoint to validate assessment input."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'valid': False, 'errors': ['No data provided']}), 400
        
        # Extract features
        required_features = [
            'radius_mean', 'texture_mean', 'perimeter_mean',
            'area_mean', 'concave_points_mean', 'symmetry_mean'
        ]
        
        errors = []
        features = []
        
        for feature in required_features:
            if feature not in data:
                errors.append(f'Missing feature: {feature}')
            else:
                try:
                    value = float(data[feature])
                    features.append(value)
                except (ValueError, TypeError):
                    errors.append(f'Invalid value for {feature}')
        
        if not errors:
            # Validate ranges
            is_valid, message = cancer_predictor.validate_input(features)
            if not is_valid:
                errors.append(message)
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors
        })
        
    except Exception as e:
        print(f"API validation error: {e}")
        return jsonify({'valid': False, 'errors': ['Validation failed']}), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'cancer-risk-assessment-api',
        'version': '2.0'
    })


# Error handlers for API blueprint
@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400


@api_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401


@api_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403


@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500