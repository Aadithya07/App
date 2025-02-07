import random
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock  # Added to delay UI updates

# Sample Meal Plans
MEALS = {
    "Muscle Gain": {
        "Breakfast": ["Oats with nuts & banana", "Paneer paratha with curd", "Egg bhurji with roti"],
        "Lunch": ["Grilled chicken with brown rice", "Dal, roti & mixed veggies", "Rajma chawal"],
        "Dinner": ["Fish curry with quinoa", "Soybean curry with rice", "Grilled tofu with veggies"],
        "Snacks": ["Protein shake", "Greek yogurt with fruits", "Handful of almonds & walnuts"]
    },
    "Weight Loss": {
        "Breakfast": ["Moong dal chilla", "Fruit smoothie", "Boiled eggs with green tea"],
        "Lunch": ["Grilled salmon with salad", "Khichdi with curd", "Multigrain roti & sabzi"],
        "Dinner": ["Lentil soup with whole wheat toast", "Chicken soup", "Vegetable stir fry"],
        "Snacks": ["Sprouts salad", "Fox nuts (Makhana)", "Cucumber & carrot sticks"]
    },
    "Maintenance": {
        "Breakfast": ["Poha with peanuts", "Ragi dosa", "Scrambled eggs with toast"],
        "Lunch": ["Vegetable biryani", "Dal, rice & sabzi", "Grilled fish with sweet potatoes"],
        "Dinner": ["Mixed vegetable soup", "Grilled paneer with salad", "Stuffed chapati rolls"],
        "Snacks": ["Roasted chana", "Fruit salad", "Homemade protein bars"]
    }
}

class MealPlanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.goal = "Muscle Gain"  # Default goal
        self.favorites = []
        Clock.schedule_once(self.init_ui, 1)  # Ensure UI is initialized

    def init_ui(self, dt):
        """Ensures labels are initialized before updating meals."""
        self.update_meals(self.goal)

    def update_meals(self, goal):
        """Updates meal suggestions based on the selected goal."""
        if goal not in MEALS:
            print(f"Error: Goal '{goal}' not found in MEALS dictionary!")
            return

        self.goal = goal
        meals = MEALS.get(goal, {})

        # Ensure UI is ready before updating labels
        if not hasattr(self, "ids") or not self.ids:
            print("UI not loaded yet, skipping meal update.")
            return

        try:
            if "breakfast_label" in self.ids:
                self.ids.breakfast_label.text = random.choice(meals.get("Breakfast", ["No meals available"]))
            if "lunch_label" in self.ids:
                self.ids.lunch_label.text = random.choice(meals.get("Lunch", ["No meals available"]))
            if "dinner_label" in self.ids:
                self.ids.dinner_label.text = random.choice(meals.get("Dinner", ["No meals available"]))
            if "snack_label" in self.ids:
                self.ids.snack_label.text = random.choice(meals.get("Snacks", ["No meals available"]))
        except KeyError as e:
            print(f"KeyError: {e} - Ensure all labels exist in mealplan.kv")

    def save_favorite(self, meal):
        """Saves a meal to favorites."""
        if meal and meal not in self.favorites:
            self.favorites.append(meal)
            print(f"Saved to favorites: {meal}")  # Replace with a popup later
