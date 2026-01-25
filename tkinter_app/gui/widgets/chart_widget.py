"""
Chart widget for analytics
Integrates matplotlib for displaying charts in tkinter
"""
import tkinter as tk
from gui.theme import Theme

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ChartWidget(tk.Frame):
    """
    Chart widget using matplotlib
    Supports doughnut (pie) and bar charts
    """

    def __init__(self, parent, figsize=(6, 4)):
        """
        Initialize chart widget

        Args:
            parent: Parent widget
            figsize: Tuple of (width, height) in inches
        """
        super().__init__(parent, bg=Theme.BG_WHITE)

        if not MATPLOTLIB_AVAILABLE:
            # Show error message if matplotlib not installed
            error_label = tk.Label(
                self,
                text="Matplotlib not installed\nRun: pip install matplotlib",
                font=Theme.FONT_BODY,
                fg=Theme.DANGER,
                bg=Theme.BG_WHITE
            )
            error_label.pack(expand=True)
            return

        # Create matplotlib figure
        self.figure = Figure(figsize=figsize, dpi=100, facecolor=Theme.BG_WHITE)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def clear(self):
        """Clear the current chart"""
        if MATPLOTLIB_AVAILABLE:
            self.figure.clear()
            self.canvas.draw()

    def plot_doughnut(self, labels, sizes, colors, title=""):
        """
        Plot doughnut (pie) chart

        Args:
            labels: List of category labels
            sizes: List of values
            colors: List of hex color codes
            title: Chart title
        """
        if not MATPLOTLIB_AVAILABLE:
            return

        self.clear()
        ax = self.figure.add_subplot(111)

        # Create pie chart with hole in center (doughnut)
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops={'width': 0.5}  # Creates doughnut effect
        )

        # Style text
        for text in texts:
            text.set_fontsize(10)
            text.set_color(Theme.TEXT_PRIMARY)

        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color(Theme.TEXT_WHITE)
            autotext.set_weight('bold')

        if title:
            ax.set_title(title, fontsize=12, color=Theme.TEXT_PRIMARY, pad=20)

        ax.axis('equal')  # Equal aspect ratio ensures circular shape
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_bar(self, categories, values, color, title="", xlabel="", ylabel=""):
        """
        Plot bar chart

        Args:
            categories: List of category names
            values: List of values
            color: Bar color (hex code)
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
        """
        if not MATPLOTLIB_AVAILABLE:
            return

        self.clear()
        ax = self.figure.add_subplot(111)

        # Create bar chart
        bars = ax.bar(categories, values, color=color, width=0.6)

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{int(height)}',
                ha='center',
                va='bottom',
                fontsize=9,
                color=Theme.TEXT_PRIMARY
            )

        # Style axes
        ax.set_facecolor(Theme.BG_WHITE)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(Theme.BORDER_DARK)
        ax.spines['bottom'].set_color(Theme.BORDER_DARK)

        ax.tick_params(colors=Theme.TEXT_SECONDARY)
        ax.tick_params(axis='x', rotation=45)

        if title:
            ax.set_title(title, fontsize=12, color=Theme.TEXT_PRIMARY, pad=20)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=10, color=Theme.TEXT_SECONDARY)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=10, color=Theme.TEXT_SECONDARY)

        # Set y-axis to start at 0
        ax.set_ylim(bottom=0)

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_line(self, x_data, y_data, color, title="", xlabel="", ylabel=""):
        """
        Plot line chart

        Args:
            x_data: List of x-axis values
            y_data: List of y-axis values
            color: Line color (hex code)
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
        """
        if not MATPLOTLIB_AVAILABLE:
            return

        self.clear()
        ax = self.figure.add_subplot(111)

        # Create line chart
        ax.plot(x_data, y_data, color=color, linewidth=2, marker='o', markersize=6)

        # Fill area under line
        ax.fill_between(x_data, y_data, alpha=0.2, color=color)

        # Style axes
        ax.set_facecolor(Theme.BG_WHITE)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(Theme.BORDER_DARK)
        ax.spines['bottom'].set_color(Theme.BORDER_DARK)

        ax.tick_params(colors=Theme.TEXT_SECONDARY)

        if title:
            ax.set_title(title, fontsize=12, color=Theme.TEXT_PRIMARY, pad=20)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=10, color=Theme.TEXT_SECONDARY)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=10, color=Theme.TEXT_SECONDARY)

        # Add grid
        ax.grid(True, alpha=0.3, color=Theme.BORDER)

        self.figure.tight_layout()
        self.canvas.draw()
