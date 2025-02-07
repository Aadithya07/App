from kivy.uix.screenmanager import Screen

class FavoritesScreen(Screen):
    def __init__(self, meal_plan_screen, **kwargs):
        super().__init__(**kwargs)
        self.meal_plan_screen = meal_plan_screen  # Reference to MealPlanScreen

    def load_favorites(self):
        """Loads the saved favorite meals into the list."""
        self.ids.favorites_list.text = "\n".join(self.meal_plan_screen.favorites) or "No favorites yet!"

    def clear_favorites(self):
        """Clears the favorites list."""
        self.meal_plan_screen.favorites.clear()
        self.load_favorites()
