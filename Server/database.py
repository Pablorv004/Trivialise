import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from hashlib import sha256

load_dotenv()

class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
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

    def reconnect(self):
        if not self.connection.is_connected():
            print("Reconnecting to MySQL database...")
            self.connect()

    def create_user(self, email, password):
        self.reconnect()
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO users (email, password, totalPoints, roundsPlayed, gamesPlayed) VALUES (%s, %s, %s, %s, %s)", 
                    (email, password, 0, 0, 0))
        self.connection.commit()
        cursor.close()
    
    def get_user_by_email(self, email):
        self.reconnect()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        return user

    def get_user_by_ip(self, ip):
        self.reconnect()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE ip = %s ORDER BY lastOnline DESC LIMIT 1", (ip,))
        user = cursor.fetchone()
        cursor.close()
        return user
    
    def update_user_ip(self, email, ip, lastOnline):
        self.reconnect()
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET ip = %s WHERE email = %s", (ip, email))
        cursor.execute("UPDATE users SET lastOnline = %s WHERE email = %s", (lastOnline, email))
        self.connection.commit()
        cursor.close()

    def update_user(self, email, totalPoints, roundsPlayed, gamesPlayed):
        self.reconnect()
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET totalPoints = %s, roundsPlayed = %s, gamesPlayed = %s WHERE email = %s", 
                    (totalPoints, roundsPlayed, gamesPlayed, email))
        self.connection.commit()
        cursor.close()

    def update_username(self, email, username):
        self.reconnect()
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET username = %s WHERE email = %s", (username, email))
        self.connection.commit()
        cursor.close()

    def get_leaderboard(self, order_by):
        self.reconnect()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(f"SELECT username, {order_by} FROM users ORDER BY {order_by} DESC LIMIT 10")
        leaderboard = cursor.fetchall()
        cursor.close()
        return [(entry['username'], entry[order_by]) for entry in leaderboard]
