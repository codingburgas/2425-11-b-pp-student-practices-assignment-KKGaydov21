"""
Admin blueprint for user management and platform administration
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from ..utils.helpers import log_user_activity


admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard with platform overview."""
    from ..models.user import User
    from ..models.assessment import Assessment
    from ..app import db
    
    # Get platform statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(is_admin=True).count()
    total_assessments = Assessment.query.count()
    
    # Recent activity (last 30 days)
    last_30_days = datetime.utcnow() - timedelta(days=30)
    new_users_30d = User.query.filter(User.created_at >= last_30_days).count()
    assessments_30d = Assessment.query.filter(Assessment.timestamp >= last_30_days).count()
    
    # Risk distribution across all users
    risk_stats = db.session.query(
        Assessment.risk_level,
        db.func.count(Assessment.id).label('count')
    ).group_by(Assessment.risk_level).all()
    
    # Top users by assessment count
    top_users = db.session.query(
        User.username,
        User.full_name,
        User.total_assessments,
        User.created_at
    ).order_by(User.total_assessments.desc()).limit(10).all()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'total_assessments': total_assessments,
        'new_users_30d': new_users_30d,
        'assessments_30d': assessments_30d,
        'risk_distribution': dict(risk_stats),
        'top_users': top_users
    }
    
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management page."""
    from ..models.user import User
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status = request.args.get('status', 'all', type=str)
    
    # Build query with filters
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.full_name.contains(search))
        )
    
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    elif status == 'admin':
        query = query.filter_by(is_admin=True)
    
    users_pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', 
                         users=users_pagination,
                         search=search,
                         status=status)


@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """User detail page."""
    from ..models.user import User
    from ..models.assessment import Assessment
    
    user = User.query.get_or_404(user_id)
    
    # Get user's recent assessments
    recent_assessments = Assessment.query.filter_by(user_id=user.id)\
        .order_by(Assessment.timestamp.desc()).limit(10).all()
    
    # Get user statistics
    risk_distribution = user.get_risk_distribution()
    
    return render_template('admin/user_detail.html', 
                         user=user,
                         recent_assessments=recent_assessments,
                         risk_distribution=dict(risk_distribution))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account."""
    from ..models.user import User
    from ..app import db
    
    if user_id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting other admin users unless you're a super admin
    if user.is_admin and not getattr(current_user, 'is_super_admin', False):
        flash('Cannot delete admin users.', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        log_user_activity('admin_user_deleted', f'Deleted user: {username}')
        flash(f'User "{username}" has been deleted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user. Please try again.', 'danger')
        print(f"Error deleting user: {e}")
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status."""
    from ..models.user import User
    from ..app import db
    
    if user_id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    
    try:
        user.is_active = not user.is_active
        status = 'activated' if user.is_active else 'deactivated'
        db.session.commit()
        
        log_user_activity('admin_user_status_changed', 
                         f'{status.title()} user: {user.username}')
        flash(f'User "{user.username}" has been {status}.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating user status.', 'danger')
        print(f"Error toggling user status: {e}")
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/make-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin_status(user_id):
    """Toggle user admin status."""
    from ..models.user import User
    from ..app import db
    
    user = User.query.get_or_404(user_id)
    
    try:
        user.is_admin = not user.is_admin
        status = 'granted' if user.is_admin else 'revoked'
        db.session.commit()
        
        log_user_activity('admin_privilege_changed', 
                         f'Admin privileges {status} for user: {user.username}')
        flash(f'Admin privileges {status} for "{user.username}".', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating admin status.', 'danger')
        print(f"Error toggling admin status: {e}")
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/assessments')
@login_required
@admin_required
def assessments():
    """Assessment management page."""
    from ..models.assessment import Assessment
    from ..models.user import User
    from ..app import db
    
    page = request.args.get('page', 1, type=int)
    risk_level = request.args.get('risk_level', '', type=str)
    user_search = request.args.get('user_search', '', type=str)
    
    # Build query with filters
    query = db.session.query(Assessment, User).join(User)
    
    if risk_level:
        query = query.filter(Assessment.risk_level == risk_level)
    
    if user_search:
        query = query.filter(
            (User.username.contains(user_search)) |
            (User.email.contains(user_search))
        )
    
    assessments_pagination = query.order_by(Assessment.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get unique risk levels for filter dropdown
    risk_levels = db.session.query(Assessment.risk_level.distinct()).all()
    risk_levels = [r[0] for r in risk_levels]
    
    return render_template('admin/assessments.html',
                         assessments=assessments_pagination,
                         risk_levels=risk_levels,
                         current_risk_level=risk_level,
                         user_search=user_search)


@admin_bp.route('/assessments/<int:assessment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_assessment(assessment_id):
    """Delete an assessment (admin only)."""
    from ..models.assessment import Assessment
    from ..models.user import User
    from ..app import db
    
    assessment = Assessment.query.get_or_404(assessment_id)
    user = User.query.get(assessment.user_id)
    
    try:
        db.session.delete(assessment)
        
        # Update user's total assessments count
        if user:
            user.total_assessments = max(0, user.total_assessments - 1)
        
        db.session.commit()
        
        log_user_activity('admin_assessment_deleted', 
                         f'Deleted assessment ID: {assessment_id}')
        flash('Assessment deleted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error deleting assessment.', 'danger')
        print(f"Error deleting assessment: {e}")
    
    return redirect(url_for('admin.assessments'))


@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Advanced analytics and reporting."""
    from ..models.user import User
    from ..models.assessment import Assessment
    from ..app import db
    
    # Time-based statistics
    last_7_days = datetime.utcnow() - timedelta(days=7)
    last_30_days = datetime.utcnow() - timedelta(days=30)
    last_90_days = datetime.utcnow() - timedelta(days=90)
    
    analytics_data = {
        'user_growth': {
            'last_7_days': User.query.filter(User.created_at >= last_7_days).count(),
            'last_30_days': User.query.filter(User.created_at >= last_30_days).count(),
            'last_90_days': User.query.filter(User.created_at >= last_90_days).count(),
        },
        'assessment_activity': {
            'last_7_days': Assessment.query.filter(Assessment.timestamp >= last_7_days).count(),
            'last_30_days': Assessment.query.filter(Assessment.timestamp >= last_30_days).count(),
            'last_90_days': Assessment.query.filter(Assessment.timestamp >= last_90_days).count(),
        },
        'risk_trends': db.session.query(
            Assessment.risk_level,
            db.func.count(Assessment.id).label('count'),
            db.func.avg(Assessment.prediction_probability).label('avg_probability')
        ).group_by(Assessment.risk_level).all(),
        'monthly_registrations': db.session.query(
            db.func.date_trunc('month', User.created_at).label('month'),
            db.func.count(User.id).label('count')
        ).group_by(db.func.date_trunc('month', User.created_at))\
         .order_by('month').limit(12).all()
    }
    
    return render_template('admin/analytics.html', analytics=analytics_data)


@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Admin settings and configuration."""
    return render_template('admin/settings.html')


@admin_bp.route('/create-admin', methods=['GET', 'POST'])
@login_required
@admin_required
def create_admin():
    """Create a new admin user."""
    from ..forms.auth_forms import RegistrationForm
    from ..models.user import User
    from ..app import db
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data.lower(),
                full_name=form.full_name.data,
                is_admin=True
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            log_user_activity('admin_user_created', f'Created admin user: {user.username}')
            flash(f'Admin user "{user.username}" created successfully.', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creating admin user.', 'danger')
            print(f"Error creating admin user: {e}")
    
    return render_template('admin/create_admin.html', form=form)


# API endpoints for admin dashboard
@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API endpoint for admin dashboard statistics."""
    from ..models.user import User
    from ..models.assessment import Assessment
    
    last_24h = datetime.utcnow() - timedelta(hours=24)
    
    stats = {
        'users_last_24h': User.query.filter(User.created_at >= last_24h).count(),
        'assessments_last_24h': Assessment.query.filter(Assessment.timestamp >= last_24h).count(),
        'total_users': User.query.count(),
        'total_assessments': Assessment.query.count(),
        'active_users': User.query.filter_by(is_active=True).count()
    }
    
    return jsonify(stats)