from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserIconView
from database import Database
from kivy.app import App

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = "test_user"  # Replace with actual logged-in user

    def on_enter(self):
        """Load user data when entering the screen."""
        app = App.get_running_app()
        self.username = app.logged_in_user
        self.load_profile()

    def load_profile(self):
        """Fetch user details and update UI."""
        db = Database()
        user = db.get_user_info(self.username)
        if user is None:
            print("⚠️ User not found! Cannot load profile.")
            return

        if user:
            self.ids.username_label.text = f"Username: {user['username']}"
            self.ids.email_label.text = f"Email: {user['email']}"
            self.ids.join_date_label.text = f"Joined: {user['join_date']}"
            self.ids.weight_label.text = f"Weight: {user['weight']} kg"
            self.ids.height_label.text = f"Height: {user['height']} cm"
            self.ids.body_fat_label.text = f"Body Fat: {user['body_fat']}%"
            self.ids.bmi_label.text = f"BMI: {user['bmi']}"
        else:
            self.show_popup("Error", "User not found!")

    def update_measurements_popup(self):
        """Popup to update weight, height, and body fat percentage."""
        popup_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        weight_input = TextInput(hint_text="Enter weight (kg)", size_hint_y=None, height=40)
        height_input = TextInput(hint_text="Enter height (cm)", size_hint_y=None, height=40)
        body_fat_input = TextInput(hint_text="Enter body fat %", size_hint_y=None, height=40)

        update_button = Button(text="Update", size_hint_y=None, height=50)
        close_button = Button(text="Cancel", size_hint_y=None, height=50)

        popup_layout.add_widget(Label(text="Update Body Measurements:", size_hint_y=None, height=30))
        popup_layout.add_widget(weight_input)
        popup_layout.add_widget(height_input)
        popup_layout.add_widget(body_fat_input)
        popup_layout.add_widget(update_button)
        popup_layout.add_widget(close_button)

        popup = Popup(title="Update Measurements", content=popup_layout, size_hint=(None, None), size=(400, 350))

        def update_action(instance):
            db = Database()
            db.update_measurements(self.username, float(weight_input.text), float(height_input.text), float(body_fat_input.text))
            db.close()
            self.load_profile()
            popup.dismiss()

        update_button.bind(on_press=update_action)
        close_button.bind(on_press=popup.dismiss)

        popup.open()

    def show_popup(self, title, message):
        """Creates and displays a popup with the given title and message."""
        popup_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        popup_label = Label(text=message, font_size=16, size_hint_y=None, height=100)
        close_button = Button(text="OK", size_hint_y=None, height=50)

        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(close_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(None, None), size=(400, 300))
        close_button.bind(on_press=popup.dismiss)

        popup.open()
