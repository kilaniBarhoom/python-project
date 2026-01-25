"""
View Record view
Replaces templates/view_record.html
Shows record details and comments
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for models import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gui.views.base_view import BaseView
from gui.theme import Theme
from utils.validators import validate_comment
from models import RecordModel, CommentModel


class ViewRecordView(BaseView):
    """
    View Record view showing record details and comments
    Allows adding, editing, and deleting comments
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.record_model = RecordModel()
        self.comment_model = CommentModel()
        self.current_record_id = None
        self.current_record = None
        self._build_ui()

    def _build_ui(self):
        """Build view record UI"""
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

        dashboard_btn = ttk.Button(
            header_frame,
            text="Dashboard",
            style='Success.TButton',
            command=lambda: self.navigate_to('dashboard')
        )
        dashboard_btn.pack(side='right', pady=20)

        # Scrollable content
        canvas = tk.Canvas(self, bg=Theme.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        self.content_frame = tk.Frame(canvas, bg=Theme.BG_LIGHT)

        self.content_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=self.content_frame, anchor='nw', width=1240)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side='right', fill='y', pady=(0, 20))

        # Content will be built in refresh()

    def _build_record_details(self):
        """Build record details section"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if not self.current_record:
            return

        # Record details card
        details_card = tk.Frame(self.content_frame, bg=Theme.BG_WHITE, relief='solid', borderwidth=1)
        details_card.pack(fill='x', pady=(0, 20))

        # Header with title and badges
        header_section = tk.Frame(details_card, bg=Theme.BG_WHITE)
        header_section.pack(fill='x', padx=20, pady=20)

        # Title
        title_label = tk.Label(
            header_section,
            text=self.current_record[1],  # title
            font=Theme.FONT_HEADING,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE,
            wraplength=800,
            justify='left'
        )
        title_label.pack(anchor='w', pady=(0, 10))

        # Badges row
        badges_frame = tk.Frame(header_section, bg=Theme.BG_WHITE)
        badges_frame.pack(anchor='w', pady=(0, 10))

        # Category badge
        category_bg = Theme.BG_GRAY
        category_label = tk.Label(
            badges_frame,
            text=self.current_record[3],  # category
            font=Theme.FONT_SMALL,
            bg=category_bg,
            fg=Theme.TEXT_PRIMARY,
            padx=10,
            pady=4
        )
        category_label.pack(side='left', padx=(0, 10))

        # Status badge
        status = self.current_record[5]  # status
        status_bg, status_fg = Theme.get_status_colors(status)
        status_label = tk.Label(
            badges_frame,
            text=status,
            font=Theme.FONT_SMALL,
            bg=status_bg,
            fg=status_fg,
            padx=10,
            pady=4
        )
        status_label.pack(side='left')

        # Date
        date_label = tk.Label(
            header_section,
            text=f"Created: {self.current_record[4]}",  # date_added
            font=Theme.FONT_BODY,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_WHITE
        )
        date_label.pack(anchor='w')

        # Edit button (if owner)
        edit_btn = ttk.Button(
            header_section,
            text="Edit",
            style='Primary.TButton',
            command=lambda: self.navigate_to('edit_record', record_id=self.current_record_id)
        )
        edit_btn.pack(anchor='w', pady=(10, 0))

        # Description
        desc_frame = tk.Frame(details_card, bg=Theme.BG_WHITE)
        desc_frame.pack(fill='both', padx=20, pady=(0, 20))

        desc_text = tk.Text(
            desc_frame,
            height=8,
            font=Theme.FONT_BODY,
            wrap='word',
            relief='flat',
            bg=Theme.BG_WHITE,
            fg=Theme.TEXT_PRIMARY
        )
        desc_text.pack(fill='both')
        desc_text.insert('1.0', self.current_record[2])  # description
        desc_text.configure(state='disabled')

        # Comments section
        self._build_comments_section()

    def _build_comments_section(self):
        """Build comments section"""
        # Comments card
        comments_card = tk.Frame(self.content_frame, bg=Theme.BG_WHITE, relief='solid', borderwidth=1)
        comments_card.pack(fill='both')

        # Comments header
        comments_header = tk.Frame(comments_card, bg=Theme.BG_GRAY)
        comments_header.pack(fill='x', padx=20, pady=15)

        comments_count = len(self.comment_model.get_comments_for_record(self.current_record_id))

        comments_title = tk.Label(
            comments_header,
            text=f"Comments ({comments_count})",
            font=Theme.FONT_SUBHEADING,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_GRAY
        )
        comments_title.pack(side='left')

        # Add comment form
        add_comment_frame = tk.Frame(comments_card, bg=Theme.BG_WHITE)
        add_comment_frame.pack(fill='x', padx=20, pady=15)

        add_label = tk.Label(
            add_comment_frame,
            text="Add Comment",
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_WHITE
        )
        add_label.pack(anchor='w', pady=(0, 5))

        self.new_comment_text = tk.Text(
            add_comment_frame,
            height=3,
            font=Theme.FONT_BODY,
            wrap='word',
            relief='solid',
            borderwidth=1
        )
        self.new_comment_text.pack(fill='x', pady=(0, 10))

        add_comment_btn = ttk.Button(
            add_comment_frame,
            text="Submit Comment",
            style='Success.TButton',
            command=self._handle_add_comment
        )
        add_comment_btn.pack(anchor='w')

        # Comments list
        self.comments_list_frame = tk.Frame(comments_card, bg=Theme.BG_WHITE)
        self.comments_list_frame.pack(fill='both', padx=20, pady=(0, 20))

        self._populate_comments()

    def _populate_comments(self):
        """Populate comments list"""
        # Clear comments list
        for widget in self.comments_list_frame.winfo_children():
            widget.destroy()

        # Get comments
        comments = self.comment_model.get_comments_for_record(self.current_record_id)

        if not comments:
            no_comments_label = tk.Label(
                self.comments_list_frame,
                text="No comments yet",
                font=Theme.FONT_BODY,
                fg=Theme.TEXT_SECONDARY,
                bg=Theme.BG_WHITE
            )
            no_comments_label.pack(pady=20)
            return

        # Display each comment
        for comment in comments:
            self._create_comment_widget(comment)

    def _create_comment_widget(self, comment):
        """Create widget for a single comment"""
        comment_frame = tk.Frame(
            self.comments_list_frame,
            bg=Theme.BG_LIGHT,
            relief='solid',
            borderwidth=1
        )
        comment_frame.pack(fill='x', pady=(0, 10))

        # Comment header
        header_frame = tk.Frame(comment_frame, bg=Theme.BG_LIGHT)
        header_frame.pack(fill='x', padx=15, pady=(10, 5))

        username_label = tk.Label(
            header_frame,
            text=comment['username'],
            font=Theme.FONT_BODY_BOLD,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_LIGHT
        )
        username_label.pack(side='left')

        timestamp_text = comment['created_at']
        if comment['updated_at'] != comment['created_at']:
            timestamp_text += " (edited)"

        timestamp_label = tk.Label(
            header_frame,
            text=timestamp_text,
            font=Theme.FONT_SMALL,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_LIGHT
        )
        timestamp_label.pack(side='left', padx=(10, 0))

        # Comment content
        content_label = tk.Label(
            comment_frame,
            text=comment['content'],
            font=Theme.FONT_BODY,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_LIGHT,
            wraplength=1100,
            justify='left',
            anchor='w'
        )
        content_label.pack(fill='x', padx=15, pady=(0, 10))

        # Action buttons (only for comment owner)
        if comment['user_id'] == self.get_session().user_id:
            actions_frame = tk.Frame(comment_frame, bg=Theme.BG_LIGHT)
            actions_frame.pack(fill='x', padx=15, pady=(0, 10))

            edit_btn = ttk.Button(
                actions_frame,
                text="Edit",
                style='Info.TButton',
                command=lambda c=comment: self._handle_edit_comment(c)
            )
            edit_btn.pack(side='left', padx=(0, 5))

            delete_btn = ttk.Button(
                actions_frame,
                text="Delete",
                style='Danger.TButton',
                command=lambda c=comment: self._handle_delete_comment(c)
            )
            delete_btn.pack(side='left')

    def _handle_add_comment(self):
        """Handle add comment button click"""
        content = self.new_comment_text.get('1.0', tk.END).strip()

        # Validate
        is_valid, message = validate_comment(content)
        if not is_valid:
            self.show_notification(message, 'error')
            return

        # Add comment
        user_id = self.get_session().user_id
        success, message = self.comment_model.add_comment(self.current_record_id, user_id, content)

        if success:
            self.show_notification(message, 'success')
            self.new_comment_text.delete('1.0', tk.END)
            self._populate_comments()
        else:
            self.show_notification(message, 'error')

    def _handle_edit_comment(self, comment):
        """Handle edit comment button click"""
        # Simple implementation: show dialog with text entry
        dialog = tk.Toplevel(self)
        dialog.title("Edit Comment")
        dialog.geometry("500x200")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Edit Comment", font=Theme.FONT_SUBHEADING).pack(pady=10)

        text_widget = tk.Text(dialog, height=5, font=Theme.FONT_BODY)
        text_widget.pack(padx=20, pady=10, fill='both', expand=True)
        text_widget.insert('1.0', comment['content'])

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)

        def save():
            new_content = text_widget.get('1.0', tk.END).strip()
            is_valid, message = validate_comment(new_content)
            if not is_valid:
                messagebox.showerror("Validation Error", message)
                return

            success, message = self.comment_model.edit_comment(comment['id'], new_content)
            if success:
                self.show_notification(message, 'success')
                dialog.destroy()
                self._populate_comments()
            else:
                messagebox.showerror("Error", message)

        ttk.Button(button_frame, text="Save", style='Success.TButton', command=save).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", style='Secondary.TButton', command=dialog.destroy).pack(side='left', padx=5)

    def _handle_delete_comment(self, comment):
        """Handle delete comment button click"""
        result = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this comment?"
        )

        if result:
            success, message = self.comment_model.delete_comment(comment['id'])
            if success:
                self.show_notification(message, 'success')
                self._populate_comments()
            else:
                self.show_notification(message, 'error')

    def refresh(self, **kwargs):
        """Load record and comments when view is shown"""
        record_id = kwargs.get('record_id')
        if not record_id:
            self.navigate_to('dashboard')
            return

        self.current_record_id = record_id

        # Get record
        self.current_record = self.record_model.read_record(record_id)
        if not self.current_record:
            self.show_notification("Record not found", 'error')
            self.navigate_to('dashboard')
            return

        # Build UI
        self._build_record_details()
