# Smart Records System - Desktop Application

A native desktop application built with Python tkinter, converted from the Flask web version.

## Features

All features from the Flask web application are preserved:

- **User Authentication**: Login and signup with password hashing
- **Record Management**: Create, read, update, and delete records
- **Categorization**: Organize records by category (General, Important, Personal, Work, Other)
- **Status Tracking**: Track record status (Active, Inactive, Completed)
- **Comments System**: Add, edit, and delete comments on records
- **Analytics Dashboard**: View statistics and charts
- **PDF Export**: Export comprehensive reports as PDF

## Requirements

- Python 3.8 or higher
- MongoDB database (same as Flask version)
- Dependencies listed in `requirements.txt`

## Installation

1. **Navigate to the tkinter_app directory:**
   ```bash
   cd tkinter_app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure MongoDB is running and configured:**
   - The app uses the same `.env` file and `config.py` as the Flask version
   - Make sure `MONGODB_URI` is set in the parent directory's `.env` file

## Running the Application

```bash
python main.py
```

The application window will open, starting at the login screen.

## Keyboard Shortcuts

- **Ctrl+N** (Cmd+N on macOS): Add new record
- **Ctrl+R** (Cmd+R on macOS): Open reports/analytics
- **Ctrl+Q** (Cmd+Q on macOS): Quit application
- **Escape**: Return to dashboard

## Project Structure

```
tkinter_app/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── gui/
│   ├── app_controller.py       # Main window and navigation
│   ├── theme.py                # Colors and styling
│   ├── widgets/                # Reusable components
│   │   ├── notification.py     # Toast notifications
│   │   ├── data_table.py       # Table widget
│   │   └── chart_widget.py     # Charts (matplotlib)
│   └── views/                  # Application screens
│       ├── base_view.py        # Base class for all views
│       ├── login_view.py       # Login screen
│       ├── signup_view.py      # Registration screen
│       ├── dashboard_view.py   # Main dashboard
│       ├── add_record_view.py  # Create record form
│       ├── edit_record_view.py # Edit record form
│       ├── view_record_view.py # View record with comments
│       └── reports_view.py     # Analytics and reports
└── utils/
    ├── session.py              # Session management
    └── validators.py           # Form validation
```

## Architecture

The application follows a **Model-View-Controller (MVC)** pattern:

- **Models**: Shared with Flask app (in parent `models/` directory)
  - `database.py`: MongoDB connection
  - `user_model.py`: User authentication
  - `record_model.py`: Record CRUD operations
  - `comment_model.py`: Comment operations

- **Views**: Tkinter GUI screens (in `gui/views/`)
  - Each view is a self-contained screen
  - Inherits from `BaseView`

- **Controller**: `AppController` (in `gui/app_controller.py`)
  - Manages view switching
  - Handles session state
  - Coordinates navigation

## Color Scheme

The application maintains the same color scheme as the Flask version:

- **Primary**: Gray-900 (#111827)
- **Success**: Green-800 (#166534) - Create/Save actions
- **Info**: Blue-600 (#2563eb) - View actions
- **Danger**: Red-600 (#dc2626) - Delete actions
- **Background**: Gray-50 (#f9fafb)

## Differences from Flask Version

### Advantages
- **Native Desktop App**: No browser required
- **Offline After Initial Setup**: Runs locally once database is configured
- **Better Performance**: Direct UI rendering without HTTP overhead
- **Native Notifications**: Toast-style notifications integrated into UI

### Similarities
- **Same Business Logic**: Uses identical models from Flask app
- **Same Database**: Connects to the same MongoDB instance
- **Same Features**: All functionality preserved
- **Same Color Scheme**: Matching visual design

## Troubleshooting

### "ModuleNotFoundError: No module named 'matplotlib'"
Install matplotlib:
```bash
pip install matplotlib
```

### "ModuleNotFoundError: No module named 'models'"
Ensure you're running from the `tkinter_app` directory and the parent `models/` directory exists.

### "Connection error to MongoDB"
Check that:
1. MongoDB is running
2. `MONGODB_URI` is correctly set in parent `.env` file
3. Network connectivity to MongoDB instance

### Fonts look wrong
The app automatically selects platform-appropriate fonts:
- macOS: SF Pro Display
- Windows: Segoe UI
- Linux: Ubuntu

If fonts render incorrectly, they'll fall back to system defaults.

## Development

### Adding a New View

1. Create new file in `gui/views/`
2. Inherit from `BaseView`
3. Implement `__init__`, `_build_ui`, and `refresh` methods
4. Add to `AppController._initialize_views()`

Example:
```python
from gui.views.base_view import BaseView
from gui.theme import Theme

class MyNewView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build_ui()

    def _build_ui(self):
        # Build your UI here
        pass

    def refresh(self, **kwargs):
        # Refresh data when view becomes active
        pass
```

## Notes

- The Flask application in the parent directory remains fully functional
- Both applications can be run independently
- They share the same database and models layer
- User accounts and data are shared between both versions
