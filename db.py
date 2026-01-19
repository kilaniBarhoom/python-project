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

    def get_summary_stats(self, user_id: str) -> Dict:
        """
        Get comprehensive summary statistics for a user's records

        Args:
            user_id: User ID

        Returns:
            Dictionary containing comprehensive statistics
        """
        try:
            from datetime import timedelta

            # Total counts
            total = self.records.count_documents({'user_id': user_id})

            # Status breakdown
            active = self.records.count_documents({'user_id': user_id, 'status': 'Active'})
            inactive = self.records.count_documents({'user_id': user_id, 'status': 'Inactive'})
            completed = self.records.count_documents({'user_id': user_id, 'status': 'Completed'})

            # Category breakdown
            category_pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {'_id': '$category', 'count': {'$sum': 1}}}
            ]
            category_results = self.records.aggregate(category_pipeline)
            by_category = {item['_id']: item['count'] for item in category_results}

            # Time-based statistics
            now = datetime.utcnow()
            today_start = datetime(now.year, now.month, now.day)
            week_start = today_start - timedelta(days=now.weekday())
            month_start = datetime(now.year, now.month, 1)

            today_count = self.records.count_documents({
                'user_id': user_id,
                'date_added': {'$gte': today_start}
            })

            week_count = self.records.count_documents({
                'user_id': user_id,
                'date_added': {'$gte': week_start}
            })

            month_count = self.records.count_documents({
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
            activity_results = self.records.aggregate(activity_pipeline)
            recent_activity = {item['_id']: item['count'] for item in activity_results}

            # Most recent and oldest records
            recent_records = list(self.records.find({'user_id': user_id})
                                 .sort('date_added', -1).limit(5))
            oldest_records = list(self.records.find({'user_id': user_id})
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

    def generate_pdf_report(self, user_id: str, username: str) -> tuple[bool, str, bytes]:
        """
        Generate a PDF report of user statistics

        Args:
            user_id: User ID
            username: Username for display in report

        Returns:
            Tuple of (success: bool, message: str, pdf_bytes: bytes)
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from io import BytesIO

            # Get statistics
            stats = self.get_summary_stats(user_id)

            # Create PDF in memory
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2a2a2a'),
                spaceAfter=12,
                spaceBefore=12
            )

            # Title
            elements.append(Paragraph("Smart Records System", title_style))
            elements.append(Paragraph(f"Analytics Report for {username}", styles['Heading2']))
            elements.append(Paragraph(f"Generated on: {stats['generated_at']}", styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))

            # Overview Section
            elements.append(Paragraph("Overview", heading_style))
            overview_data = [
                ['Metric', 'Value'],
                ['Total Records', str(stats['total'])],
                ['Active Records', str(stats['status_breakdown']['active'])],
                ['Completed Records', str(stats['status_breakdown']['completed'])],
                ['Inactive Records', str(stats['status_breakdown']['inactive'])],
            ]

            if stats['date_range']['first_record']:
                overview_data.append(['First Record Date', stats['date_range']['first_record']])
            if stats['date_range']['last_record']:
                overview_data.append(['Last Record Date', stats['date_range']['last_record']])

            overview_table = Table(overview_data, colWidths=[3*inch, 3*inch])
            overview_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a2a2a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            elements.append(overview_table)
            elements.append(Spacer(1, 0.3*inch))

            # Time-based Statistics
            elements.append(Paragraph("Recent Activity", heading_style))
            time_data = [
                ['Period', 'Records Created'],
                ['Today', str(stats['time_stats']['today'])],
                ['This Week', str(stats['time_stats']['this_week'])],
                ['This Month', str(stats['time_stats']['this_month'])],
            ]
            time_table = Table(time_data, colWidths=[3*inch, 3*inch])
            time_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a2a2a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            elements.append(time_table)
            elements.append(Spacer(1, 0.3*inch))

            # Category Breakdown
            if stats['by_category']:
                elements.append(Paragraph("Records by Category", heading_style))
                category_data = [['Category', 'Count']]
                for category, count in sorted(stats['by_category'].items()):
                    category_data.append([category, str(count)])

                category_table = Table(category_data, colWidths=[3*inch, 3*inch])
                category_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a2a2a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                ]))
                elements.append(category_table)
                elements.append(Spacer(1, 0.3*inch))

            # Recent Records
            if stats['recent_records']:
                elements.append(Paragraph("Recent Records (Last 5)", heading_style))
                recent_data = [['Title', 'Category', 'Status', 'Date']]
                for record in stats['recent_records']:
                    title = record['title'][:30] + '...' if len(record['title']) > 30 else record['title']
                    recent_data.append([
                        title,
                        record['category'],
                        record['status'],
                        record['date'].split(' ')[0]  # Just the date part
                    ])

                recent_table = Table(recent_data, colWidths=[2.2*inch, 1.5*inch, 1.3*inch, 1.5*inch])
                recent_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a2a2a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                ]))
                elements.append(recent_table)

            # Build PDF
            doc.build(elements)
            pdf_bytes = buffer.getvalue()
            buffer.close()

            return True, "PDF generated successfully", pdf_bytes

        except ImportError:
            return False, "reportlab library not installed. Run: pip install reportlab", b''
        except Exception as e:
            return False, f"Error generating PDF: {str(e)}", b''

    def close(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
            print("✓ MongoDB connection closed")
