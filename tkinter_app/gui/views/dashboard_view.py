"""
Dashboard view
Replaces templates/index.html
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for models import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gui.views.base_view import BaseView
from gui.theme import Theme
from gui.widgets.data_table import DataTable
from models import RecordModel


class DashboardView(BaseView):
    """
    Dashboard view showing all user records
    Main screen after login
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.record_model = RecordModel()
        self._build_ui()

    def _build_ui(self):
        """Build dashboard UI"""
        # Header
        header_frame = tk.Frame(self, bg=Theme.BG_WHITE, height=80)
        header_frame.pack(fill='x', padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(
            header_frame,
            text="THE RECORDERRR",
            font=Theme.FONT_HEADING,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE
        )
        title_label.pack(side='left', pady=20)

        # Header buttons
        logout_btn = ttk.Button(
            header_frame,
            text="Logout",
            style='Danger.TButton',
            command=self.controller.logout
        )
        logout_btn.pack(side='right', padx=(10, 0), pady=20)

        reports_btn = ttk.Button(
            header_frame,
            text="Reports",
            style='Success.TButton',
            command=lambda: self.navigate_to('reports')
        )
        reports_btn.pack(side='right', pady=20)

        # Main content container
        content_frame = tk.Frame(self, bg=Theme.BG_LIGHT)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Toolbar
        toolbar_frame = tk.Frame(content_frame, bg=Theme.BG_LIGHT)
        toolbar_frame.pack(fill='x', pady=(0, 15))

        dashboard_title = tk.Label(
            toolbar_frame,
            text="Dashboard",
            font=Theme.FONT_SUBHEADING,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_LIGHT
        )
        dashboard_title.pack(side='left')

        add_btn = ttk.Button(
            toolbar_frame,
            text="+ Add New Record",
            style='Success.TButton',
            command=lambda: self.navigate_to('add_record')
        )
        add_btn.pack(side='right')

        # Records table container
        self.table_container = tk.Frame(content_frame, bg=Theme.BG_WHITE)
        self.table_container.pack(fill='both', expand=True)

        # This will be populated in _create_table() or _show_empty_state()
        self._create_table()

    def _create_table(self):
        """Create records table"""
        # Clear container
        for widget in self.table_container.winfo_children():
            widget.destroy()

        # Create table frame
        table_frame = tk.Frame(self.table_container, bg=Theme.BG_WHITE)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Create data table
        columns = [
            ('id', 'ID', 80),
            ('title', 'Title', 200),
            ('description', 'Description', 300),
            ('category', 'Category', 120),
            ('date', 'Date Added', 150),
            ('status', 'Status', 100)
        ]

        self.data_table = DataTable(table_frame, columns, height=20)
        self.data_table.pack(fill='both', expand=True)

        # Action buttons frame (below table)
        self.actions_frame = tk.Frame(table_frame, bg=Theme.BG_WHITE)
        self.actions_frame.pack(fill='x', pady=(10, 0))

        # Create action buttons (initially disabled)
        view_btn = ttk.Button(
            self.actions_frame,
            text="View",
            style='Info.TButton',
            command=self._handle_view,
            state='disabled'
        )
        view_btn.pack(side='left', padx=(0, 5))
        self.view_btn = view_btn

        edit_btn = ttk.Button(
            self.actions_frame,
            text="Edit",
            style='Primary.TButton',
            command=self._handle_edit,
            state='disabled'
        )
        edit_btn.pack(side='left', padx=5)
        self.edit_btn = edit_btn

        delete_btn = ttk.Button(
            self.actions_frame,
            text="Delete",
            style='Danger.TButton',
            command=self._handle_delete,
            state='disabled'
        )
        delete_btn.pack(side='left', padx=5)
        self.delete_btn = delete_btn

        # Enable buttons when row is selected
        self.data_table.bind_selection(self._on_selection_changed)

        # Double-click to view
        self.data_table.bind_double_click(lambda row: self._handle_view())

    def _on_selection_changed(self):
        """Enable/disable action buttons based on selection"""
        selected = self.data_table.get_selected()
        state = 'normal' if selected else 'disabled'
        self.view_btn.configure(state=state)
        self.edit_btn.configure(state=state)
        self.delete_btn.configure(state=state)

    def _handle_view(self):
        """Handle view button click"""
        record_id = self.data_table.get_selected_id(id_column=0)
        if record_id:
            self.navigate_to('view_record', record_id=str(record_id))

    def _handle_edit(self):
        """Handle edit button click"""
        record_id = self.data_table.get_selected_id(id_column=0)
        if record_id:
            self.navigate_to('edit_record', record_id=str(record_id))

    def _handle_delete(self):
        """Handle delete button click"""
        record_id = self.data_table.get_selected_id(id_column=0)
        if not record_id:
            return

        # Confirmation dialog
        result = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this record?"
        )

        if result:
            success, message = self.record_model.delete_record(str(record_id))
            if success:
                self.show_notification(message, 'success')
                self.refresh()
            else:
                self.show_notification(message, 'error')

    def _show_empty_state(self):
        """Show empty state when no records"""
        # Clear container
        for widget in self.table_container.winfo_children():
            widget.destroy()

        # Empty state container
        empty_container = tk.Frame(self.table_container, bg=Theme.BG_WHITE)
        empty_container.pack(expand=True)

        # Icon
        icon_label = tk.Label(
            empty_container,
            text="📋",
            font=(Theme.FONT_FAMILY, 48),
            bg=Theme.BG_WHITE
        )
        icon_label.pack(pady=(0, 20))

        # Message
        message_label = tk.Label(
            empty_container,
            text="No records yet",
            font=Theme.FONT_HEADING,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE
        )
        message_label.pack(pady=(0, 10))

        # CTA button
        create_btn = ttk.Button(
            empty_container,
            text="Create your first record",
            style='Success.TButton',
            command=lambda: self.navigate_to('add_record')
        )
        create_btn.pack()

    def refresh(self, **kwargs):
        """Refresh dashboard with latest records"""
        user_id = self.get_session().user_id
        if not user_id:
            return

        # Get all records for user
        records = self.record_model.read_all_records(user_id)

        if not records or len(records) == 0:
            # Show empty state
            self._show_empty_state()
        else:
            # Show table
            if not hasattr(self, 'data_table'):
                self._create_table()

            # Populate table
            self.data_table.set_data(records)
