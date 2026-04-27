# Luanda Feeds Centre - Agrovet Automation Software

A comprehensive supermarket automation system for **Luanda Feeds Centre** in Kenya. This desktop application manages sales transactions, inventory, pricing, and reporting for an agrovet business.

## Features

- **Point of Sale (POS)**: Fast checkout with barcode/item search, cart management, automatic change calculation
- **Inventory Management**: Track stock levels, add/edit items, adjust stock with reasons
- **Price Management**: Update prices with full audit trail
- **Manager Dashboard**: Real-time analytics, low stock alerts, top sellers, revenue tracking
- **Sales Reporting**: Date-range reports with PDF and Excel export
- **User Management**: Role-based access (Cashier, Inventory Manager, Manager)
- **Single-Page Receipt Printing**: Browser-based receipt with print optimization

## Tech Stack

- **Backend**: Django 4.2 (LTS), Python 3.13
- **Database**: SQLite (file-based, portable)
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Production Server**: Waitress
- **Static Files**: WhiteNoise
- **Export**: ReportLab (PDF), OpenPyXL (Excel)
- **Packaging**: PyInstaller (Windows executable)

## Quick Start

### Prerequisites

- Python 3.10+
- Windows (for standalone executable)

### Installation

1. Clone or download the project

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Populate sample data:
```bash
python populate_inventory.py
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Open browser at `http://127.0.0.1:8000`

### Default Login Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Superuser |
| manager | manager123 | Manager |
| cashier1 | cashier123 | Cashier |
| inventory | inventory123 | Inventory Manager |

## Building Standalone Executable

To create a Windows executable:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Run PyInstaller:
```bash
pyinstaller LuandaFeeds.spec --clean
```

3. The executable will be in `dist/LuandaFeedsCentre/`

## Project Structure

```
luanda_feeds/
├── luanda_feeds/          # Main Django project
│   ├── settings.py        # Configuration
│   ├── urls.py           # URL routing
│   ├── wsgi.py           # WSGI application
│   └── context_processors.py
├── users/                # User authentication & management
├── inventory/            # Inventory & stock management
├── sales/                # POS & transactions
├── reports/              # Reporting & exports
├── templates/            # HTML templates
├── static/               # CSS & JS files
├── run.py                # Standalone entry point
├── populate_inventory.py # Sample data script
├── requirements.txt      # Dependencies
└── LuandaFeeds.spec      # PyInstaller config
```

## User Roles

- **Cashier**: POS access, view own transactions
- **Inventory Manager**: Inventory management, stock adjustments
- **Manager**: Full dashboard, reports, price management, user management

Superusers can log in as any role by selecting at login.

## License

Proprietary - Luanda Feeds Centre

## Support

For support, contact Luanda Feeds Centre IT Department.
