"""
Signup view
Replaces templates/signup.html
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path for models import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gui.views.base_view import BaseView
from gui.theme import Theme
from utils.validators import validate_signup_form
from models import UserModel


class SignupView(BaseView):
    """
    Signup view with split design
    Left: Branding, Right: Registration form
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.user_model = UserModel()
        self._build_ui()

    def _build_ui(self):
        """Build signup UI"""
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

        # Form container (centered with scrollbar)
        canvas = tk.Canvas(right_panel, bg=Theme.BG_WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_panel, orient='vertical', command=canvas.yview)
        form_container = tk.Frame(canvas, bg=Theme.BG_WHITE)

        form_container.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((400, 50), window=form_container, anchor='n')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Heading
        heading = tk.Label(
            form_container,
            text="Create Account",
            font=Theme.FONT_HEADING,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE
        )
        heading.pack(pady=(0, 30))

        # Full Name
        fullname_label = tk.Label(
            form_container,
            text="Full Name",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE,
            anchor='w'
        )
        fullname_label.pack(fill='x', pady=(0, 5))

        self.fullname_entry = ttk.Entry(form_container, width=40, font=Theme.FONT_BODY)
        self.fullname_entry.pack(pady=(0, 20))
        self.fullname_entry.focus()

        # Username
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
        self.username_entry.pack(pady=(0, 5))

        username_helper = tk.Label(
            form_container,
            text="Minimum 4 characters",
            font=Theme.FONT_SMALL,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_WHITE,
            anchor='w'
        )
        username_helper.pack(fill='x', pady=(0, 20))

        # Password 
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
        self.password_entry.pack(pady=(0, 5))

        password_helper = tk.Label(
            form_container,
            text="Minimum 6 characters",
            font=Theme.FONT_SMALL,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_WHITE,
            anchor='w'
        )
        password_helper.pack(fill='x', pady=(0, 20))

        # Confirm Password
        confirm_password_label = tk.Label(
            form_container,
            text="Confirm Password",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE,
            anchor='w'
        )
        confirm_password_label.pack(fill='x', pady=(0, 5))

        self.confirm_password_entry = ttk.Entry(form_container, width=40, font=Theme.FONT_BODY, show="*")
        self.confirm_password_entry.pack(pady=(0, 30))

        # Bind Enter key to signup
        self.confirm_password_entry.bind('<Return>', lambda e: self._handle_signup())

        # Create Account button
        signup_btn = ttk.Button(
            form_container,
            text="Create Account",
            style='Primary.TButton',
            command=self._handle_signup,
            width=40
        )
        signup_btn.pack(pady=(0, 20))

        # Login link
        login_frame = tk.Frame(form_container, bg=Theme.BG_WHITE)
        login_frame.pack()

        login_label = tk.Label(
            login_frame,
            text="Already have an account? ",
            font=Theme.FONT_BODY,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_WHITE
        )
        login_label.pack(side='left')

        login_link = tk.Label(
            login_frame,
            text="Sign in",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.INFO,
            bg=Theme.BG_WHITE,
            cursor='hand2'
        )
        login_link.pack(side='left')
        login_link.bind('<Button-1>', lambda e: self.navigate_to('login'))

    def _handle_signup(self):
        """Handle signup button click"""
        fullname = self.fullname_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Validate form
        is_valid, message = validate_signup_form(fullname, username, password, confirm_password)
        if not is_valid:
            self.show_notification(message, 'error')
            return

        # Create user
        success, message = self.user_model.create_user(username, password, fullname)

        if success:
            # Signup successful
            self.show_notification(f"{message} Please login.", 'success')
            self.navigate_to('login')
        else:
            # Signup failed
            self.show_notification(message, 'error')

    def refresh(self, **kwargs):
        """Clear form when view is shown"""
        self.fullname_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)
        self.fullname_entry.focus()
