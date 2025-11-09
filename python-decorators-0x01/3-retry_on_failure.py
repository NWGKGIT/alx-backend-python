import time
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
            raise 
        finally:
            if conn:
                conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):
    """
    Decorator factory that retries a function 'retries' times
    with a 'delay' between attempts.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Attempt {attempt + 1}/{retries} failed: {e}")
                    if attempt < retries - 1:
                        print(f"Retrying in {delay} second(s)...")
                        time.sleep(delay)
            
            print(f"All {retries} attempts failed.")
            if last_exception:
                raise last_exception
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1) 
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

try:
    users = fetch_users_with_retry()
    print(f"Successfully fetched users: {users}")
except Exception as e:
    print(f"Failed to fetch users after all retries: {e}")