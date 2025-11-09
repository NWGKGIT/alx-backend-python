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
            print(f"An error occurred: {e}")
            raise
        finally:
            if conn:
                conn.close()
    return wrapper


query_cache = {}

def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get('query')
        
        if query is None:
            if len(args) > 1:
                query = args[1]
            else:
                print("CACHE: Could not determine query string, skipping cache.")
                return func(*args, **kwargs)

        if query in query_cache:
            print(f"CACHE: Returning cached result for: {query}")
            return query_cache[query]
        
        print(f"CACHE: Executing and caching new query: {query}")
        result = func(*args, **kwargs)
        
        query_cache[query] = result
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):

    cursor = conn.cursor()
    cursor.execute(query)
    time.sleep(1) 
    return cursor.fetchall()

print("--- First Call ---")
start_time = time.time()
users = fetch_users_with_cache(query="SELECT * FROM users")
print(f"Time taken: {time.time() - start_time:.2f}s")

print("\n--- Second Call ---")
start_time = time.time()
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(f"Time taken: {time.time() - start_time:.2f}s")
print(f"\nResults are identical: {users == users_again}")