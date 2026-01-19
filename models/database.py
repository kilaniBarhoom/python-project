"""
Database connection manager
"""
from pymongo import MongoClient
import os


class Database:
    """MongoDB database connection manager"""

    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        """Singleton pattern to ensure one database connection"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize database connection"""
        if self._client is None:
            self.connect()

    def connect(self, connection_string: str = None):
        """
        Connect to MongoDB

        Args:
            connection_string: MongoDB connection URI
        """
        connection_string = connection_string or os.getenv('MONGODB_URI')

        if not connection_string:
            raise ValueError(
                "MongoDB connection string not provided. "
                "Please set MONGODB_URI environment variable."
            )

        try:
            self._client = MongoClient(connection_string)
            self._db = self._client['smart_records_db']

            # Test connection
            self._client.admin.command('ping')
            print("✓ MongoDB connection successful!")

        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            raise

    @property
    def db(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db

    @property
    def users(self):
        """Get users collection"""
        return self.db['users']

    @property
    def records(self):
        """Get records collection"""
        return self.db['records']

    @property
    def comments(self):
        """Get comments collection"""
        return self.db['comments']

    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("✓ MongoDB connection closed")
