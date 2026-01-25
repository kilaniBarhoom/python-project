"""
Login view
Replaces templates/login.html
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path for models import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gui.views.base_view import BaseView
from gui.theme import Theme
from utils.validators import validate_login_form
from models import UserModel


class LoginView(BaseView):
    """
    Login view with split design
    Left: Branding, Right: Login form
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.user_model = UserModel()
        self._build_ui()

    def _build_ui(self):
        """Build login UI"""
        # Main container (split design)
        main_container = tk.Frame(self, bg=Theme.BG_WHITE)
        main_container.pack(fill='both', expand=True)

        # Left panel (branding) - 1/3 width
        left_panel = tk.Frame(main_container, bg=Theme.PRIMARY, width=400)
        left_panel.pack(side='left', fill='both')
        left_panel.pack_propagate(False)

        # Branding
        brand_label = tk.Label(
            left_panel,
            text="Recorderrrr",
            font=Theme.FONT_TITLE,
            fg=Theme.TEXT_WHITE,
            bg=Theme.PRIMARY
        )
        brand_label.pack(expand=True)

        # Right panel (form) - 2/3 width
        right_panel = tk.Frame(main_container, bg=Theme.BG_WHITE)
        right_panel.pack(side='right', fill='both', expand=True)

        # Form container (centered)
        form_container = tk.Frame(right_panel, bg=Theme.BG_WHITE)
        form_container.place(relx=0.5, rely=0.5, anchor='center')

        # Heading
        heading = tk.Label(
            form_container,
            text="Welcome Back",
            font=Theme.FONT_HEADING,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE
        )
        heading.pack(pady=(0, 30))

        # Username field
        username_label = tk.Label(
            form_container,
            text="Username",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE,
            anchor='w'
        )
        username_label.pack(fill='x', pady=(0, 5))

        self.username_entry = ttk.Entry(form_container, width=40, font=Theme.FONT_BODY)
        self.username_entry.pack(pady=(0, 20))
        self.username_entry.focus()

        # Password field
        password_label = tk.Label(
            form_container,
            text="Password",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE,
            anchor='w'
        )
        password_label.pack(fill='x', pady=(0, 5))

        self.password_entry = ttk.Entry(form_container, width=40, font=Theme.FONT_BODY, show="*")
        self.password_entry.pack(pady=(0, 30))

        # Bind Enter key to login
        self.username_entry.bind('<Return>', lambda e: self._handle_login())
        self.password_entry.bind('<Return>', lambda e: self._handle_login())

        # Sign In button
        signin_btn = ttk.Button(
            form_container,
            text="Sign In",
            style='Primary.TButton',
            command=self._handle_login,
            width=40
        )
        signin_btn.pack(pady=(0, 20))

        # Signup link
        signup_frame = tk.Frame(form_container, bg=Theme.BG_WHITE)
        signup_frame.pack()

        signup_label = tk.Label(
            signup_frame,
            text="Don't have an account? ",
            font=Theme.FONT_BODY,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_WHITE
        )
        signup_label.pack(side='left')

        signup_link = tk.Label(
            signup_frame,
            text="Sign up",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.INFO,
            bg=Theme.BG_WHITE,
            cursor='hand2'
        )
        signup_link.pack(side='left')
        signup_link.bind('<Button-1>', lambda e: self.navigate_to('signup'))

    def _handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        # Validate form
        is_valid, message = validate_login_form(username, password)
        if not is_valid:
            self.show_notification(message, 'error')
            return

        # Authenticate user
        success, user_id, message = self.user_model.authenticate_user(username, password)

        if success:
            # Login successful
            self.controller.login(user_id, username)
        else:
            # Login failed
            self.show_notification(message, 'error')
            self.password_entry.delete(0, tk.END)

    def refresh(self, **kwargs):
        """Clear form when view is shown"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus()
