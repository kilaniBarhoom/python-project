"""
Database connection manager
"""
from pymongo import MongoClient
import os
import ssl
import certifi


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
            try:
                self.connect()
            except Exception as e:
                print(f"⚠ Failed to initialize database: {str(e)[:50]}...")

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
            # Create SSL context with proper certificate handling
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            # Configure connection with SSL context
            self._client = MongoClient(
                connection_string,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                retryWrites=False
            )
            self._db = self._client['smart_records_db']

            # Test connection
            try:
                self._client.admin.command('ping')
                print("✓ MongoDB connection successful!")
            except Exception as ping_error:
                print(f"⚠ MongoDB connection created but ping failed")
                print(f"  Error: {str(ping_error)[:100]}...")
                print("⚠ App will continue running. Database features may be limited.")

        except Exception as e:
            print(f"⚠ MongoDB connection initialization failed")
            print(f"  Error: {str(e)[:100]}...")
            print("⚠ App starting without database. Some features may not work.")
            self._client = None
            self._db = None

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
