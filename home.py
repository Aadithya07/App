from kivy.uix.screenmanager import Screen
import random
from kivy.app import App
from database import Database  # Import the database module

class HomeScreen(Screen):
    def on_pre_enter(self):
        """Called before entering the screen to update the dashboard."""
        self.update_dashboard()

    def update_dashboard(self):
        """Fetches and updates the workout summary, goals, and motivational quote."""
        db = Database()
        username = self.get_logged_in_user()  # Get the actual logged-in user
        summary = db.get_workout_summary(username)  # Fetch summary for current user
        db.close()

        goals = {
            "steps": "10,000",
            "water": "2.5L",
            "calories": "2,000 kcal"
        }

        motivational_quotes = [
            "Push yourself, because no one else is going to do it for you.",
            "The body achieves what the mind believes.",
            "Success starts with self-discipline."
        ]

        self.ids.workout_summary.text = (
            f"[b]Workout Summary:[/b]\n"
            f"Total Workouts: {summary['total_workouts']}\n"
            f"Total Time: {summary['total_time']} mins\n"
            f"Total Calories Burned: {summary['total_calories']} kcal"
        )
        self.ids.today_goals.text = (
            f"[b]Today’s Goals:[/b]\n"
            f"Steps: {goals['steps']}\n"
            f"Water: {goals['water']}\n"
            f"Calories: {goals['calories']}"
        )
        self.ids.motivation.text = random.choice(motivational_quotes)

    def refresh_summary(self):
        """Refreshes the workout summary when the user presses the refresh button."""
        print("Refreshing workout summary...")
        self.update_dashboard()

    def reset_summary(self):
        """Resets the workout summary by deleting all records from the database."""
        db = Database()
        username = self.get_logged_in_user()
        db.reset_workout_summary(username)  # Call the reset function in database
        db.close()

        self.ids.workout_summary.text = (
            f"[b]Workout Summary:[/b]\n"
            f"Total Workouts: 0\n"
            f"Total Time: 0 mins\n"
            f"Total Calories Burned: 0 kcal"
        )
        self.ids.today_goals.text = "[b]Today’s Goals:[/b]\nSteps: 0\nWater: 0L\nCalories: 0 kcal"
        self.ids.motivation.text = "Workout data has been reset."

    def go_to(self, screen_name):
        """Navigates to a different screen."""
        self.manager.current = screen_name

    def get_logged_in_user(self):
        """Fetches the logged-in user from the app instance."""
        app = self.get_app_instance()
        return getattr(app, 'logged_in_user', "test_user")  # Default to test_user

    def get_app_instance(self):
        """Returns the running Kivy app instance."""
        from kivy.app import App
        return App.get_running_app()
