from flask import session, request, jsonify, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import uuid
from data.database import SessionLocal, User

class AuthManager:
    def __init__(self):
        pass
    
    def require_auth(self, f):
        """Decorator to require authentication for routes"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            return f(*args, **kwargs)
        return decorated_function
    
    def register_user(self, username, email, password, full_name=None):
        """Register a new user"""
        db = SessionLocal()
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return {'success': False, 'message': 'Username or email already exists'}
            
            # Create new user
            user_id = str(uuid.uuid4())
            hashed_password = generate_password_hash(password)
            
            new_user = User(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=hashed_password,
                full_name=full_name
            )
            
            db.add(new_user)
            db.commit()
            
            return {'success': True, 'message': 'User registered successfully', 'user_id': user_id}
            
        except Exception as e:
            db.rollback()
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
        finally:
            db.close()
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if user and check_password_hash(user.password_hash, password):
                return {
                    'success': True, 
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name
                }
            else:
                return {'success': False, 'message': 'Invalid credentials'}
                
        except Exception as e:
            return {'success': False, 'message': f'Authentication failed: {str(e)}'}
        finally:
            db.close()
    
    def get_user_profile(self, user_id):
        """Get user profile information"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                return {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'created_at': user.created_at.strftime('%Y-%m-%d'),
                    'last_assessment': user.last_assessment.strftime('%Y-%m-%d %H:%M') if user.last_assessment else None,
                    'total_assessments': user.total_assessments
                }
            return None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
        finally:
            db.close()
    
    def update_user_profile(self, user_id, **kwargs):
        """Update user profile"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Update allowed fields
            allowed_fields = ['username', 'email', 'full_name']
            for field, value in kwargs.items():
                if field in allowed_fields and value:
                    setattr(user, field, value)
            
            db.commit()
            return {'success': True, 'message': 'Profile updated successfully'}
            
        except Exception as e:
            db.rollback()
            return {'success': False, 'message': f'Update failed: {str(e)}'}
        finally:
            db.close()
    
    def change_password(self, user_id, current_password, new_password):
        """Change user password"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            if not check_password_hash(user.password_hash, current_password):
                return {'success': False, 'message': 'Current password is incorrect'}
            
            user.password_hash = generate_password_hash(new_password)
            db.commit()
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            db.rollback()
            return {'success': False, 'message': f'Password change failed: {str(e)}'}
        finally:
            db.close()

# Global auth manager instance
auth_manager = AuthManager()