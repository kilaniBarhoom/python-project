"""
User model for authentication and user management
"""
import hashlib
from typing import Optional
from datetime import datetime
from .database import Database


class UserModel:
    """User model for authentication and user management"""

    def __init__(self):
        self.db = Database()

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username: str, password: str, full_name: str) -> tuple[bool, str]:
        """
        Create a new user account

        Args:
            username: Unique username
            password: User password (will be hashed)
            full_name: User's full name

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if self.db.users.find_one({'username': username}):
                return False, "Username already exists!"

            hashed_password = self.hash_password(password)

            user_doc = {
                'username': username,
                'password': hashed_password,
                'full_name': full_name,
                'created_at': datetime.utcnow()
            }

            self.db.users.insert_one(user_doc)
            return True, "Account created successfully!"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def authenticate_user(self, username: str, password: str) -> tuple[bool, Optional[str], str]:
        """
        Authenticate user login

        Args:
            username: Username
            password: Password to verify

        Returns:
            Tuple of (success: bool, user_id: str or None, message: str)
        """
        try:
            hashed_password = self.hash_password(password)

            user = self.db.users.find_one({
                'username': username,
                'password': hashed_password
            })

            if user:
                user_id = str(user['_id'])
                return True, user_id, f"Welcome back, {user['full_name']}!"
            else:
                return False, None, "Invalid username or password!"

        except Exception as e:
            return False, None, f"Error: {str(e)}"

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """
        Get user by ID

        Args:
            user_id: User ID

        Returns:
            User document or None
        """
        try:
            from bson.objectid import ObjectId
            return self.db.users.find_one({'_id': ObjectId(user_id)})
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
