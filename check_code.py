#!/usr/bin/env python
"""
Quick code quality check script.
Run this before committing code to catch common errors.
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return True if successful."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}:")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Run all code quality checks."""
    print("🔍 Running code quality checks...")
    
    checks_passed = []
    
    # Check for syntax errors
    checks_passed.append(
        run_command("python manage.py check", "Django system check")
    )
    
    # Check for missing migrations
    checks_passed.append(
        run_command("python manage.py makemigrations --check --dry-run", "Checking for missing migrations")
    )
    
    # Run flake8
    checks_passed.append(
        run_command("flake8 .", "Flake8 linting")
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    if all(checks_passed):
        print("✅ All checks passed!")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

