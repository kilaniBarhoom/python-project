
import sqlite3
import hashlib
from typing import Optional, List, Tuple
class DatabaseManager:
    def __init__(self, db_name: str = "smart_records.db"):
        self.db_name = db_name
        self.create_tables()
    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Users table
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        # Records table
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        category TEXT,
                        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'Active',
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
        conn.commit()
        conn.close()

        print("✓ Database tables created successfully")

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    

    def create_user(self, username: str, password: str, full_name: str) -> Tuple[bool, str]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            hashed_password = self.hash_password(password)
            cursor.execute('''
                        INSERT INTO users (username, password, full_name)
                        VALUES (?, ?, ?)
                    ''', (username, hashed_password, full_name))
            conn.commit()
            conn.close()
            return True, "Account created successfully!"
        except sqlite3.IntegrityError:
                return False, "Username already exists!"
        except Exception as e:
            return False, f"Error: {str(e)}"
        
        
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[int], str]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            hashed_password = self.hash_password(password)
            cursor.execute('''
                        SELECT id, full_name FROM users 
                        WHERE username = ? AND password = ?
                    ''', (username, hashed_password))
            result = cursor.fetchone()
            conn.close()

            if result:
                return True, result[0], f"Welcome back, {result[1]}!"
            else:
                return False, None, "Invalid username or password!"
            
        except Exception as e:
            return False, None, f"Error: {str(e)}"
        

    def create_record(self, user_id: int, title: str, description: str, category: str) -> Tuple[bool, str]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                            INSERT INTO records (user_id, title, description, category)
                            VALUES (?, ?, ?, ?)
                        ''', (user_id, title, description, category))
            conn.commit()
            conn.close()
            return True, "Record created successfully!"
        except Exception as e:
            return False, f"Error: {str(e)}"
        
    def read_all_records(self, user_id: Optional[int] = None) -> List[Tuple]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if user_id:
                cursor.execute('''
                                SELECT id, title, description, category, date_added, status
                                FROM records WHERE user_id = ?
                                ORDER BY date_added DESC
                            ''', (user_id,))
            else:
                cursor.execute('''
                                SELECT id, title, description, category, date_added, status
                                FROM records ORDER BY date_added DESC
                            ''')
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"Error reading records: {e}")
            return []
        

    def update_record(self, record_id: int, title: str, description: str, category: str, status: str) -> Tuple[bool, str]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                            UPDATE records 
                            SET title = ?, description = ?, category = ?, status = ?
                            WHERE id = ?
                        ''', (title, description, category, status, record_id))
            conn.commit()
            conn.close()
            if cursor.rowcount > 0:
                return True, "Record updated successfully!"
            else:
                return False, "Record not found!"
        except Exception as e:
            return False, f"Error: {str(e)}"
        

    def delete_record(self, record_id: int) -> Tuple[bool, str]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM records WHERE id = ?', (record_id,))
            conn.commit()
            conn.close()
            if cursor.rowcount > 0:
                return True, "Record deleted successfully!"
            else:
                return False, "Record not found!"
        except Exception as e:
            return False, f"Error: {str(e)}"
        
    def search_records(self, user_id: int, search_term: str) -> List[Tuple]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            search_pattern = f"%{search_term}%"
            cursor.execute('''
                            SELECT id, title, description, category, date_added, status
                            FROM records 
                            WHERE user_id = ? AND (title LIKE ? OR description LIKE ?)
                            ORDER BY date_added DESC
                        ''', (user_id, search_pattern, search_pattern))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"Error searching records: {e}")
            return []
        

    # ============= REPORT GENERATION DATA =============
    def get_summary_stats(self, user_id: int) -> dict:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Total records
            cursor.execute('SELECT COUNT(*) FROM records WHERE user_id = ?', (user_id,))
            6
            total = cursor.fetchone()[0]
            # Active records
            cursor.execute('SELECT COUNT(*) FROM records WHERE user_id = ? AND status = "Active"', (user_id,))
            active = cursor.fetchone()[0]
            # Records by category
            cursor.execute('''
                            SELECT category, COUNT(*) 
                            FROM records WHERE user_id = ?
                            GROUP BY category
                        ''', (user_id,))
            by_category = cursor.fetchall()
            conn.close()
            return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_category': dict(by_category)
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'total': 0, 'active': 0, 'inactive': 0, 'by_category': {}}


# ============= TESTING CODE =============
if __name__ == "__main__":
# Test the database manager
    db = DatabaseManager()
    # Test 1: Create a user
    print("\n=== Test 1: Create User ===")
    success, msg = db.create_user("kilani", "kilani123", "Ibrahim Kilani")
    print(msg)
    # Test 2: Authenticate user
    print("\n=== Test 2: Authenticate User ===")
    success, user_id, msg = db.authenticate_user("kilani", "kilani123")
    print(msg)
    if success:
        # Test 3: Create records
        print("\n=== Test 3: Create Records ===")
        db.create_record(user_id, "First Record", "This is a test", "General")
        db.create_record(user_id, "Second Record", "Another test", "Important")
        print("Records created!")
        # Test 4: Read all records
        print("\n=== Test 4: Read Records ===")
        
        records = db.read_all_records(user_id)
        for record in records:
            print(f"ID: {record[0]}, Title: {record[1]}, Category: {record[3]}")
    # Test 5: Get statistics
    print("\n=== Test 5: Statistics ===")
    stats = db.get_summary_stats(user_id)
    print(f"Total records: {stats['total']}")
    print(f"Active: {stats['active']}")
    print(f"By category: {stats['by_category']}")