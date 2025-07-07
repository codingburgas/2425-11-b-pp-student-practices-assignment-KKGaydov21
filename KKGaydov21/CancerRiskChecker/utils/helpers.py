"""
Helper functions and utilities
"""
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import flash, request, jsonify
from flask_login import current_user
import plotly.graph_objects as go
import plotly.utils


def login_required_json(f):
    """Decorator for API endpoints requiring authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator for admin-only endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('Admin access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def flash_errors(form):
    """Flash form validation errors."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", 'error')


def create_gauge_chart(probability, title="Risk Probability"):
    """Create a Plotly gauge chart for risk visualization."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{title} (%)", 'font': {'size': 24, 'color': '#2d3748'}},
        delta={'reference': 50, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': "#2d3748"},
            'bar': {'color': "#667eea", 'thickness': 0.8},
            'steps': [
                {'range': [0, 25], 'color': "#c6f6d5"},   # Very Low
                {'range': [25, 45], 'color': "#bee3f8"},  # Low
                {'range': [45, 70], 'color': "#fbb6ce"},  # Moderate
                {'range': [70, 100], 'color': "#fed7d7"}  # High
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
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def create_trend_chart(assessments):
    """Create a trend chart for assessment history."""
    if not assessments:
        return None
    
    dates = [a.timestamp for a in assessments]
    probabilities = [a.prediction_probability * 100 for a in assessments]
    risk_levels = [a.risk_level for a in assessments]
    
    fig = go.Figure()
    
    # Add probability line
    fig.add_trace(go.Scatter(
        x=dates,
        y=probabilities,
        mode='lines+markers',
        name='Risk Probability',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8)
    ))
    
    # Add risk level annotations
    colors = {'Very Low': '#28a745', 'Low': '#17a2b8', 'Moderate': '#ffc107', 'High': '#dc3545'}
    for i, (date, prob, risk) in enumerate(zip(dates, probabilities, risk_levels)):
        fig.add_annotation(
            x=date,
            y=prob,
            text=risk,
            showarrow=True,
            arrowhead=2,
            arrowcolor=colors.get(risk, '#6c757d'),
            bgcolor=colors.get(risk, '#6c757d'),
            bordercolor="white",
            borderwidth=2,
            font=dict(color="white", size=10)
        )
    
    fig.update_layout(
        title="Assessment History Trend",
        xaxis_title="Date",
        yaxis_title="Risk Probability (%)",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#2d3748", 'family': "Arial"}
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def format_datetime(dt, format_str='%Y-%m-%d %H:%M'):
    """Format datetime object to string."""
    if dt is None:
        return 'N/A'
    return dt.strftime(format_str)


def format_percentage(value, decimals=1):
    """Format value as percentage."""
    if value is None:
        return 'N/A'
    return f"{value * 100:.{decimals}f}%"


def time_ago(dt):
    """Return human-readable time difference."""
    if dt is None:
        return 'Never'
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"


def get_risk_color_class(risk_level):
    """Get Bootstrap color class for risk level."""
    colors = {
        'Very Low': 'success',
        'Low': 'primary',
        'Moderate': 'warning',
        'High': 'danger'
    }
    return colors.get(risk_level, 'secondary')


def sanitize_input(data):
    """Sanitize user input data."""
    if isinstance(data, str):
        # Basic HTML tag removal
        import re
        data = re.sub(r'<[^>]+>', '', data)
        data = data.strip()
    elif isinstance(data, dict):
        data = {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        data = [sanitize_input(item) for item in data]
    
    return data


def generate_assessment_id():
    """Generate unique assessment ID."""
    import uuid
    return str(uuid.uuid4())[:8].upper()


def log_user_activity(activity, details=None):
    """Log user activity for audit purposes."""
    if current_user.is_authenticated:
        # In a production app, you might want to store this in a separate table
        print(f"User {current_user.username} - {activity}: {details}")


def validate_file_upload(file, allowed_extensions=None, max_size_mb=5):
    """Validate uploaded file."""
    if allowed_extensions is None:
        allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv'}
    
    if file.filename == '':
        return False, "No file selected"
    
    # Check extension
    if '.' not in file.filename:
        return False, "File must have an extension"
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return False, f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    # Check file size (this is a basic check, more sophisticated validation needed for production)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > max_size_mb * 1024 * 1024:
        return False, f"File too large. Maximum size: {max_size_mb}MB"
    
    return True, "Valid file"


def paginate_query(query, page, per_page=20):
    """Helper function for query pagination."""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )


def get_client_ip():
    """Get client IP address."""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']


def rate_limit_key(prefix='rate_limit'):
    """Generate rate limit key for current user/IP."""
    if current_user.is_authenticated:
        return f"{prefix}:user:{current_user.id}"
    else:
        return f"{prefix}:ip:{get_client_ip()}"