"""
Theme configuration for tkinter application
Matches Tailwind CSS color scheme from Flask app
"""
import platform
from tkinter import ttk


class Theme:
    """Centralized theme configuration matching Tailwind CSS palette"""

    # Primary colors (matching Tailwind)
    PRIMARY = '#111827'       # gray-900
    BG_LIGHT = '#f9fafb'      # gray-50
    BG_WHITE = '#ffffff'
    BG_GRAY = '#f3f4f6'       # gray-100
    BG_DARK = '#1f2937'       # gray-800
    BORDER = '#e5e7eb'        # gray-200
    BORDER_DARK = '#d1d5db'   # gray-300

    # Action colors
    SUCCESS = '#166534'       # green-800
    SUCCESS_HOVER = '#15803d' # green-700
    SUCCESS_LIGHT = '#dcfce7' # green-100
    SUCCESS_TEXT = '#166534'  # green-700

    INFO = '#2563eb'          # blue-600
    INFO_HOVER = '#1d4ed8'    # blue-700
    INFO_LIGHT = '#dbeafe'    # blue-100
    INFO_TEXT = '#1e40af'     # blue-700

    DANGER = '#dc2626'        # red-600
    DANGER_HOVER = '#b91c1c'  # red-700
    DANGER_LIGHT = '#fee2e2'  # red-100
    DANGER_TEXT = '#dc2626'   # red-600

    WARNING = '#ca8a04'       # yellow-600
    WARNING_LIGHT = '#fef3c7' # yellow-100

    PURPLE = '#9333ea'        # purple-600
    PURPLE_LIGHT = '#f3e8ff'  # purple-100
    PURPLE_TEXT = '#7e22ce'   # purple-700

    INDIGO = '#4f46e5'        # indigo-600
    INDIGO_LIGHT = '#e0e7ff'  # indigo-100

    # Text colors
    TEXT_PRIMARY = '#111827'   # gray-900
    TEXT_SECONDARY = '#6b7280' # gray-500
    TEXT_LIGHT = '#9ca3af'     # gray-400
    TEXT_WHITE = '#ffffff'

    # Status colors
    STATUS_ACTIVE_BG = '#dcfce7'    # green-100
    STATUS_ACTIVE_TEXT = '#166534'   # green-700

    STATUS_COMPLETED_BG = '#dbeafe'  # blue-100
    STATUS_COMPLETED_TEXT = '#1e40af' # blue-700

    STATUS_INACTIVE_BG = '#f3f4f6'   # gray-100
    STATUS_INACTIVE_TEXT = '#4b5563'  # gray-600

    # Fonts (platform-specific)
    @staticmethod
    def get_font_family():
        """Get appropriate font family for platform"""
        system = platform.system()
        if system == 'Darwin':  # macOS
            return 'SF Pro Display'
        elif system == 'Windows':
            return 'Segoe UI'
        else:  # Linux
            return 'Ubuntu'

    FONT_FAMILY = get_font_family.__func__()
    FONT_TITLE = (FONT_FAMILY, 24, 'bold')
    FONT_HEADING = (FONT_FAMILY, 18, 'bold')
    FONT_SUBHEADING = (FONT_FAMILY, 14, 'bold')
    FONT_BODY = (FONT_FAMILY, 11)
    FONT_BODY_BOLD = (FONT_FAMILY, 11, 'bold')
    FONT_SMALL = (FONT_FAMILY, 9)
    FONT_BUTTON = (FONT_FAMILY, 11, 'bold')

    @staticmethod
    def configure_ttk_styles():
        """Configure ttk widget styles"""
        style = ttk.Style()

        # Use 'clam' theme as base (works well cross-platform)
        try:
            style.theme_use('clam')
        except:
            pass  # Use default if clam not available

        # Primary Button (gray-900 background)
        style.configure('Primary.TButton',
                       background=Theme.PRIMARY,
                       foreground=Theme.TEXT_WHITE,
                       borderwidth=0,
                       relief='flat',
                       padding=(16, 10),
                       font=Theme.FONT_BUTTON)
        style.map('Primary.TButton',
                 background=[('active', Theme.BG_DARK), ('disabled', Theme.TEXT_LIGHT)])

        # Success Button (green-800)
        style.configure('Success.TButton',
                       background=Theme.SUCCESS,
                       foreground=Theme.TEXT_WHITE,
                       borderwidth=0,
                       relief='flat',
                       padding=(16, 10),
                       font=Theme.FONT_BUTTON)
        style.map('Success.TButton',
                 background=[('active', Theme.SUCCESS_HOVER), ('disabled', Theme.TEXT_LIGHT)])

        # Info Button (blue-600)
        style.configure('Info.TButton',
                       background=Theme.INFO,
                       foreground=Theme.TEXT_WHITE,
                       borderwidth=0,
                       relief='flat',
                       padding=(12, 8),
                       font=Theme.FONT_BODY_BOLD)
        style.map('Info.TButton',
                 background=[('active', Theme.INFO_HOVER)])

        # Danger Button (red-600)
        style.configure('Danger.TButton',
                       background=Theme.DANGER,
                       foreground=Theme.TEXT_WHITE,
                       borderwidth=0,
                       relief='flat',
                       padding=(12, 8),
                       font=Theme.FONT_BODY_BOLD)
        style.map('Danger.TButton',
                 background=[('active', Theme.DANGER_HOVER)])

        # Secondary Button (gray background)
        style.configure('Secondary.TButton',
                       background=Theme.BG_GRAY,
                       foreground=Theme.TEXT_PRIMARY,
                       borderwidth=0,
                       relief='flat',
                       padding=(16, 10),
                       font=Theme.FONT_BUTTON)
        style.map('Secondary.TButton',
                 background=[('active', Theme.BORDER_DARK)])

        # Link Button (text only)
        style.configure('Link.TButton',
                       background=Theme.BG_WHITE,
                       foreground=Theme.INFO,
                       borderwidth=0,
                       relief='flat',
                       padding=(4, 2),
                       font=Theme.FONT_BODY)
        style.map('Link.TButton',
                 foreground=[('active', Theme.INFO_HOVER)])

        # Entry widgets
        style.configure('TEntry',
                       fieldbackground=Theme.BG_WHITE,
                       background=Theme.BG_WHITE,
                       foreground=Theme.TEXT_PRIMARY,
                       borderwidth=1,
                       relief='solid',
                       padding=10,
                       font=Theme.FONT_BODY)

        # Combobox
        style.configure('TCombobox',
                       fieldbackground=Theme.BG_WHITE,
                       background=Theme.BG_WHITE,
                       foreground=Theme.TEXT_PRIMARY,
                       borderwidth=1,
                       relief='solid',
                       padding=10,
                       font=Theme.FONT_BODY)

        # Treeview (tables)
        style.configure('Treeview',
                       background=Theme.BG_WHITE,
                       foreground=Theme.TEXT_PRIMARY,
                       fieldbackground=Theme.BG_WHITE,
                       borderwidth=1,
                       font=Theme.FONT_BODY)
        style.configure('Treeview.Heading',
                       background=Theme.BG_GRAY,
                       foreground=Theme.TEXT_PRIMARY,
                       borderwidth=1,
                       font=Theme.FONT_BODY_BOLD)
        style.map('Treeview',
                 background=[('selected', Theme.BG_GRAY)])

        # Labels
        style.configure('TLabel',
                       background=Theme.BG_WHITE,
                       foreground=Theme.TEXT_PRIMARY,
                       font=Theme.FONT_BODY)

        style.configure('Heading.TLabel',
                       background=Theme.BG_WHITE,
                       foreground=Theme.TEXT_PRIMARY,
                       font=Theme.FONT_HEADING)

        # Frame
        style.configure('TFrame',
                       background=Theme.BG_WHITE)

        style.configure('Card.TFrame',
                       background=Theme.BG_WHITE,
                       borderwidth=1,
                       relief='solid')

    @staticmethod
    def get_status_colors(status):
        """Get background and foreground colors for status badge"""
        status_map = {
            'Active': (Theme.STATUS_ACTIVE_BG, Theme.STATUS_ACTIVE_TEXT),
            'Completed': (Theme.STATUS_COMPLETED_BG, Theme.STATUS_COMPLETED_TEXT),
            'Inactive': (Theme.STATUS_INACTIVE_BG, Theme.STATUS_INACTIVE_TEXT)
        }
        return status_map.get(status, (Theme.STATUS_INACTIVE_BG, Theme.STATUS_INACTIVE_TEXT))
