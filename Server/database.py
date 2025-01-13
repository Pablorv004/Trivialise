import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error: {e}")

    def create_user(self, username, password):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO users (username, password, totalPoints, roundsPlayed, gamesPlayed) VALUES (%s, %s, %s, %s, %s)", 
                    (username, password, 0, 0, 0))
        self.connection.commit()
        cursor.close()

    def get_user(self, username):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        return user

    def update_user(self, username, totalPoints, roundsPlayed, gamesPlayed):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET totalPoints = %s, roundsPlayed = %s, gamesPlayed = %s WHERE username = %s", 
                    (totalPoints, roundsPlayed, gamesPlayed, username))
        self.connection.commit()
        cursor.close()
