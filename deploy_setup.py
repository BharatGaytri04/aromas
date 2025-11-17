"""
Helper script to set up production environment variables
Run this before deploying to production
"""
import secrets
import os

def generate_secret_key():
    """Generate a secure secret key for Django"""
    return secrets.token_urlsafe(50)

def create_env_file():
    """Create .env file with production settings"""
    if os.path.exists('.env'):
        response = input(".env file already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Keeping existing .env file")
            return
    
    secret_key = generate_secret_key()
    
    env_content = f"""# Django Settings
SECRET_KEY={secret_key}
DEBUG=False

# Database (PostgreSQL for production)
DB_NAME=aromas_db
DB_USER=aromas_user
DB_PASSWORD=CHANGE_THIS_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@treandy.in

# Domain
ALLOWED_HOSTS=treandy.in,www.treandy.in
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with production settings")
    print("⚠️  IMPORTANT: Update the database password and email settings!")

if __name__ == "__main__":
    print("=" * 60)
    print("Production Environment Setup")
    print("=" * 60)
    create_env_file()

