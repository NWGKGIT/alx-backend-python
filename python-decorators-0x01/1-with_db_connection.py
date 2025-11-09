import sqlite3 
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect('users.db')
            print("Database connection opened.")
            
            result = func(conn, *args, **kwargs)
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
        finally:
            if conn:
                conn.close()
                print("Database connection closed.")
    return wrapper

@with_db_connection 
def get_user_by_id(conn, user_id):

    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 

try:
    user = get_user_by_id(user_id=1)
    print(f"Found user: {user}")
except Exception as e:
    print(f"Failed to fetch user.")