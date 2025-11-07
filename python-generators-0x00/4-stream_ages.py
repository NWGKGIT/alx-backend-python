import seed
import mysql.connector
from mysql.connector import Error


def stream_user_ages():
    connection=seed.connect_to_prodev()
    cursor=connection.cursor()
    cursor.execute("SELECT age FROM user_data")
    for (age,) in cursor:
        yield age
    cursor.close()
    connection.close()
    

def calculate_average_age():
    total = 0
    count = 0
    for age in stream_user_ages:
        total+=age
        count+=1
    if count>0:
        average=total/count
        print(f"Average age of users:{calculate_average_age()} ")
    else:
        print("No users Found.")