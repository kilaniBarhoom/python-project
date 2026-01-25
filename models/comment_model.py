"""
Comment model for managing comments on records
"""
from typing import List, Dict
from datetime import datetime
from bson.objectid import ObjectId
from .database import Database


class CommentModel:

    def __init__(self):
        self.db = Database()

    def create_comment(self, record_id: str, user_id: str, content: str) -> tuple[bool, str]:
        """
        Create a new comment on a record

        Args:
            record_id: ID of the record being commented on
            user_id: ID of the user creating the comment
            content: Comment content

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            comment_doc = {
                'record_id': record_id,
                'user_id': user_id,
                'content': content,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }

            self.db.comments.insert_one(comment_doc)
            return True, "Comment added successfully!"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_comments_by_record(self, record_id: str) -> List[Dict]:
        """
        Get all comments for a specific record

        Args:
            record_id: Record ID

        Returns:
            List of comment dictionaries
        """
        try:
            cursor = self.db.comments.find({'record_id': record_id}).sort('created_at', -1)

            comments = []
            for comment in cursor:
                # Get user info
                user = self.db.users.find_one({'_id': ObjectId(comment['user_id'])})
                username = user['username'] if user else 'Unknown'

                comments.append({
                    'id': str(comment['_id']),
                    'record_id': comment['record_id'],
                    'user_id': comment['user_id'],
                    'username': username,
                    'content': comment['content'],
                    'created_at': comment['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': comment['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                })

            return comments

        except Exception as e:
            print(f"Error getting comments: {e}")
            return []

    def update_comment(self, comment_id: str, content: str, user_id: str) -> tuple[bool, str]:
        """
        Update a comment

        Args:
            comment_id: ID of the comment to update
            content: New comment content
            user_id: ID of the user updating (for authorization)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Check if comment belongs to user
            comment = self.db.comments.find_one({'_id': ObjectId(comment_id)})
            if not comment:
                return False, "Comment not found!"

            if comment['user_id'] != user_id:
                return False, "You can only edit your own comments!"

            result = self.db.comments.update_one(
                {'_id': ObjectId(comment_id)},
                {'$set': {
                    'content': content,
                    'updated_at': datetime.utcnow()
                }}
            )

            if result.modified_count > 0 or result.matched_count > 0:
                return True, "Comment updated successfully!"
            else:
                return False, "Comment not found!"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def delete_comment(self, comment_id: str, user_id: str) -> tuple[bool, str]:
        """
        Delete a comment

        Args:
            comment_id: ID of the comment to delete
            user_id: ID of the user deleting (for authorization)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Check if comment belongs to user
            comment = self.db.comments.find_one({'_id': ObjectId(comment_id)})
            if not comment:
                return False, "Comment not found!"

            if comment['user_id'] != user_id:
                return False, "You can only delete your own comments!"

            result = self.db.comments.delete_one({'_id': ObjectId(comment_id)})

            if result.deleted_count > 0:
                return True, "Comment deleted successfully!"
            else:
                return False, "Comment not found!"

        except Exception as e:
            return False, f"Error: {str(e)}"


    # Report functions
    def get_comment_count_by_record(self, record_id: str) -> int:
        """
        Get the count of comments for a specific record

        Args:
            record_id: Record ID

        Returns:
            Number of comments
        """
        try:
            return self.db.comments.count_documents({'record_id': record_id})
        except Exception as e:
            print(f"Error counting comments: {e}")
            return 0

    def get_all_comments_by_user(self, user_id: str) -> List[Dict]:
        """
        Get all comments by a specific user

        Args:
            user_id: User ID

        Returns:
            List of comment dictionaries
        """
        try:
            cursor = self.db.comments.find({'user_id': user_id}).sort('created_at', -1)

            comments = []
            for comment in cursor:
                # Get record info
                record = self.db.records.find_one({'_id': ObjectId(comment['record_id'])})
                record_title = record['title'] if record else 'Unknown'

                comments.append({
                    'id': str(comment['_id']),
                    'record_id': comment['record_id'],
                    'record_title': record_title,
                    'content': comment['content'],
                    'created_at': comment['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': comment['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                })

            return comments

        except Exception as e:
            print(f"Error getting user comments: {e}")
            return []

    def get_comment_stats(self, user_id: str) -> Dict:
        """
        Get comment statistics for a user

        Args:
            user_id: User ID

        Returns:
            Dictionary with comment statistics
        """
        try:
            # Total comments by user
            total_comments = self.db.comments.count_documents({'user_id': user_id})

            # Comments on user's records
            user_records = list(self.db.records.find({'user_id': user_id}, {'_id': 1}))
            record_ids = [str(r['_id']) for r in user_records]

            comments_on_records = self.db.comments.count_documents({
                'record_id': {'$in': record_ids}
            })

            # Recent comments
            recent_comments = list(self.db.comments.find({'user_id': user_id})
                                  .sort('created_at', -1).limit(5))

            recent_list = []
            for comment in recent_comments:
                record = self.db.records.find_one({'_id': ObjectId(comment['record_id'])})
                recent_list.append({
                    'id': str(comment['_id']),
                    'record_title': record['title'] if record else 'Unknown',
                    'content': comment['content'][:50] + '...' if len(comment['content']) > 50 else comment['content'],
                    'created_at': comment['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                })

            # Comments per record
            pipeline = [
                {'$match': {'record_id': {'$in': record_ids}}},
                {'$group': {
                    '_id': '$record_id',
                    'count': {'$sum': 1}
                }},
                {'$sort': {'count': -1}},
                {'$limit': 5}
            ]

            top_commented = list(self.db.comments.aggregate(pipeline))
            top_commented_records = []
            for item in top_commented:
                record = self.db.records.find_one({'_id': ObjectId(item['_id'])})
                if record:
                    top_commented_records.append({
                        'record_title': record['title'],
                        'comment_count': item['count']
                    })

            return {
                'total_comments': total_comments,
                'comments_on_my_records': comments_on_records,
                'recent_comments': recent_list,
                'top_commented_records': top_commented_records
            }

        except Exception as e:
            print(f"Error getting comment stats: {e}")
            return {
                'total_comments': 0,
                'comments_on_my_records': 0,
                'recent_comments': [],
                'top_commented_records': []
            }
