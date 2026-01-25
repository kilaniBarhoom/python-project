"""
Main application controller
Manages window, views, navigation, and state
"""
import tkinter as tk
from tkinter import messagebox
import platform
from gui.theme import Theme
from gui.widgets.notification import Notification
from utils.session import SessionManager


class AppController(tk.Tk):
    """
    Main application window and controller
    Manages view switching, session state, and navigation
    """

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Smart Records System")
        self.geometry("1280x800")
        self.minsize(1200, 700)

        # Center window on screen
        self._center_window()

        # Configure window background
        self.configure(bg=Theme.BG_LIGHT)

        # Initialize session manager
        self.session = SessionManager()

        # Create notification system
        self.notification = Notification(self)

        # Create menu bar
        self._create_menu_bar()

        # Create container for views
        self.container = tk.Frame(self, bg=Theme.BG_LIGHT)
        self.container.pack(fill='both', expand=True)

        # Dictionary to store views
        self.views = {}

        # Initialize all views
        self._initialize_views()

        # Configure keyboard shortcuts
        self._setup_keyboard_shortcuts()

        # Start with login view
        self.show_view('login')

    def _center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = 1280
        height = 800
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(
            label="Dashboard",
            command=lambda: self.show_view('dashboard'),
            accelerator="Esc"
        )
        file_menu.add_command(
            label="Add Record",
            command=lambda: self.show_view('add_record'),
            accelerator="Ctrl+N" if platform.system() != 'Darwin' else "Cmd+N"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Logout",
            command=self.logout
        )
        file_menu.add_command(
            label="Exit",
            command=self.quit_app,
            accelerator="Ctrl+Q" if platform.system() != 'Darwin' else "Cmd+Q"
        )

        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(
            label="Analytics",
            command=lambda: self.show_view('reports'),
            accelerator="Ctrl+R" if platform.system() != 'Darwin' else "Cmd+R"
        )

    def _initialize_views(self):
        """Initialize all application views"""
        # Import views here to avoid circular imports
        from gui.views.login_view import LoginView
        from gui.views.signup_view import SignupView
        from gui.views.dashboard_view import DashboardView
        from gui.views.add_record_view import AddRecordView
        from gui.views.edit_record_view import EditRecordView
        from gui.views.view_record_view import ViewRecordView
        from gui.views.reports_view import ReportsView

        # Create view instances
        self.views['login'] = LoginView(self.container, self)
        self.views['signup'] = SignupView(self.container, self)
        self.views['dashboard'] = DashboardView(self.container, self)
        self.views['add_record'] = AddRecordView(self.container, self)
        self.views['edit_record'] = EditRecordView(self.container, self)
        self.views['view_record'] = ViewRecordView(self.container, self)
        self.views['reports'] = ReportsView(self.container, self)

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Determine modifier key based on platform
        modifier = 'Command' if platform.system() == 'Darwin' else 'Control'

        # Ctrl/Cmd + N: New record
        self.bind(f'<{modifier}-n>', lambda e: self._shortcut_new_record())

        # Ctrl/Cmd + R: Reports
        self.bind(f'<{modifier}-r>', lambda e: self._shortcut_reports())

        # Ctrl/Cmd + Q: Quit
        self.bind(f'<{modifier}-q>', lambda e: self.quit_app())

        # Escape: Back to dashboard
        self.bind('<Escape>', lambda e: self._shortcut_dashboard())

    def _shortcut_new_record(self):
        """Keyboard shortcut: New record"""
        if self.session.is_authenticated:
            self.show_view('add_record')

    def _shortcut_reports(self):
        """Keyboard shortcut: Reports"""
        if self.session.is_authenticated:
            self.show_view('reports')

    def _shortcut_dashboard(self):
        """Keyboard shortcut: Dashboard"""
        if self.session.is_authenticated:
            self.show_view('dashboard')

    def show_view(self, view_name: str, **kwargs):
        """
        Switch to specified view

        Args:
            view_name: Name of view to display
            **kwargs: Parameters to pass to view's refresh method
        """
        # Check authentication for protected views
        protected_views = ['dashboard', 'add_record', 'edit_record', 'view_record', 'reports']
        if view_name in protected_views and not self.session.is_authenticated:
            self.show_view('login')
            self.show_notification("Please login to access this page", 'error')
            return

        if view_name in self.views:
            # Hide all views
            for view in self.views.values():
                view.hide()

            # Show target view
            view = self.views[view_name]
            view.show()
            view.refresh(**kwargs)

    def login(self, user_id: str, username: str):
        """
        Handle successful login

        Args:
            user_id: User's ID
            username: User's username
        """
        self.session.login(user_id, username)
        self.show_view('dashboard')
        self.show_notification(f"Welcome back, {username}!", 'success')

    def logout(self):
        """Handle logout"""
        if self.session.is_authenticated:
            result = messagebox.askyesno(
                "Confirm Logout",
                "Are you sure you want to logout?"
            )
            if result:
                self.session.logout()
                self.show_view('login')
                self.show_notification("Logged out successfully", 'success')
        else:
            self.show_view('login')

    def show_notification(self, message: str, msg_type: str = 'info'):
        """
        Show notification toast

        Args:
            message: Message text
            msg_type: Type ('success', 'error', 'info')
        """
        self.notification.show(message, msg_type)

    def quit_app(self):
        """Quit application with confirmation"""
        result = messagebox.askyesno(
            "Confirm Exit",
            "Are you sure you want to exit?"
        )
        if result:
            self.quit()
