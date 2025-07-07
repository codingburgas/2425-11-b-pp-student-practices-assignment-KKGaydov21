"""
Admin setup utilities for creating initial admin user
"""
from ..models.user import User
from ..app import db


def create_initial_admin():
    """Create initial admin user if none exists."""
    try:
        # Check if any admin users exist
        existing_admin = User.query.filter_by(is_admin=True).first()
        
        if not existing_admin:
            # Create default admin user
            admin_user = User(
                username='admin',
                email='admin@cancerrisktool.com',
                full_name='System Administrator',
                is_admin=True,
                is_active=True
            )
            admin_user.set_password('admin123!')  # Change this in production!

            db.session.add(admin_user)
            db.session.commit()
            
            print("Initial admin user created:")
            print("Username: admin")
            print("Email: admin@cancerrisktool.com")
            print("Password: admin123!")
            print("IMPORTANT: Change the password after first login!")
            
            return admin_user
        else:
            print(f"Admin user already exists: {existing_admin.username}")
            return existing_admin
            
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.session.rollback()
        return None


def setup_admin_permissions():
    """Set up admin permissions and roles."""
    try:
        # Ensure at least one admin exists
        admin_count = User.query.filter_by(is_admin=True).count()
        
        if admin_count == 0:
            return create_initial_admin()
        
        print(f"Found {admin_count} admin user(s)")
        return True
        
    except Exception as e:
        print(f"Error setting up admin permissions: {e}")
        return False


def promote_user_to_admin(username):
    """Promote a user to admin status."""
    try:
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"User '{username}' not found")
            return False
        
        if user.is_admin:
            print(f"User '{username}' is already an admin")
            return True
        
        user.is_admin = True
        db.session.commit()
        
        print(f"User '{username}' promoted to admin successfully")
        return True
        
    except Exception as e:
        print(f"Error promoting user to admin: {e}")
        db.session.rollback()
        return False


def list_admin_users():
    """List all admin users."""
    try:
        admin_users = User.query.filter_by(is_admin=True).all()
        
        if not admin_users:
            print("No admin users found")
            return []
        
        print("Admin users:")
        for admin in admin_users:
            status = "Active" if admin.is_active else "Inactive"
            print(f"- {admin.username} ({admin.email}) - {status}")
        
        return admin_users
        
    except Exception as e:
        print(f"Error listing admin users: {e}")
        return []


def exec():
    from ..app import create_app
    
    app = create_app()
    with app.app_context():
        print("Setting up admin users...")
        create_initial_admin()
        list_admin_users()