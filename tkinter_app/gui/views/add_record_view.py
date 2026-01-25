"""
Add Record view
Replaces templates/add.html
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path for models import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gui.views.base_view import BaseView
from gui.theme import Theme
from utils.validators import validate_record_form
from models import RecordModel


class AddRecordView(BaseView):
    """
    Add Record view with form
    Allows creating new records
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.record_model = RecordModel()
        self._build_ui()

    def _build_ui(self):
        """Build add record UI"""
        # Center container
        center_frame = tk.Frame(self, bg=Theme.BG_LIGHT)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Card frame
        card_frame = tk.Frame(
            center_frame,
            bg=Theme.BG_WHITE,
            relief='solid',
            borderwidth=1
        )
        card_frame.pack(padx=40, pady=40)

        # Header
        header_frame = tk.Frame(card_frame, bg=Theme.BG_GRAY, height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="Add New Record",
            font=Theme.FONT_SUBHEADING,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_GRAY
        )
        header_label.pack(pady=15, padx=20)

        # Form container
        form_frame = tk.Frame(card_frame, bg=Theme.BG_WHITE)
        form_frame.pack(fill='both', padx=30, pady=30)

        # Title field
        title_label = tk.Label(
            form_frame,
            text="Title",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE,
            anchor='w'
        )
        title_label.pack(fill='x', pady=(0, 5))

        self.title_entry = ttk.Entry(form_frame, width=60, font=Theme.FONT_BODY)
        self.title_entry.pack(pady=(0, 20))
        self.title_entry.focus()

        # Description field
        desc_label = tk.Label(
            form_frame,
            text="Description",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE,
            anchor='w'
        )
        desc_label.pack(fill='x', pady=(0, 5))

        # Text widget with scrollbar for description
        desc_frame = tk.Frame(form_frame, bg=Theme.BG_WHITE)
        desc_frame.pack(fill='x', pady=(0, 20))

        self.desc_text = tk.Text(
            desc_frame,
            height=6,
            font=Theme.FONT_BODY,
            wrap='word',
            relief='solid',
            borderwidth=1
        )
        self.desc_text.pack(side='left', fill='both', expand=True)

        desc_scrollbar = ttk.Scrollbar(desc_frame, orient='vertical', command=self.desc_text.yview)
        desc_scrollbar.pack(side='right', fill='y')
        self.desc_text.configure(yscrollcommand=desc_scrollbar.set)

        # Category field
        category_label = tk.Label(
            form_frame,
            text="Category",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE,
            anchor='w'
        )
        category_label.pack(fill='x', pady=(0, 5))

        self.category_var = tk.StringVar(value='General')
        category_combo = ttk.Combobox(
            form_frame,
            textvariable=self.category_var,
            values=['General', 'Important', 'Personal', 'Work', 'Other'],
            state='readonly',
            width=57,
            font=Theme.FONT_BODY
        )
        category_combo.pack(pady=(0, 30))

        # Buttons
        button_frame = tk.Frame(form_frame, bg=Theme.BG_WHITE)
        button_frame.pack(fill='x')

        save_btn = ttk.Button(
            button_frame,
            text="Save Record",
            style='Success.TButton',
            command=self._handle_save
        )
        save_btn.pack(side='left', fill='x', expand=True, padx=(0, 5))

        back_btn = ttk.Button(
            button_frame,
            text="Back to Dashboard",
            style='Secondary.TButton',
            command=lambda: self.navigate_to('dashboard')
        )
        back_btn.pack(side='left', fill='x', expand=True, padx=(5, 0))

    def _handle_save(self):
        """Handle save button click"""
        title = self.title_entry.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        category = self.category_var.get()

        # Validate form
        is_valid, message = validate_record_form(title, description)
        if not is_valid:
            self.show_notification(message, 'error')
            return

        # Create record
        user_id = self.get_session().user_id
        success, message = self.record_model.create_record(user_id, title, description, category)

        if success:
            self.show_notification(message, 'success')
            self.navigate_to('dashboard')
        else:
            self.show_notification(message, 'error')

    def refresh(self, **kwargs):
        """Clear form when view is shown"""
        self.title_entry.delete(0, tk.END)
        self.desc_text.delete('1.0', tk.END)
        self.category_var.set('General')
        self.title_entry.focus()
