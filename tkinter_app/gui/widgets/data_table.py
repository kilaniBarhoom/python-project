"""
Data table widget
Wrapper around ttk.Treeview for displaying records
"""
import tkinter as tk
from tkinter import ttk
from gui.theme import Theme


class DataTable(tk.Frame):
    """
    Reusable table widget for displaying data with scrollbar
    Wraps ttk.Treeview with convenient methods
    """

    def __init__(self, parent, columns, show_scrollbar=True, height=15):
        """
        Initialize data table

        Args:
            parent: Parent widget
            columns: List of column definitions [(id, heading, width), ...]
            show_scrollbar: Whether to show vertical scrollbar
            height: Number of rows to display
        """
        super().__init__(parent, bg=Theme.BG_WHITE)
        self.columns = columns

        # Create treeview
        column_ids = [col[0] for col in columns]
        self.tree = ttk.Treeview(
            self,
            columns=column_ids,
            show='headings',
            selectmode='browse',
            height=height
        )

        # Configure columns
        for col_id, col_heading, col_width in columns:
            self.tree.heading(col_id, text=col_heading)
            self.tree.column(col_id, width=col_width, anchor='w')

        # Pack treeview
        self.tree.pack(side='left', fill='both', expand=True)

        # Add scrollbar if requested
        if show_scrollbar:
            scrollbar = ttk.Scrollbar(
                self,
                orient='vertical',
                command=self.tree.yview
            )
            scrollbar.pack(side='right', fill='y')
            self.tree.configure(yscrollcommand=scrollbar.set)

        # Zebra striping (alternating row colors)
        self.tree.tag_configure('oddrow', background=Theme.BG_WHITE)
        self.tree.tag_configure('evenrow', background=Theme.BG_LIGHT)

    def set_data(self, rows):
        """
        Populate table with data

        Args:
            rows: List of tuples matching column structure
        """
        # Clear existing data
        self.clear()

        # Insert new data
        for i, row in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert('', 'end', values=row, tags=(tag,))

    def clear(self):
        """Clear all data from table"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def get_selected(self):
        """
        Get selected row data

        Returns:
            Tuple of selected row values, or None if no selection
        """
        selection = self.tree.selection()
        if not selection:
            return None

        item = selection[0]
        return self.tree.item(item)['values']

    def get_selected_id(self, id_column=0):
        """
        Get ID of selected row

        Args:
            id_column: Index of ID column (default 0)

        Returns:
            ID value or None if no selection
        """
        selected = self.get_selected()
        if selected:
            return selected[id_column]
        return None

    def bind_double_click(self, callback):
        """
        Bind double-click event to callback

        Args:
            callback: Function to call on double-click, receives row data
        """
        def on_double_click(event):
            selected = self.get_selected()
            if selected:
                callback(selected)

        self.tree.bind('<Double-Button-1>', on_double_click)

    def bind_selection(self, callback):
        """
        Bind selection change event to callback

        Args:
            callback: Function to call when selection changes
        """
        self.tree.bind('<<TreeviewSelect>>', lambda e: callback())

    def get_all_rows(self):
        """
        Get all row data from table

        Returns:
            List of tuples containing row values
        """
        rows = []
        for item in self.tree.get_children():
            rows.append(self.tree.item(item)['values'])
        return rows

    def set_column_widths(self, widths):
        """
        Update column widths

        Args:
            widths: Dictionary of {column_id: width}
        """
        for col_id, width in widths.items():
            self.tree.column(col_id, width=width)
