# Luanda Feeds Centre - Installation Guide

## System Requirements

### For Development
- Python 3.10 or higher
- Windows, macOS, or Linux
- Web browser (Chrome, Firefox, Edge, or Safari)

### For Production (Standalone)
- Windows 10 or higher
- Chrome or Edge browser installed
- 500MB disk space

## Installation Steps

### Option 1: Development Installation

1. **Extract the Archive**
   ```
   Extract LuandaFeedsCentre.zip to a folder
   ```

2. **Install Python**
   - Download Python from https://python.org
   - During installation, check "Add Python to PATH"
   - Verify: Open CMD and type `python --version`

3. **Install Dependencies**
   - Open Command Prompt in the project folder
   - Run:
     ```
     pip install -r requirements.txt
     ```

4. **Initialize Database**
   ```
   python manage.py migrate
   ```

5. **Populate Sample Data (Optional)**
   ```
   python populate_inventory.py
   ```

6. **Run the Application**
   ```
   python run.py
   ```

   Or for development:
   ```
   python manage.py runserver
   ```

7. **Access the Application**
   - Browser will open automatically to http://127.0.0.1:8000
   - Or manually open your browser to that address

### Option 2: Standalone Executable

1. **Locate the Executable**
   - If you received a pre-built package, extract it
   - Run `LuandaFeedsCentre.exe`

2. **First Run**
   - The application will open automatically
   - If it's the first time, you'll need to run migrations:
     ```
     python manage.py migrate
     python populate_inventory.py
     ```

## Initial Setup

### Creating Admin User

1. After installation, create an admin account:
   ```
   python manage.py createsuperuser
   ```
2. Follow the prompts to set username and password

### Default Credentials

If you ran the populate script:
| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Superuser |
| manager | manager123 | Manager |
| cashier1 | cashier123 | Cashier |
| inventory | inventory123 | Inventory Manager |

**IMPORTANT**: Change these passwords after first login!

## Configuration

### Database Location

The SQLite database (`db.sqlite3`) is stored in the application folder. To move data:

1. Close the application
2. Copy `db.sqlite3` to the new location
3. Update `settings.py` if needed:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': 'new/path/to/db.sqlite3',
       }
   }
   ```

### Currency Settings

To change the currency symbol, edit `settings.py`:
```python
CURRENCY_SYMBOL = 'KES'  # Change to your currency
```

### Timezone

The system uses Africa/Nairobi timezone by default. To change:
```python
TIME_ZONE = 'Africa/Nairobi'  # Your timezone
```

## Troubleshooting

### Application Won't Start

1. **Check Python version**
   ```
   python --version
   ```
   Should be 3.10 or higher

2. **Reinstall dependencies**
   ```
   pip install -r requirements.txt --force-reinstall
   ```

3. **Check port availability**
   - Another application might be using port 8000
   - Change port in run.py or use:
     ```
     python manage.py runserver 8080
     ```

### Database Errors

1. **Backup your database first**
2. **Reset migrations**
   ```
   python manage.py migrate --reset
   ```

### Browser Issues

- Ensure Chrome or Edge is installed
- Check if browser can open local URLs
- Disable browser extensions if causing issues

## Data Backup

### Manual Backup

1. Stop the application
2. Copy the entire application folder
3. Store in a safe location

### What to Back Up
- `db.sqlite3` - All your data
- `media/` folder if exists (uploaded files)

### Restoring Backup

1. Replace current files with backup
2. Restart application

## Updates

To update the application:

1. Backup your database
2. Stop the application
3. Replace files (keep `db.sqlite3`)
4. Run migrations if needed:
   ```
   python manage.py migrate
   ```
5. Restart

## Support

For installation support:
- Email: support@luandafeeds.co.ke
- Phone: [Contact number]

## Uninstalling

1. Close the application
2. Delete the application folder
3. Delete any shortcuts
4. Optionally delete user data:
   - `browser_profile/` folder
   - `app.log` file
   - `db.sqlite3` if no longer needed
