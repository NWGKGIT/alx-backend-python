import mysql.connector

class DatabaseConnection:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()
        print("Database connection opened.")
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")
        return False 


if __name__ == "__main__":
    with DatabaseConnection(
        host="localhost",
        user="root",
        password="your_password", 
        database="ALX_prodev"
    ) as cursor:
        cursor.execute("SELECT * FROM users;") 
        results = cursor.fetchall()
        print("Query Results:")
        for row in results:
            print(row)