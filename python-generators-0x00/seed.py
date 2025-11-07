import mysql.connector
from mysql.connector import Error
import csv
import uuid
import os

from dotenv import load_dotenv
load_dotenv()

def connect_db():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", ""),
            password=os.getenv("MYSQL_PASSWORD", "")
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        cursor.close()
        print("Database ALX_prodev created or already exists")
    except Error as e:
        print(f"Error creating database: {e}")

def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "ALX_prodev")
        )
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None

def create_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                age DECIMAL NOT NULL,
                INDEX(user_id)
            );
        """)
        cursor.close()
        print("Table user_data created successfully")
    except Error as e:
        print(f"Error creating table: {e}")

def read_csv_in_batches(csv_file, batch_size=100):
    with open(csv_file, newline="",encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch=[]
        for row in reader:
            batch.append(row)
            if len(batch)==batch_size:
                yield batch
                batch=[]
        if batch: # remaining batches
            yield batch
                        
def insert_data(connection, csv_file, batch_size=100):
    try:
        cursor = connection.cursor()
        for batch in read_csv_in_batches(csv_file, batch_size):            
            # Filter out duplicates
            data_to_insert = [
                (str(uuid.uuid4()), row['name'], row['email'], row['age'])
                for row in batch
            ]
            
            if data_to_insert:
                cursor.executemany(
                    "INSERT IGNORE INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s);",
                    data_to_insert
                )
            connection.commit()
        cursor.close()
        print("Data inserted successfully")
    except FileNotFoundError:
        print(f"CSV file '{csv_file}' not found")
    except Error as e:
        print(f"Error inserting data: {e}")