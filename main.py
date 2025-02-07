from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from auth import Auth
from home import HomeScreen
from kivy.lang import Builder
from workout import WorkoutScreen
from mealplan import MealPlanScreen  
from favorites import FavoritesScreen  
from teams import TeamsScreen 
from user_profile import ProfileScreen
from settings import SettingsScreen


# Load Kivy files
Builder.load_file("Auth.kv")
Builder.load_file("login.kv")
Builder.load_file("signup.kv")
Builder.load_file("forgot.kv")
Builder.load_file("home.kv")
Builder.load_file("workout.kv")
Builder.load_file("mealplan.kv")  
Builder.load_file("favorites.kv")
Builder.load_file("teams.kv")
Builder.load_file("user_profile.kv")
Builder.load_file("settings.kv")

auth = Auth()

class LoginScreen(Screen):
    def login(self, username, password):
        result = auth.login(username, password)
        self.ids.username.text = ""
        self.ids.password.text = ""
        print(result)  # Replace with a popup later
        if "successful" in result:
            self.manager.current = "home"

class SignupScreen(Screen):
    def signup(self, username, email, password, confirm_password):
        result = auth.register(username, email, password, confirm_password)
        self.ids.username.text = ""
        self.ids.email.text = ""
        self.ids.password.text = ""
        self.ids.confirm_password.text = ""
        print(result)  # Replace with a popup later
        if "successful" in result:
            self.manager.current = "login"

class ForgotScreen(Screen):
    def forgot_password(self, username):
        result = auth.forgot_password(username)
        self.ids.username.text = ""
        print(result)  # Replace with a popup later

class FitnessApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme = "dark"  # Default to dark mode

    def build(self):
        sm = ScreenManager()
        sm.add_widget(Auth(name="auth"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(ForgotScreen(name="forgot"))
        sm.add_widget(HomeScreen(name="home")) 
        sm.add_widget(WorkoutScreen(name="workout"))
        sm.add_widget(TeamsScreen(name="teams"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(SettingsScreen(name="settings"))

        try:
            meal_plan_screen = MealPlanScreen(name="mealplan")
            sm.add_widget(meal_plan_screen)
        except Exception as e:
            print(f"Error loading MealPlanScreen: {e}")

        try:
            favorites_screen = FavoritesScreen(meal_plan_screen, name="favorites")
            sm.add_widget(favorites_screen)
        except Exception as e:
            print(f"Error loading FavoritesScreen: {e}")

        return sm
    
    def toggle_theme(self):
        """Toggles between light and dark mode."""
        self.theme = "dark" if self.theme == "light" else "light"
        print(f"Theme switched to {self.theme}")  

if __name__ == "__main__":
    FitnessApp().run()
