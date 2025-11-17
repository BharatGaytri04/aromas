# Development Guide - Preventing Common Errors

This guide helps you catch errors before they cause problems.

## 🛠️ Setup (One-time)

1. **Install development tools:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

## ✅ Daily Workflow

### Before Running the Server

Always run this check first:
```powershell
python manage.py check
```

This will catch:
- Missing commas in lists
- Invalid app references
- Configuration errors
- Import errors

### Before Committing Code

Run the comprehensive check:
```powershell
python check_code.py
```

This checks:
- ✅ Django system configuration
- ✅ Missing migrations
- ✅ Code style (flake8)

## 🔍 Individual Tools

### 1. Django System Check
```powershell
python manage.py check
```
**Catches:** Configuration errors, missing apps, syntax issues

### 2. Flake8 (Linting)
```powershell
flake8 .
```
**Catches:** Syntax errors, style issues, undefined names

### 3. Black (Code Formatting)
```powershell
black .
```
**Auto-fixes:** Code formatting, indentation

### 4. Pylint (Advanced Linting)
```powershell
pylint aromas category
```
**Catches:** Code quality issues, potential bugs

## 💡 Best Practices

### 1. Always Use Trailing Commas
```python
# ✅ Good - easier to add items, prevents errors
INSTALLED_APPS = [
    'django.contrib.admin',
    'category',  # trailing comma
]

# ❌ Bad - easy to forget comma
INSTALLED_APPS = [
    'django.contrib.admin',
    'category'  # missing comma
    'accounts'  # error!
]
```

### 2. Verify Apps Exist
Before adding an app to `INSTALLED_APPS`, make sure it exists:
```powershell
# Check if app directory exists
dir accounts
```

### 3. Use Your IDE Features
- **VS Code/Cursor**: Install Python extension for real-time error detection
- Enable "Python: Linting" in settings
- Enable "Format on Save"

### 4. Test After Changes
After modifying `settings.py`, always run:
```powershell
python manage.py check
```

## 🚨 Common Errors & Prevention

| Error | Prevention |
|-------|-----------|
| Missing comma in list | Use trailing commas, run `python manage.py check` |
| Non-existent app | Verify app exists before adding to `INSTALLED_APPS` |
| Import errors | Run `flake8` to catch undefined imports |
| Syntax errors | IDE will highlight, or run `python -m py_compile file.py` |

## 📝 Quick Reference

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Check Django setup
python manage.py check

# Run all checks
python check_code.py

# Format code
black .

# Lint code
flake8 .

# Run server
python manage.py runserver
```

## 🎯 IDE Setup (VS Code/Cursor)

Add to `.vscode/settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.linting.pylintEnabled": false
}
```

This will show errors in real-time as you type!

