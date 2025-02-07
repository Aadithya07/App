from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App
from database import Database

class WorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_running = False
        self.timer_seconds = 0

    def on_enter(self):
        """Fetch the logged-in username when entering the screen."""
        app = App.get_running_app()
        self.username = getattr(app, 'logged_in_user', None)

        if not self.username:
            print("No logged-in user found!")
            self.ids.workout_log.text = "[b]Error: No logged-in user![/b]"
            return  # Prevent errors if no user is logged in

        self.load_workout_history()

    def start_timer(self):
        """Starts the workout timer."""
        if not self.timer_running:
            self.timer_running = True
            Clock.schedule_interval(self.update_timer, 1)

    def stop_timer(self):
        """Stops the workout timer."""
        if self.timer_running:
            self.timer_running = False
            Clock.unschedule(self.update_timer)

    def reset_timer(self):
        """Resets the timer to zero."""
        self.stop_timer()
        self.timer_seconds = 0
        self.ids.timer_label.text = "00:00"

    def update_timer(self, dt):
        """Updates the timer display every second."""
        self.timer_seconds += 1
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.ids.timer_label.text = f"{minutes:02}:{seconds:02}"

    def log_workout(self):
        """Logs the completed workout to the database."""
        if not hasattr(self, 'username') or not self.username:
            self.ids.workout_log.text = "[b]Error: No logged-in user![/b]"
            return

        workout_type = self.ids.workout_type_spinner.text
        calories_burned = int(self.ids.calories_slider.value)
        duration = self.timer_seconds // 60  # Convert seconds to minutes

        if workout_type == "Select Workout":
            self.ids.workout_log.text = "[b]Please select a workout type![/b]"
            return

        db = Database()
        db.add_workout(self.username, workout_type, duration, calories_burned)
        db.close()

        self.ids.workout_log.text = "[b]Workout Logged Successfully![/b]"
        self.load_workout_history()  # Refresh workout history

    def load_workout_history(self):
        """Loads the workout history from the database and updates the UI."""
        if not hasattr(self, 'username') or not self.username:
            self.ids.workout_history.text = "[b]Error: No logged-in user![/b]"
            return

        db = Database()
        history = db.get_workout_history(self.username)
        db.close()

        if history:
            history_text = "\n".join([
                f"{entry['workout_type']} - {entry['duration']} mins, {entry['calories']} kcal ({entry['date']})"
                for entry in history
            ])
            self.ids.workout_history.text = f"[b]Workout History:[/b]\n{history_text}"
        else:
            self.ids.workout_history.text = "[b]No past workouts found.[/b]"

    def go_back(self):
        """Navigates back to the home screen."""
        self.manager.current = "home"
