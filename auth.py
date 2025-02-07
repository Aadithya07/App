from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from database import Database

class Auth(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()

    def login(self):
        """Logs in the user if credentials are correct."""
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()

        if not username or not password:
            self.ids.status_label.text = "Username and password are required."
            return

        user = self.db.validate_user(username, password)
        if user:
            app = App.get_running_app()
            app.logged_in_user = username
            self.manager.current = "home"
        else:
            self.ids.status_label.text = "Invalid username or password."

    def forgot_password(self):
        """Handles password recovery."""
        username = self.ids.username.text.strip()
        if not username:
            self.ids.status_label.text = "Username is required."
            return

        email = self.db.get_email(username)
        self.ids.status_label.text = f"Password reset instructions sent to {email}" if email else "Username not found."

    def open_register_popup(self):
        """Opens the registration form inside a popup."""
        popup_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        username_input = TextInput(hint_text="Username", size_hint_y=None, height=40)
        email_input = TextInput(hint_text="Email", size_hint_y=None, height=40)
        password_input = TextInput(hint_text="Password", password=True, size_hint_y=None, height=40)
        confirm_password_input = TextInput(hint_text="Confirm Password", password=True, size_hint_y=None, height=40)

        status_label = Label(text="", font_size=14, size_hint_y=None, height=20, color=(1, 0, 0, 1))

        register_button = Button(text="Register", size_hint_y=None, height=50)
        close_button = Button(text="Cancel", size_hint_y=None, height=50)

        popup_layout.add_widget(Label(text="Register", font_size=20, bold=True))
        popup_layout.add_widget(username_input)
        popup_layout.add_widget(email_input)
        popup_layout.add_widget(password_input)
        popup_layout.add_widget(confirm_password_input)
        popup_layout.add_widget(status_label)
        popup_layout.add_widget(register_button)
        popup_layout.add_widget(close_button)

        popup = Popup(title="Register", content=popup_layout, size_hint=(None, None), size=(400, 450))

        def process_registration(instance):
            """Processes the registration and provides feedback."""
            username = username_input.text.strip()
            email = email_input.text.strip()
            password = password_input.text.strip()
            confirm_password = confirm_password_input.text.strip()

            if not username or not email or not password or not confirm_password:
                status_label.text = "All fields are required."
                return

            if " " in username:
                status_label.text = "Username cannot contain spaces."
                return

            if password != confirm_password:
                status_label.text = "Passwords do not match."
                return

            if len(password) < 6:
                status_label.text = "Password must be at least 6 characters."
                return

            response = self.db.add_user(username, email, password)
            if "successfully" in response:
                status_label.text = "Registration successful!"
                popup.dismiss()
            else:
                status_label.text = "Username or Email already exists."

        register_button.bind(on_press=process_registration)
        close_button.bind(on_press=popup.dismiss)

        popup.open()
