from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from database import Database

class TeamsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = "test_user"  # Replace with actual logged-in user

    def on_enter(self):
        """Ensures UI is fully loaded before accessing self.ids."""
        Clock.schedule_once(self.delayed_load, 0.1)

    def delayed_load(self, dt):
        """Checks if user is in a team and updates UI."""
        self.check_user_team()

    def check_user_team(self):
        """Checks if the user is in a team and updates the UI."""
        db = Database()
        self.current_team = db.get_user_team(self.username)
        self.is_admin = db.is_team_admin(self.username, self.current_team) if self.current_team else False
        db.close()

        if self.current_team:
            self.show_popup("Team Info", f"You are in Team: {self.current_team}")
        else:
            self.show_popup("No Team", "You are not in a team.")

    def load_teams(self):
        """Fetches and displays available teams in a popup."""
        db = Database()
        teams = db.get_teams()
        db.close()

        if teams:
            team_list = "\n".join([f"{team['name']} - {team['members']} members" for team in teams])
            self.show_popup("Available Teams", team_list)
        else:
            self.show_popup("No Teams Found", "No teams available. Create one!")

    def create_team(self):
        """Creates a new team and shows a popup with the result."""
        team_name = self.ids.team_name_input.text.strip()
        if not team_name:
            self.show_popup("Error", "Enter a valid team name!")
            return

        db = Database()
        result = db.add_team(team_name, self.username)
        db.close()

        if result:
            self.show_popup("Success", f"Team '{team_name}' created successfully!")
        else:
            self.show_popup("Error", "Team name already exists!")

    def join_team(self):
        """Allows the user to join an existing team and shows a popup."""
        team_name = self.ids.team_join_input.text.strip()
        if not team_name:
            self.show_popup("Error", "Enter a valid team name to join!")
            return

        db = Database()
        result = db.join_team(team_name, self.username)
        db.close()

        if result:
            self.show_popup("Success", f"Joined team '{team_name}' successfully!")
        else:
            self.show_popup("Error", "Team not found or already a member!")

    def leave_team(self):
        """Allows the user to leave their team and shows a popup."""
        db = Database()
        result = db.leave_team(self.username)
        db.close()

        if result:
            self.show_popup("Success", "You left the team successfully!")
        else:
            self.show_popup("Error", "You are not in a team!")

    def show_team_members(self):
        """Displays the members of the user's current team in a popup."""
        db = Database()
        team_name = db.get_user_team(self.username)
        members = db.get_team_members(team_name) if team_name else []
        db.close()

        if team_name and members:
            member_list = "\n".join(members)
            self.show_popup(f"Members of {team_name}", member_list)
        else:
            self.show_popup("No Members", "You are not in a team or the team has no members.")

    def remove_member_popup(self):
        """Shows a popup to remove a team member."""
        if not self.current_team:
            self.show_popup("Error", "You are not in a team!")
            return

        db = Database()
        is_admin = db.is_team_admin(self.username, self.current_team)
        db.close()

        if not is_admin:
            self.show_popup("Error", "Only the team admin can remove members!")
            return

        popup_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        member_input = TextInput(hint_text="Enter member username", size_hint_y=None, height=40)
        remove_button = Button(text="Remove", size_hint_y=None, height=50)
        close_button = Button(text="Cancel", size_hint_y=None, height=50)

        popup_layout.add_widget(Label(text="Enter member username to remove:", size_hint_y=None, height=30))
        popup_layout.add_widget(member_input)
        popup_layout.add_widget(remove_button)
        popup_layout.add_widget(close_button)

        popup = Popup(title="Remove Team Member", content=popup_layout, size_hint=(None, None), size=(400, 300))
        
        def remove_member_action(instance):
            db = Database()
            result = db.remove_member(self.username, self.current_team, member_input.text.strip())
            db.close()

            if result:
                self.show_popup("Success", f"Removed {member_input.text.strip()} from team!")
            else:
                self.show_popup("Error", "Member not found or not removable!")
            popup.dismiss()

        remove_button.bind(on_press=remove_member_action)
        close_button.bind(on_press=popup.dismiss)

        popup.open()

    def delete_team(self):
        """Deletes the team if the user is an admin."""
        if not self.current_team:
            self.show_popup("Error", "You are not in a team!")
            return

        db = Database()
        is_admin = db.is_team_admin(self.username, self.current_team)
        db.close()

        if not is_admin:
            self.show_popup("Error", "Only the team admin can delete the team!")
            return

        def confirm_delete(instance):
            db = Database()
            result = db.delete_team(self.username, self.current_team)
            db.close()

            if result:
                self.show_popup("Success", "Team deleted successfully!")
            else:
                self.show_popup("Error", "Failed to delete team!")

            confirm_popup.dismiss()

        popup_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        popup_layout.add_widget(Label(text="Are you sure you want to delete the team?", size_hint_y=None, height=40))
        confirm_button = Button(text="Delete", size_hint_y=None, height=50)
        cancel_button = Button(text="Cancel", size_hint_y=None, height=50)

        popup_layout.add_widget(confirm_button)
        popup_layout.add_widget(cancel_button)

        confirm_popup = Popup(title="Delete Team", content=popup_layout, size_hint=(None, None), size=(400, 300))
        confirm_button.bind(on_press=confirm_delete)
        cancel_button.bind(on_press=confirm_popup.dismiss)
        confirm_popup.open()

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
