import seed
import mysql.connector
from mysql.connector import Error

def stream_users_in_batches(batch_size=100):
    try: 
        connection = seed.connect_to_prodev()
        cursor = connection.cursor(buffered=False)
        cursor.execute("SELECT * FROM user_data")
        columns = cursor.column_names
        batch=[]
        for row in cursor:
            batch.append(zip(dict(columns,row)))
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
            
    except Error as e:
        print(f"Error: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            return

def batch_processing(batch_size=100):
    for batch in stream_users_in_batches(batch_size):
        filtered=[user for user in batch if user['age']>25]
        yield filtered
    return