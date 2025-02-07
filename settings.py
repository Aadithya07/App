from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore("settings.json")  # Persistent storage

    def on_enter(self):
        """Load saved settings and apply theme when entering the settings screen."""
        self.load_settings()

    def toggle_theme(self, is_dark):
        """Toggle between light and dark mode and update UI accordingly."""
        app = App.get_running_app()
        app.theme = "dark" if is_dark else "light"

        # Change background and text colors
        if app.theme == "dark":
            Window.clearcolor = (0, 0, 0, 1)  # Black background
            text_color = (1, 1, 1, 1)  # White text
        else:
            Window.clearcolor = (1, 1, 1, 1)  # White background
            text_color = (0, 0, 0, 1)  # Black text

        # Apply text color updates
        self.update_text_colors(text_color)

        # Save to storage
        self.store.put("settings", theme=app.theme)
        print(f"Theme changed to: {app.theme}")

    def update_text_colors(self, color):
        """Updates the text color for all labels and widgets in settings."""
        self.ids.settings_label.color = color
        self.ids.theme_label.color = color
        self.ids.unit_label.color = color
        self.ids.timer_label.color = color

    def change_units(self, unit_choice):
        """Change units between metric (kg/cm) and imperial (lbs/inches)."""
        app = App.get_running_app()
        app.units = unit_choice
        self.store.put("settings", units=unit_choice)
        print(f"Units changed to: {unit_choice}")

    def change_timer_mode(self, mode):
        """Switch between Stopwatch and Countdown Timer."""
        app = App.get_running_app()
        app.timer_mode = mode
        self.store.put("settings", timer_mode=mode)
        print(f"Timer mode set to: {mode}")

    def logout(self):
        """Log out and return to login screen."""
        app = App.get_running_app()
        app.logged_in_user = None  # Clear logged-in user
        self.manager.current = "login"
        print("User logged out!")

    def go_back_home(self):
        """Navigates back to the home screen."""
        self.manager.current = "home"
        print("Back to Home")

    def load_settings(self):
        """Load settings from storage and apply them."""
        if self.store.exists("settings"):
            settings = self.store.get("settings")

            # Apply saved settings
            app = App.get_running_app()
            app.theme = settings.get("theme", "light")
            app.units = settings.get("units", "kg/cm")
            app.timer_mode = settings.get("timer_mode", "Stopwatch")

            # Apply theme
            is_dark = app.theme == "dark"
            self.ids.theme_switch.active = is_dark

            if is_dark:
                Window.clearcolor = (0, 0, 0, 1)  # Dark mode background
                text_color = (1, 1, 1, 1)  # White text
            else:
                Window.clearcolor = (1, 1, 1, 1)  # Light mode background
                text_color = (0, 0, 0, 1)  # Black text

            self.update_text_colors(text_color)
