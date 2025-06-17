from flask import Blueprint, request, jsonify, session, render_template
from auth import auth_manager

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    
    if not all([username, email, password]):
        return jsonify({'success': False, 'message': 'Username, email, and password are required'}), 400
    
    result = auth_manager.register_user(username, email, password, full_name)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400
    
    result = auth_manager.authenticate_user(username, password)
    
    if result['success']:
        session['user_id'] = result['user_id']
        session['username'] = result['username']
        session['email'] = result['email']
        session['full_name'] = result['full_name']
        return jsonify({'success': True, 'message': 'Login successful', 'user': {
            'username': result['username'],
            'email': result['email'],
            'full_name': result['full_name']
        }})
    else:
        return jsonify(result), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    profile = auth_manager.get_user_profile(session['user_id'])
    if profile:
        return jsonify(profile)
    else:
        return jsonify({'error': 'User not found'}), 404

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    result = auth_manager.update_user_profile(session['user_id'], **data)
    
    if result['success']:
        # Update session data
        if 'username' in data:
            session['username'] = data['username']
        if 'email' in data:
            session['email'] = data['email']
        if 'full_name' in data:
            session['full_name'] = data['full_name']
    
    return jsonify(result)

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not all([current_password, new_password]):
        return jsonify({'success': False, 'message': 'Current and new passwords are required'}), 400
    
    result = auth_manager.change_password(session['user_id'], current_password, new_password)
    return jsonify(result)

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'username': session.get('username'),
                'email': session.get('email'),
                'full_name': session.get('full_name')
            }
        })
    else:
        return jsonify({'authenticated': False})