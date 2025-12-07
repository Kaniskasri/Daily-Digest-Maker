"""Setup script to initialize the Daily Digest Maker project."""
import os
import sys


def create_directories():
    """Create necessary directories."""
    directories = [
        'logs',
        'credentials',
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}/")
        else:
            print(f"  Directory already exists: {directory}/")


def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✓ Created .env file from .env.example")
            print("  Please edit .env with your credentials")
        else:
            print("✗ .env.example not found")
    else:
        print("  .env file already exists")


def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        print(f"  Current version: {sys.version}")
        return False
    else:
        print(f"✓ Python version: {sys.version.split()[0]}")
        return True


def main():
    """Run setup."""
    print("=" * 60)
    print("Daily Digest Maker - Project Setup")
    print("=" * 60)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print()
    print("Creating directories...")
    create_directories()
    
    print()
    print("Setting up configuration...")
    create_env_file()
    
    print()
    print("=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Edit .env file with your credentials")
    print("3. Run the digest: python main.py")
    print("4. Run tests: python run_tests.py")
    print()


if __name__ == "__main__":
    main()
