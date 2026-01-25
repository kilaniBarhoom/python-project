"""
Base view class for all application views
"""
import tkinter as tk
from abc import ABC, abstractmethod
from gui.theme import Theme


class BaseView(tk.Frame, ABC):
    """
    Abstract base class for all views in the application
    Provides common structure and navigation interface
    """

    def __init__(self, parent, controller):
        """
        Initialize base view

        Args:
            parent: Parent widget (container frame)
            controller: AppController instance for navigation and state
        """
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=Theme.BG_LIGHT)

    def show(self):
        """Display this view by packing it into parent"""
        self.pack(fill='both', expand=True)

    def hide(self):
        """Hide this view by removing from pack"""
        self.pack_forget()

    def refresh(self, **kwargs):
        """
        Refresh view data and UI
        Override in child classes to reload data when view becomes active

        Args:
            **kwargs: Optional parameters for refreshing (e.g., record_id for detail views)
        """
        pass

    def show_notification(self, message: str, msg_type: str = 'info'):
        """
        Show notification toast message

        Args:
            message: Message text
            msg_type: Type of notification ('success', 'error', 'info')
        """
        if hasattr(self.controller, 'show_notification'):
            self.controller.show_notification(message, msg_type)

    def get_session(self):
        """Get session manager from controller"""
        return self.controller.session

    def navigate_to(self, view_name: str, **kwargs):
        """
        Navigate to another view

        Args:
            view_name: Name of view to show
            **kwargs: Parameters to pass to view's refresh method
        """
        self.controller.show_view(view_name, **kwargs)
