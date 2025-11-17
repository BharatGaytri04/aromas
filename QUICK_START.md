# 🚀 Quick Start - Prevent Errors

## ⚡ Before Running Server (ALWAYS DO THIS!)

```powershell
python manage.py check
```

**This catches 90% of errors!** Run it every time before starting the server.

## 📋 Complete Setup (One-time)

```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Install tools (already done!)
pip install -r requirements.txt

# 3. Test it works
python manage.py check
```

## ✅ Daily Workflow

### Option 1: Quick Check (Recommended)
```powershell
python manage.py check
```

### Option 2: Full Check (Before committing)
```powershell
python check_code.py
```

## 🎯 What Each Tool Catches

| Tool | Command | Catches |
|------|---------|---------|
| **Django Check** | `python manage.py check` | Missing commas, invalid apps, config errors |
| **Flake8** | `flake8 .` | Syntax errors, undefined names, style issues |
| **Black** | `black .` | Auto-fixes formatting |

## 💡 Pro Tips

1. **Always use trailing commas** in lists:
   ```python
   INSTALLED_APPS = [
       'category',  # ← trailing comma prevents errors
   ]
   ```

2. **Verify apps exist** before adding to `INSTALLED_APPS`

3. **Run `python manage.py check`** after editing `settings.py`

4. **Enable IDE linting** - Your editor will show errors in real-time!

## 📖 Full Guide

See `DEVELOPMENT_GUIDE.md` for detailed instructions.

