import seed
import mysql.connector
from mysql.connector import Error
def stream_users():
    try: 
        prodevconnection = seed.connect_to_prodev()
        cursor = prodevconnection.cursor(buffered=False)
        cursor.execute("SELECT * FROM user_data")
        columns = cursor.column_names
        for row in cursor:
            yield dict(zip(columns, row))

    except Error as e:
        print(f"Error: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if prodevconnection:
            prodevconnection.close()