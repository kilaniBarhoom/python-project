"""
Reports view
Replaces templates/reports.html
Shows analytics, charts, and PDF export
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import sys
import os

# Add parent directory to path for models import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gui.views.base_view import BaseView
from gui.theme import Theme
from gui.widgets.chart_widget import ChartWidget
from models import RecordModel, CommentModel


class ReportsView(BaseView):
    """
    Reports view showing analytics and statistics
    Includes charts and PDF export
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.record_model = RecordModel()
        self.comment_model = CommentModel()
        self.stats = None
        self._build_ui()

    def _build_ui(self):
        """Build reports UI"""
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

    def _build_content(self):
        """Build reports content"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if not self.stats:
            return

        # Title section
        title_section = tk.Frame(self.content_frame, bg=Theme.BG_LIGHT)
        title_section.pack(fill='x', pady=(0, 20))

        reports_title = tk.Label(
            title_section,
            text="Reports & Analytics",
            font=Theme.FONT_HEADING,
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_LIGHT
        )
        reports_title.pack(side='left')

        export_btn = ttk.Button(
            title_section,
            text="Export PDF",
            style='Success.TButton',
            command=self._handle_export_pdf
        )
        export_btn.pack(side='right')

        # Generated date
        date_label = tk.Label(
            self.content_frame,
            text=f"Generated on: {self.stats['generated_at']}",
            font=Theme.FONT_BODY,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_LIGHT
        )
        date_label.pack(anchor='w', pady=(0, 20))

        # Overview cards
        self._build_overview_cards()

        # Charts section
        self._build_charts()

        # Time stats
        self._build_time_stats()

        # Date range
        self._build_date_range()

    def _build_overview_cards(self):
        """Build overview statistics cards"""
        # Card container
        cards_frame = tk.Frame(self.content_frame, bg=Theme.BG_LIGHT)
        cards_frame.pack(fill='x', pady=(0, 20))

        # Configure grid
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1, uniform='card')

        # Total records
        self._create_stat_card(
            cards_frame, 0, 0,
            "Total Records",
            str(self.stats['total']),
            Theme.TEXT_PRIMARY
        )

        # Active
        self._create_stat_card(
            cards_frame, 0, 1,
            "Active",
            str(self.stats['status_breakdown']['active']),
            Theme.SUCCESS_TEXT
        )

        # Completed
        self._create_stat_card(
            cards_frame, 0, 2,
            "Completed",
            str(self.stats['status_breakdown']['completed']),
            Theme.INFO_TEXT
        )

        # Inactive
        self._create_stat_card(
            cards_frame, 0, 3,
            "Inactive",
            str(self.stats['status_breakdown']['inactive']),
            Theme.TEXT_SECONDARY
        )

        # Comment stats
        comment_cards_frame = tk.Frame(self.content_frame, bg=Theme.BG_LIGHT)
        comment_cards_frame.pack(fill='x', pady=(0, 20))

        for i in range(2):
            comment_cards_frame.columnconfigure(i, weight=1, uniform='card')

        self._create_stat_card(
            comment_cards_frame, 0, 0,
            "My Comments",
            str(self.stats['comments']['total_comments']),
            Theme.PURPLE_TEXT
        )

        self._create_stat_card(
            comment_cards_frame, 0, 1,
            "Comments on My Records",
            str(self.stats['comments']['comments_on_my_records']),
            Theme.INDIGO
        )

    def _create_stat_card(self, parent, row, col, title, value, color):
        """Create a single stat card"""
        card = tk.Frame(
            parent,
            bg=Theme.BG_WHITE,
            relief='solid',
            borderwidth=1
        )
        card.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

        title_label = tk.Label(
            card,
            text=title,
            font=Theme.FONT_BODY,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_WHITE
        )
        title_label.pack(pady=(15, 5))

        value_label = tk.Label(
            card,
            text=value,
            font=(Theme.FONT_FAMILY, 32, 'bold'),
            fg=color,
            bg=Theme.BG_WHITE
        )
        value_label.pack(pady=(0, 15))

    def _build_charts(self):
        """Build charts section"""
        charts_frame = tk.Frame(self.content_frame, bg=Theme.BG_LIGHT)
        charts_frame.pack(fill='x', pady=(0, 20))

        charts_frame.columnconfigure(0, weight=1)
        charts_frame.columnconfigure(1, weight=1)

        # Status distribution (doughnut chart)
        status_chart = ChartWidget(charts_frame, figsize=(5, 4))
        status_chart.grid(row=0, column=0, padx=(0, 10), sticky='nsew')

        labels = ['Active', 'Completed', 'Inactive']
        sizes = [
            self.stats['status_breakdown']['active'],
            self.stats['status_breakdown']['completed'],
            self.stats['status_breakdown']['inactive']
        ]
        colors = [Theme.SUCCESS, Theme.INFO, Theme.TEXT_LIGHT]

        status_chart.plot_doughnut(labels, sizes, colors, "Status Distribution")

        # Category distribution (bar chart)
        category_chart = ChartWidget(charts_frame, figsize=(5, 4))
        category_chart.grid(row=0, column=1, padx=(10, 0), sticky='nsew')

        if self.stats['by_category']:
            categories = list(self.stats['by_category'].keys())
            values = list(self.stats['by_category'].values())

            category_chart.plot_bar(
                categories,
                values,
                Theme.SUCCESS,
                "Category Distribution",
                ylabel="Count"
            )

    def _build_time_stats(self):
        """Build time-based statistics"""
        time_frame = tk.Frame(self.content_frame, bg=Theme.BG_LIGHT)
        time_frame.pack(fill='x', pady=(0, 20))

        for i in range(3):
            time_frame.columnconfigure(i, weight=1, uniform='time')

        self._create_stat_card(
            time_frame, 0, 0,
            "Today",
            str(self.stats['time_stats']['today']),
            Theme.TEXT_PRIMARY
        )

        self._create_stat_card(
            time_frame, 0, 1,
            "This Week",
            str(self.stats['time_stats']['this_week']),
            Theme.TEXT_PRIMARY
        )

        self._create_stat_card(
            time_frame, 0, 2,
            "This Month",
            str(self.stats['time_stats']['this_month']),
            Theme.TEXT_PRIMARY
        )

    def _build_date_range(self):
        """Build date range section"""
        if self.stats['date_range']['first_record']:
            date_card = tk.Frame(
                self.content_frame,
                bg=Theme.BG_WHITE,
                relief='solid',
                borderwidth=1
            )
            date_card.pack(fill='x', pady=(0, 20))

            content = tk.Frame(date_card, bg=Theme.BG_WHITE)
            content.pack(fill='x', padx=20, pady=15)

            tk.Label(
                content,
                text="First Record",
                font=Theme.FONT_BODY_BOLD,
                fg=Theme.TEXT_PRIMARY,
                bg=Theme.BG_WHITE
            ).pack(side='left')

            tk.Label(
                content,
                text=self.stats['date_range']['first_record'],
                font=Theme.FONT_BODY,
                fg=Theme.TEXT_SECONDARY,
                bg=Theme.BG_WHITE
            ).pack(side='left', padx=(10, 20))

            tk.Label(
                content,
                text="→",
                font=Theme.FONT_BODY,
                fg=Theme.TEXT_SECONDARY,
                bg=Theme.BG_WHITE
            ).pack(side='left', padx=(0, 20))

            tk.Label(
                content,
                text="Latest Record",
                font=Theme.FONT_BODY_BOLD,
                fg=Theme.TEXT_PRIMARY,
                bg=Theme.BG_WHITE
            ).pack(side='left')

            tk.Label(
                content,
                text=self.stats['date_range']['last_record'],
                font=Theme.FONT_BODY,
                fg=Theme.TEXT_SECONDARY,
                bg=Theme.BG_WHITE
            ).pack(side='left', padx=(10, 0))

    def _handle_export_pdf(self):
        """Handle PDF export button click"""
        # Import PDF generation function
        from routes.report_routes import generate_pdf_report

        user_id = self.get_session().user_id
        username = self.get_session().username

        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"report_{username}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

        if filename:
            # Generate PDF
            success, message, pdf_bytes = generate_pdf_report(user_id, username)

            if success:
                # Save PDF
                try:
                    with open(filename, 'wb') as f:
                        f.write(pdf_bytes)
                    self.show_notification("PDF exported successfully", 'success')
                except Exception as e:
                    self.show_notification(f"Error saving PDF: {str(e)}", 'error')
            else:
                self.show_notification(message, 'error')

    def refresh(self, **kwargs):
        """Load statistics when view is shown"""
        user_id = self.get_session().user_id
        if not user_id:
            return

        # Get statistics
        record_stats = self.record_model.get_summary_stats(user_id)
        comment_stats = self.comment_model.get_comment_stats(user_id)

        # Combine stats
        self.stats = {**record_stats, 'comments': comment_stats}

        # Build content
        self._build_content()
