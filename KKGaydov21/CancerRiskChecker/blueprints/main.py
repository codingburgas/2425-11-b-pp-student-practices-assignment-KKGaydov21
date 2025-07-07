"""
Main blueprint for public pages and general routes
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from ..models.assessment import Assessment


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page with platform overview."""
    # Get some basic statistics for the homepage
    stats = {
        'total_assessments': Assessment.query.count(),
        'total_users': 0,  # Will be calculated if needed
        'success_rate': 95.2  # Example metric
    }
    
    return render_template('index.html', stats=stats)


@main_bp.route('/about')
def about():
    """About page with platform information."""
    return render_template('pages/about.html')


@main_bp.route('/privacy')
def privacy():
    """Privacy policy page."""
    return render_template('pages/privacy.html')


@main_bp.route('/terms')
def terms():
    """Terms of service page."""
    return render_template('pages/terms.html')


@main_bp.route('/contact')
def contact():
    """Contact information page."""
    return render_template('pages/contact.html')


@main_bp.route('/faq')
def faq():
    """Frequently asked questions page."""
    return render_template('pages/faq.html')


@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'service': 'cancer-risk-assessment',
        'version': '2.0'
    })


@main_bp.route('/sitemap.xml')
def sitemap():
    """Generate sitemap for SEO."""
    from flask import Response, url_for
    
    pages = [
        'main.index',
        'main.about',
        'main.privacy',
        'main.terms',
        'main.contact',
        'main.faq',
        'auth.login',
        'auth.register'
    ]
    
    sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for page in pages:
        sitemap_xml.append('<url>')
        sitemap_xml.append(f'<loc>{request.url_root[:-1]}{url_for(page)}</loc>')
        sitemap_xml.append('<changefreq>weekly</changefreq>')
        sitemap_xml.append('<priority>0.8</priority>')
        sitemap_xml.append('</url>')
    
    sitemap_xml.append('</urlset>')
    
    response = Response('\n'.join(sitemap_xml), mimetype='application/xml')
    return response


@main_bp.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    from ..app import db
    db.session.rollback()
    return render_template('errors/500.html'), 500


@main_bp.app_errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors."""
    return render_template('errors/403.html'), 403