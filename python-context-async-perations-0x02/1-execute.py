import mysql.connector

class ExecuteQuery:
    def __init__(self, query, params=None):
        self.query = query
        self.params = params
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_password",  
            database="ALX_prodev"
        )
        self.cursor = self.connection.cursor()
        print("Database connection opened.")

        self.cursor.execute(self.query, self.params)
        result = self.cursor.fetchall()
        return result

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")
        return False 
if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > %s;"
    params = (25,)

    with ExecuteQuery(query, params) as results:
        print("Query Results:")
        for row in results:
            print(row)
