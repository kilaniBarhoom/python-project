"""
Record model for CRUD operations on records
"""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from .database import Database


class RecordModel:
    """Record model for CRUD operations"""

    def __init__(self):
        self.db = Database()

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

            self.db.records.insert_one(record_doc)
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

            cursor = self.db.records.find(query).sort('date_added', -1)

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

    def get_record_by_id(self, record_id: str) -> Optional[dict]:
        """
        Get a single record by ID

        Args:
            record_id: Record ID

        Returns:
            Record document or None
        """
        try:
            return self.db.records.find_one({'_id': ObjectId(record_id)})
        except Exception as e:
            print(f"Error getting record: {e}")
            return None

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
            result = self.db.records.update_one(
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
            result = self.db.records.delete_one({'_id': ObjectId(record_id)})

            if result.deleted_count > 0:
                return True, "Record deleted successfully!"
            else:
                return False, "Record not found!"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_summary_stats(self, user_id: str) -> Dict:
        """
        Get comprehensive summary statistics for a user's records

        Args:
            user_id: User ID

        Returns:
            Dictionary containing comprehensive statistics
        """
        try:
            # Total counts
            total = self.db.records.count_documents({'user_id': user_id})

            # Status breakdown
            active = self.db.records.count_documents({'user_id': user_id, 'status': 'Active'})
            inactive = self.db.records.count_documents({'user_id': user_id, 'status': 'Inactive'})
            completed = self.db.records.count_documents({'user_id': user_id, 'status': 'Completed'})

            # Category breakdown
            category_pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {'_id': '$category', 'count': {'$sum': 1}}}
            ]
            category_results = self.db.records.aggregate(category_pipeline)
            by_category = {item['_id']: item['count'] for item in category_results}

            # Time-based statistics
            now = datetime.utcnow()
            today_start = datetime(now.year, now.month, now.day)
            week_start = today_start - timedelta(days=now.weekday())
            month_start = datetime(now.year, now.month, 1)

            today_count = self.db.records.count_documents({
                'user_id': user_id,
                'date_added': {'$gte': today_start}
            })

            week_count = self.db.records.count_documents({
                'user_id': user_id,
                'date_added': {'$gte': week_start}
            })

            month_count = self.db.records.count_documents({
                'user_id': user_id,
                'date_added': {'$gte': month_start}
            })

            # Recent activity - records created in last 30 days grouped by day
            thirty_days_ago = now - timedelta(days=30)
            activity_pipeline = [
                {'$match': {
                    'user_id': user_id,
                    'date_added': {'$gte': thirty_days_ago}
                }},
                {'$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$date_added'
                        }
                    },
                    'count': {'$sum': 1}
                }},
                {'$sort': {'_id': 1}}
            ]
            activity_results = self.db.records.aggregate(activity_pipeline)
            recent_activity = {item['_id']: item['count'] for item in activity_results}

            # Most recent and oldest records
            recent_records = list(self.db.records.find({'user_id': user_id})
                                 .sort('date_added', -1).limit(5))
            oldest_records = list(self.db.records.find({'user_id': user_id})
                                 .sort('date_added', 1).limit(5))

            # Format recent records
            recent_list = [{
                'id': str(r['_id']),
                'title': r['title'],
                'category': r['category'],
                'status': r['status'],
                'date': r['date_added'].strftime('%Y-%m-%d %H:%M:%S')
            } for r in recent_records]

            # Get first and last record dates
            first_record_date = None
            last_record_date = None
            if oldest_records:
                first_record_date = oldest_records[0]['date_added'].strftime('%Y-%m-%d')
            if recent_records:
                last_record_date = recent_records[0]['date_added'].strftime('%Y-%m-%d')

            return {
                'total': total,
                'status_breakdown': {
                    'active': active,
                    'inactive': inactive,
                    'completed': completed
                },
                'by_category': by_category,
                'time_stats': {
                    'today': today_count,
                    'this_week': week_count,
                    'this_month': month_count
                },
                'recent_activity': recent_activity,
                'recent_records': recent_list,
                'date_range': {
                    'first_record': first_record_date,
                    'last_record': last_record_date
                },
                'generated_at': now.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'total': 0,
                'status_breakdown': {'active': 0, 'inactive': 0, 'completed': 0},
                'by_category': {},
                'time_stats': {'today': 0, 'this_week': 0, 'this_month': 0},
                'recent_activity': {},
                'recent_records': [],
                'date_range': {'first_record': None, 'last_record': None},
                'generated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
