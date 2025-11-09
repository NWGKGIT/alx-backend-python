import sqlite3 
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect('users.db')
            result = func(conn, *args, **kwargs)
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
        finally:
            if conn:
                conn.close()
    return wrapper

def transactional(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = args[0]
        try:
            result = func(*args, **kwargs)
            conn.commit()
            print("Transaction committed.")
            return result
        except Exception as e:
            conn.rollback()
            print(f"Transaction rolled back due to error: {e}")
            raise
    return wrapper


@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email):

    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    print(f"Attempting to update user {user_id} email to {new_email}")

try:
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
except Exception as e:
    print(f"Update failed: {e}")