"""
Session management for tkinter application
Replaces Flask session-based authentication
"""


class SessionManager:
    """Manages user session state for the application"""

    def __init__(self):
        self._user_id = None
        self._username = None
        self._is_authenticated = False

    def login(self, user_id: str, username: str):
        """
        Log in a user and store session data

        Args:
            user_id: User's MongoDB ObjectId as string
            username: User's username
        """
        self._user_id = user_id
        self._username = username
        self._is_authenticated = True

    def logout(self):
        """Clear session data and log out user"""
        self._user_id = None
        self._username = None
        self._is_authenticated = False

    @property
    def user_id(self):
        """Get current user ID"""
        return self._user_id

    @property
    def username(self):
        """Get current username"""
        return self._username

    @property
    def is_authenticated(self):
        """Check if user is logged in"""
        return self._is_authenticated

    def require_login(self):
        """
        Check if user is authenticated, raise error if not
        Can be used as decorator replacement for Flask's @login_required

        Raises:
            PermissionError: If user is not authenticated
        """
        if not self._is_authenticated:
            raise PermissionError("Login required")

    def __repr__(self):
        return f"SessionManager(user_id={self._user_id}, username={self._username}, authenticated={self._is_authenticated})"
