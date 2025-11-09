import sqlite3
import functools

def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = ""
        if args:
            query = args[0]  
        elif 'query' in kwargs:
            query = kwargs['query'] 

        if query:
            print(f"LOG: Executing query: {query}")
        else:
            print("LOG: Could not find query to log.")
        
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    """
    Fetches all users from the database.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

users = fetch_all_users(query="SELECT * FROM users")
print(f"Found users: {users}")