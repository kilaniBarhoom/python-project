import hashlib
from typing import Optional, List, Dict
from pymongo import MongoClient
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv('MONGODB_URI')

        if not self.connection_string:
            raise ValueError(
                "MongoDB connection string not provided. "
                "Please provide it as a parameter or set MONGODB_URI environment variable."
            )

        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client['smart_records_db']

            self.users = self.db['users']
            self.records = self.db['records']

            self.client.admin.command('ping')
            print("✓ MongoDB connection successful!")

        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            raise

    @staticmethod
    def hash_password(password: str) -> str:
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
            if self.users.find_one({'username': username}):
                return False, "Username already exists!"

            hashed_password = self.hash_password(password)

            user_doc = {
                'username': username,
                'password': hashed_password,
                'full_name': full_name,
                'created_at': datetime.utcnow()
            }

            self.users.insert_one(user_doc)
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

            user = self.users.find_one({
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

    def create_record(self, user_id: str, title: str, description: str, category: str) -> tuple[bool, str]:
        """
        Create a new record

        Args:
            user_id: ID of the user creating the record
            title: Record title
            description: Record description
            category: Record category

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            record_doc = {
                'user_id': user_id,
                'title': title,
                'description': description,
                'category': category,
                'date_added': datetime.utcnow(),
                'status': 'Active'
            }

            self.records.insert_one(record_doc)
            return True, "Record created successfully!"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def read_all_records(self, user_id: Optional[str] = None) -> List[tuple]:
        """
        Read all records for a user

        Args:
            user_id: User ID to filter records (if None, returns all records)

        Returns:
            List of tuples containing record data
        """
        try:
            query = {'user_id': user_id} if user_id else {}

            cursor = self.records.find(query).sort('date_added', -1)

            results = []
            for record in cursor:
                results.append((
                    str(record['_id']),
                    record['title'],
                    record['description'],
                    record['category'],
                    record['date_added'].strftime('%Y-%m-%d %H:%M:%S'),
                    record['status']
                ))

            return results

        except Exception as e:
            print(f"Error reading records: {e}")
            return []

    def update_record(self, record_id: str, title: str, description: str,
                     category: str, status: str) -> tuple[bool, str]:
        """
        Update an existing record

        Args:
            record_id: ID of the record to update
            title: New title
            description: New description
            category: New category
            status: New status

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            from bson.objectid import ObjectId

            result = self.records.update_one(
                {'_id': ObjectId(record_id)},
                {'$set': {
                    'title': title,
                    'description': description,
                    'category': category,
                    'status': status
                }}
            )

            if result.modified_count > 0 or result.matched_count > 0:
                return True, "Record updated successfully!"
            else:
                return False, "Record not found!"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def delete_record(self, record_id: str) -> tuple[bool, str]:
        """
        Delete a record

        Args:
            record_id: ID of the record to delete

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            from bson.objectid import ObjectId

            result = self.records.delete_one({'_id': ObjectId(record_id)})

            if result.deleted_count > 0:
                return True, "Record deleted successfully!"
            else:
                return False, "Record not found!"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def search_records(self, user_id: str, search_term: str) -> List[tuple]:
        """
        Search records by title or description

        Args:
            user_id: User ID to filter records
            search_term: Term to search for

        Returns:
            List of tuples containing matching records
        """
        try:
            query = {
                'user_id': user_id,
                '$or': [
                    {'title': {'$regex': search_term, '$options': 'i'}},
                    {'description': {'$regex': search_term, '$options': 'i'}}
                ]
            }

            cursor = self.records.find(query).sort('date_added', -1)

            results = []
            for record in cursor:
                results.append((
                    str(record['_id']),
                    record['title'],
                    record['description'],
                    record['category'],
                    record['date_added'].strftime('%Y-%m-%d %H:%M:%S'),
                    record['status']
                ))

            return results

        except Exception as e:
            print(f"Error searching records: {e}")
            return []

    def get_summary_stats(self, user_id: str) -> Dict:
        
        """
        Get summary statistics for a user's records

        Args:
            user_id: User ID

        Returns:
            Dictionary containing statistics
        """
        try:
            total = self.records.count_documents({'user_id': user_id})

            active = self.records.count_documents({
                'user_id': user_id,
                'status': 'Active'
            })

            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {
                    '_id': '$category',
                    'count': {'$sum': 1}
                }}
            ]

            category_results = self.records.aggregate(pipeline)
            by_category = {item['_id']: item['count'] for item in category_results}

            return {
                'total': total,
                'active': active,
                'inactive': total - active,
                'by_category': by_category
            }

        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'total': 0, 'active': 0, 'inactive': 0, 'by_category': {}}

    def close(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
            print("✓ MongoDB connection closed")
