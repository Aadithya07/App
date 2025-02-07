import sqlite3
import hashlib
from datetime import datetime
from kivy.app import App

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("users.db", isolation_level=None)  # Auto-commit mode
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Creates necessary database tables if they do not exist."""
        with self.conn:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    join_date TEXT NOT NULL
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS body_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    weight REAL DEFAULT 0,
                    height REAL DEFAULT 0,
                    body_fat REAL DEFAULT 0,
                    bmi REAL DEFAULT 0,
                    FOREIGN KEY (username) REFERENCES users (username)
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS workouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    workout_type TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    calories INTEGER NOT NULL,
                    date TEXT NOT NULL
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    creator TEXT NOT NULL
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    FOREIGN KEY (team_name) REFERENCES teams (name),
                    FOREIGN KEY (username) REFERENCES users (username),
                    UNIQUE(team_name, username)  
                )
            """)

    def hash_password(self, password):
        """Hashes the password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, email, password):
        """Registers a new user and returns a status message."""
        try:
            hashed_password = self.hash_password(password)
            with self.conn:
                self.cursor.execute("INSERT INTO users (username, email, password, join_date) VALUES (?, ?, ?, ?)",
                                    (username, email, hashed_password, datetime.now().strftime("%Y-%m-%d")))
            return "User registered successfully!"
        except sqlite3.IntegrityError:
            return "Username or email already exists."

    def validate_user(self, username, password):
        """Validates user credentials and returns user info if valid."""
        hashed_password = self.hash_password(password)
        self.cursor.execute("SELECT id, username, email FROM users WHERE username=? AND password=?",
                            (username, hashed_password))
        return self.cursor.fetchone()

    def get_logged_in_username(self):
        """Fetch the logged-in username from the app."""
        app = App.get_running_app()
        return getattr(app, 'logged_in_user', None)

    def get_email(self, username):
        """Fetches the email associated with a username."""
        self.cursor.execute("SELECT email FROM users WHERE username=?", (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_user_info(self, username):
        """Fetch user details and body measurements."""
        self.cursor.execute("SELECT username, email, join_date FROM users WHERE username=?", (username,))
        user = self.cursor.fetchone()

        if user is None:
            print(f"User '{username}' not found in the database!")
            return None  # Prevents crashing

        self.cursor.execute("SELECT weight, height, body_fat, bmi FROM body_measurements WHERE username=?", (username,))
        measurements = self.cursor.fetchone()

        return {
            "username": user[0],
            "email": user[1],
            "join_date": user[2],
            "weight": measurements[0] if measurements else 0,
            "height": measurements[1] if measurements else 0,
            "body_fat": measurements[2] if measurements else 0,
            "bmi": measurements[3] if measurements else 0,
        }

    # ==================== WORKOUT FUNCTIONS ==================== #
    def add_workout(self, username, workout_type, duration, calories):
        """Logs a new workout entry for a user."""
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            self.cursor.execute("""
                INSERT INTO workouts (username, workout_type, duration, calories, date) 
                VALUES (?, ?, ?, ?, ?)""", 
                (username, workout_type, duration, calories, date)
            )

    def get_workout_summary(self, username):
        """Retrieves a summary of a user's workouts."""
        self.cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(duration), 0), COALESCE(SUM(calories), 0) 
            FROM workouts WHERE username=?""", 
            (username,))
        result = self.cursor.fetchone()

        return {
            "total_workouts": result[0],
            "total_time": result[1],
            "total_calories": result[2]
        }

    def get_workout_history(self, username, limit=10):
        """Fetches the last `limit` workout records for a user."""
        self.cursor.execute("""
            SELECT id, workout_type, duration, calories, date 
            FROM workouts 
            WHERE username=? 
            ORDER BY date DESC 
            LIMIT ?""", 
            (username, limit))
        
        return [
            {"id": row[0], "workout_type": row[1], "duration": row[2], "calories": row[3], "date": row[4]}
            for row in self.cursor.fetchall()
        ]

    # ==================== TEAMS FUNCTIONS ==================== #
    def get_user_team(self, username):
        """Returns the team name of the user, or None if not in a team."""
        self.cursor.execute("SELECT team_name FROM team_members WHERE username = ?", (username,))
        result = self.cursor.fetchone()
    
        if result:
            print(f"User '{username}' is in team '{result[0]}'")  # Debugging log
            return result[0]  # Return team name
        else:
            print(f"User '{username}' is NOT in a team!")  # Debugging log
            return None  # No team found

    def get_teams(self):
        """Fetches all teams from the database along with the number of members."""
        self.cursor.execute("""
            SELECT teams.name, COUNT(team_members.username) 
            FROM teams 
            LEFT JOIN team_members ON teams.name = team_members.team_name 
            GROUP BY teams.name
        """)
        teams = self.cursor.fetchall()

        return [{"name": row[0], "members": row[1]} for row in teams]
    
    def join_team(self, team_name, username):
        """Allows a user to join an existing team if they are not already in it."""
        self.cursor.execute("SELECT name FROM teams WHERE name = ?", (team_name,))
        if not self.cursor.fetchone():
            return False  # Team does not exist

        with self.conn:
            self.cursor.execute("INSERT OR IGNORE INTO team_members (team_name, username) VALUES (?, ?)", 
                                (team_name, username))
        return True  # Successfully joined the team



    def add_team(self, team_name, username):
        """Creates a new team and assigns the creator as the admin."""
        self.cursor.execute("SELECT name FROM teams WHERE name = ?", (team_name,))
        if self.cursor.fetchone():
            return False  # Team already exists

        with self.conn:
            self.cursor.execute("INSERT INTO teams (name, creator) VALUES (?, ?)", (team_name, username))  
            self.cursor.execute("INSERT INTO team_members (team_name, username) VALUES (?, ?)", (team_name, username))  

        print(f"Team '{team_name}' created by '{username}' (Admin)")  # Debugging log
        return True  # Team created successfully

    
    def delete_team(self, admin_username, team_name):
        """Deletes the team and removes all members (Admin Only)."""
        if not self.is_team_admin(admin_username, team_name):
            return False  # Only the creator can delete the team

        with self.conn:
            self.cursor.execute("DELETE FROM team_members WHERE team_name = ?", (team_name,))
            self.cursor.execute("DELETE FROM teams WHERE name = ?", (team_name,))

        return True  # Team deleted successfully


    def is_team_admin(self, username, team_name):
        """Checks if a user is the admin (creator) of a given team."""
        self.cursor.execute("SELECT creator FROM teams WHERE name = ?", (team_name,))
        result = self.cursor.fetchone()
    
        if result and result[0] == username:
            print(f"'{username}' is the admin of '{team_name}'")  # Debugging log
            return True  
        else:
            print(f"'{username}' is NOT the admin of '{team_name}'")  # Debugging log
            return False
        
    def check_user_team(self):
        """Checks if the user is in a team and updates admin status."""
        db = Database()
        self.current_team = db.get_user_team(self.username)  # Fetch team
        self.is_admin = db.is_team_admin(self.username, self.current_team) if self.current_team else False
        db.close()

        if self.current_team:
            print(f"Current Team: {self.current_team}, Admin: {self.is_admin}")  # Debugging log
            self.show_popup("Team Info", f"You are in Team: {self.current_team}")
        else:
            print(f"No team found for user '{self.username}'")  # Debugging log
            self.show_popup("No Team", "You are not in a team.")



    def get_team_members(self, team_name):
        """Returns all members of a given team."""
        self.cursor.execute("SELECT username FROM team_members WHERE team_name = ?", (team_name,))
        return [row[0] for row in self.cursor.fetchall()]

    def leave_team(self, username):
        """Removes the user from their team."""
        team_name = self.get_user_team(username)
        if not team_name:
            return False

        with self.conn:
            self.cursor.execute("DELETE FROM team_members WHERE username = ?", (username,))

        return True

    def delete_team(self, admin_username, team_name):
        """Deletes the team and removes all members (Admin Only)."""
        if not self.is_team_admin(admin_username, team_name):
            return False

        with self.conn:
            self.cursor.execute("DELETE FROM team_members WHERE team_name = ?", (team_name,))
            self.cursor.execute("DELETE FROM teams WHERE name = ?", (team_name,))

        return True

    # ==================== GENERAL FUNCTIONS ==================== #
    def reset_workout_summary(self, username):
        """Deletes all workout data for the given user, effectively resetting their summary."""
        with self.conn:
            self.cursor.execute("DELETE FROM workouts WHERE username = ?", (username,))

    def close(self):
        """Closes the database connection."""
        self.conn.close()
