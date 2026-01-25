"""
Notification toast widget
Replaces Flask flash messages with auto-dismissing toast notifications
"""
import tkinter as tk
from gui.theme import Theme


class Notification(tk.Frame):
    """
    Toast-style notification widget
    Appears in top-right corner and auto-dismisses after 5 seconds
    """

    def __init__(self, parent):
        """
        Initialize notification container

        Args:
            parent: Parent widget (root window)
        """
        super().__init__(parent, bg=Theme.BG_LIGHT)
        self.parent = parent
        self.active_notifications = []
        self.notification_height = 80
        self.notification_width = 400
        self.padding = 10

    def show(self, message: str, msg_type: str = 'info'):
        """
        Show a notification toast

        Args:
            message: Message text to display
            msg_type: Type of notification ('success', 'error', 'info')
        """
        # Create notification frame
        notification_frame = tk.Frame(
            self.parent,
            bg=Theme.BG_WHITE,
            relief='solid',
            borderwidth=1
        )

        # Configure colors based on type
        if msg_type == 'success':
            border_color = Theme.SUCCESS
            icon = '✓'
            icon_bg = Theme.SUCCESS_LIGHT
            icon_fg = Theme.SUCCESS_TEXT
        elif msg_type == 'error':
            border_color = Theme.DANGER
            icon = '✕'
            icon_bg = Theme.DANGER_LIGHT
            icon_fg = Theme.DANGER_TEXT
        else:  # info
            border_color = Theme.INFO
            icon = 'ℹ'
            icon_bg = Theme.INFO_LIGHT
            icon_fg = Theme.INFO_TEXT

        # Add colored left border
        left_border = tk.Frame(
            notification_frame,
            bg=border_color,
            width=4
        )
        left_border.pack(side='left', fill='y')

        # Content frame
        content_frame = tk.Frame(notification_frame, bg=Theme.BG_WHITE)
        content_frame.pack(side='left', fill='both', expand=True, padx=12, pady=12)

        # Icon
        icon_label = tk.Label(
            content_frame,
            text=icon,
            font=(Theme.FONT_FAMILY, 16, 'bold'),
            bg=icon_bg,
            fg=icon_fg,
            width=2,
            height=1,
            relief='flat'
        )
        icon_label.pack(side='left', padx=(0, 10))

        # Message
        message_label = tk.Label(
            content_frame,
            text=message,
            font=Theme.FONT_BODY,
            bg=Theme.BG_WHITE,
            fg=Theme.TEXT_PRIMARY,
            justify='left',
            wraplength=300
        )
        message_label.pack(side='left', fill='both', expand=True)

        # Close button
        close_btn = tk.Label(
            content_frame,
            text='×',
            font=(Theme.FONT_FAMILY, 18),
            bg=Theme.BG_WHITE,
            fg=Theme.TEXT_SECONDARY,
            cursor='hand2'
        )
        close_btn.pack(side='right', padx=(10, 0))
        close_btn.bind('<Button-1>', lambda e: self.dismiss(notification_frame))

        # Position notification
        self._position_notification(notification_frame)

        # Track active notifications
        self.active_notifications.append(notification_frame)

        # Auto-dismiss after 5 seconds
        self.parent.after(5000, lambda: self.dismiss(notification_frame))

        # Fade in animation (optional, can be improved)
        notification_frame.lift()

    def _position_notification(self, notification_frame):
        """
        Position notification in top-right corner

        Args:
            notification_frame: Notification frame to position
        """
        # Get window dimensions
        window_width = self.parent.winfo_width()
        window_height = self.parent.winfo_height()

        # If window not yet displayed, use screen dimensions
        if window_width <= 1:
            window_width = self.parent.winfo_screenwidth()
        if window_height <= 1:
            window_height = self.parent.winfo_screenheight()

        # Calculate position (top-right corner)
        x = window_width - self.notification_width - self.padding
        y = self.padding + (len(self.active_notifications) * (self.notification_height + self.padding))

        # Place notification
        notification_frame.place(
            x=x,
            y=y,
            width=self.notification_width,
            height=self.notification_height
        )

    def dismiss(self, notification_frame):
        """
        Dismiss a notification

        Args:
            notification_frame: Notification frame to dismiss
        """
        if notification_frame in self.active_notifications:
            self.active_notifications.remove(notification_frame)
            notification_frame.destroy()

            # Reposition remaining notifications
            self._reposition_all()

    def _reposition_all(self):
        """Reposition all active notifications after dismissal"""
        for i, notification in enumerate(self.active_notifications):
            window_width = self.parent.winfo_width()
            if window_width <= 1:
                window_width = self.parent.winfo_screenwidth()

            x = window_width - self.notification_width - self.padding
            y = self.padding + (i * (self.notification_height + self.padding))

            notification.place(x=x, y=y)
