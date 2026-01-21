## Project Structure
### This is a simple note taking recorder system, where all users can add records, ,and all users write comments on each others records.

### Tech stack:
- Python
- Flask
- MongoDB
- HTMML
- Tailwind CSS
- Nodejs

```
Project/
├── app.py                    # Main application entry point
├── config.py                 # Configuration management
│
├── models/                   # Data layer
│   ├── __init__.py
│   ├── database.py          # MongoDB connection (Singleton)
│   ├── user_model.py        # User authentication & management
│   ├── record_model.py      # Record CRUD operations
│   └── comment_model.py     # Comment CRUD operations
│
├── routes/                   # Route handlers (Blueprints)
│   ├── __init__.py
│   ├── auth_routes.py       # Authentication endpoints
│   ├── record_routes.py     # Record CRUD endpoints
│   ├── comment_routes.py    # Comment CRUD endpoints
│   └── report_routes.py     # Analytics & PDF export
│
├── templates/                # HTML templates
│   ├── login.html
│   ├── signup.html
│   ├── index.html           # Dashboard
│   ├── add.html             # Add record
│   ├── edit.html            # Edit record
│   ├── view_record.html     # View record with comments
│   └── reports.html         # Analytics dashboard
│
├── static/                   # Static files (CSS, JS, images)
│
└── README.md
```
