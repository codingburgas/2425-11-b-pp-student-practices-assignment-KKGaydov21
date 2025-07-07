"""
Dashboard blueprint for user statistics and overview
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from ..utils.helpers import create_trend_chart, log_user_activity


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page."""
    from ..models.assessment import Assessment
    from ..app import db
    
    # Get user's recent assessments
    recent_assessments = current_user.get_recent_assessments(limit=10)
    
    # Get statistics
    total_assessments = current_user.total_assessments
    risk_distribution = current_user.get_risk_distribution()
    
    # Calculate additional statistics
    last_30_days = datetime.utcnow() - timedelta(days=30)
    recent_count = Assessment.query.filter(
        Assessment.user_id == current_user.id,
        Assessment.timestamp >= last_30_days
    ).count()
    
    # Get average risk probability
    avg_risk = db.session.query(
        db.func.avg(Assessment.prediction_probability)
    ).filter_by(user_id=current_user.id).scalar()
    
    avg_risk = round(avg_risk * 100, 1) if avg_risk else 0
    
    # Create trend chart if user has assessments
    trend_chart = None
    if recent_assessments:
        trend_chart = create_trend_chart(recent_assessments)
    
    stats = {
        'total_assessments': total_assessments,
        'recent_count': recent_count,
        'avg_risk': avg_risk,
        'risk_distribution': dict(risk_distribution) if risk_distribution else {}
    }
    
    return render_template('dashboard/index.html',
                         recent_assessments=recent_assessments,
                         stats=stats,
                         trend_chart=trend_chart)


@dashboard_bp.route('/analytics')
@login_required
def analytics():
    """Advanced analytics page."""
    from ..models.assessment import Assessment
    from ..app import db
    
    # Time-based analysis
    assessments_by_month = db.session.query(
        db.func.date_trunc('month', Assessment.timestamp).label('month'),
        db.func.count(Assessment.id).label('count')
    ).filter_by(user_id=current_user.id)\
     .group_by(db.func.date_trunc('month', Assessment.timestamp))\
     .order_by('month').all()
    
    # Risk level trends
    risk_trends = db.session.query(
        Assessment.risk_level,
        db.func.avg(Assessment.prediction_probability).label('avg_prob'),
        db.func.count(Assessment.id).label('count')
    ).filter_by(user_id=current_user.id)\
     .group_by(Assessment.risk_level).all()
    
    # Feature analysis (average values for each measurement)
    feature_averages = db.session.query(
        db.func.avg(Assessment.radius_mean).label('avg_radius'),
        db.func.avg(Assessment.texture_mean).label('avg_texture'),
        db.func.avg(Assessment.perimeter_mean).label('avg_perimeter'),
        db.func.avg(Assessment.area_mean).label('avg_area'),
        db.func.avg(Assessment.concave_points_mean).label('avg_concave'),
        db.func.avg(Assessment.symmetry_mean).label('avg_symmetry')
    ).filter_by(user_id=current_user.id).first()
    
    analytics_data = {
        'monthly_assessments': [
            {'month': m.strftime('%Y-%m'), 'count': c} 
            for m, c in assessments_by_month
        ],
        'risk_trends': [
            {'risk_level': r, 'avg_probability': round(p*100, 1), 'count': c}
            for r, p, c in risk_trends
        ],
        'feature_averages': {
            'radius_mean': round(feature_averages.avg_radius, 2) if feature_averages.avg_radius else 0,
            'texture_mean': round(feature_averages.avg_texture, 2) if feature_averages.avg_texture else 0,
            'perimeter_mean': round(feature_averages.avg_perimeter, 2) if feature_averages.avg_perimeter else 0,
            'area_mean': round(feature_averages.avg_area, 2) if feature_averages.avg_area else 0,
            'concave_points_mean': round(feature_averages.avg_concave, 3) if feature_averages.avg_concave else 0,
            'symmetry_mean': round(feature_averages.avg_symmetry, 3) if feature_averages.avg_symmetry else 0
        }
    }
    
    return render_template('dashboard/analytics.html', analytics=analytics_data)


@dashboard_bp.route('/settings')
@login_required
def settings():
    """User settings and preferences page."""
    return render_template('dashboard/settings.html')


@dashboard_bp.route('/notifications')
@login_required
def notifications():
    """User notifications and alerts."""
    # In a real app, you might have a notifications system
    notifications = [
        {
            'id': 1,
            'type': 'info',
            'title': 'Welcome to the platform!',
            'message': 'Complete your first assessment to get started.',
            'timestamp': datetime.utcnow() - timedelta(hours=1),
            'read': False
        }
    ]
    
    return render_template('dashboard/notifications.html', notifications=notifications)


@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for dashboard statistics."""
    from ..models.assessment import Assessment
    from ..app import db
    
    # Get recent statistics
    last_7_days = datetime.utcnow() - timedelta(days=7)
    last_30_days = datetime.utcnow() - timedelta(days=30)
    
    stats = {
        'total_assessments': current_user.total_assessments,
        'last_7_days': Assessment.query.filter(
            Assessment.user_id == current_user.id,
            Assessment.timestamp >= last_7_days
        ).count(),
        'last_30_days': Assessment.query.filter(
            Assessment.user_id == current_user.id,
            Assessment.timestamp >= last_30_days
        ).count(),
        'avg_risk_last_30_days': db.session.query(
            db.func.avg(Assessment.prediction_probability)
        ).filter(
            Assessment.user_id == current_user.id,
            Assessment.timestamp >= last_30_days
        ).scalar() or 0
    }
    
    # Convert average to percentage
    stats['avg_risk_last_30_days'] = round(stats['avg_risk_last_30_days'] * 100, 1)
    
    return jsonify(stats)


@dashboard_bp.route('/api/recent-assessments')
@login_required
def api_recent_assessments():
    """API endpoint for recent assessments."""
    limit = request.args.get('limit', 10, type=int)
    assessments = current_user.get_recent_assessments(limit=limit)
    
    return jsonify([assessment.to_dict() for assessment in assessments])


@dashboard_bp.route('/export/dashboard-report')
@login_required
def export_dashboard_report():
    """Export comprehensive dashboard report."""
    from ..models.assessment import Assessment
    import io
    from flask import Response
    from datetime import datetime
    
    # Generate comprehensive report
    report_lines = [
        f"Cancer Risk Assessment Dashboard Report",
        f"Generated for: {current_user.full_name or current_user.username}",
        f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        f"",
        f"Summary Statistics:",
        f"- Total Assessments: {current_user.total_assessments}",
        f"- Member Since: {current_user.created_at.strftime('%Y-%m-%d')}",
        f"- Last Assessment: {current_user.last_assessment.strftime('%Y-%m-%d') if current_user.last_assessment else 'None'}",
        f"",
        f"Risk Distribution:"
    ]
    
    # Add risk distribution
    risk_distribution = current_user.get_risk_distribution()
    for risk_level, count in risk_distribution:
        report_lines.append(f"- {risk_level}: {count} assessments")
    
    report_lines.extend([
        f"",
        f"Recent Assessments:",
        f"Date\t\tRisk Level\t\tProbability"
    ])
    
    # Add recent assessments
    recent_assessments = current_user.get_recent_assessments(limit=20)
    for assessment in recent_assessments:
        report_lines.append(
            f"{assessment.timestamp.strftime('%Y-%m-%d %H:%M')}\t"
            f"{assessment.risk_level}\t\t"
            f"{assessment.probability_percentage}%"
        )
    
    report_content = '\n'.join(report_lines)
    
    return Response(
        report_content,
        mimetype='text/plain',
        headers={
            'Content-Disposition': 'attachment; filename=dashboard_report.txt'
        }
    )