# screens.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse, RoundedRectangle
from kivy.core.window import Window
from components import TopBar, ProfileIconButton

# [Keep all your existing screen classes exactly as they were]
# Only the TopBar in components.py has been modified to include the profile icon

class CircleIconButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Fully transparent
        self.color = (0, 0, 0, 0)  # Hide default text rendering
        
        with self.canvas.before:
            # Blue circle background
            Color(0.2, 0.6, 0.8, 1)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
            
            # White icon/text
            Color(1, 1, 1, 1)
            self.text_rect = Rectangle(
                texture=self.texture,
                size=self.texture_size,
                pos=(
                    self.center_x - self.texture_size[0]/2,
                    self.center_y - self.texture_size[1]/2
                )
            )
        
        self.bind(
            pos=self.update_graphics,
            size=self.update_graphics,
            texture=self.update_texture
        )
    
    def update_graphics(self, *args):
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size
        self.update_texture()
    
    def update_texture(self, *args):
        self.text_rect.texture = self.texture
        self.text_rect.size = self.texture_size
        self.text_rect.pos = (
            self.center_x - self.texture_size[0]/2,
            self.center_y - self.texture_size[1]/2
        )

class RoundedTextInputWithButton(BoxLayout):
    def __init__(self, button_icon="", **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(50)
        self.orientation = 'horizontal'
        self.padding = [dp(15), dp(5), dp(5), dp(5)]
        self.spacing = dp(5)
        
        # Create rounded background for input
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(25)]
            )
        
        # Text input field
        self.text_input = TextInput(
            background_normal='',
            background_active='',
            background_color=(0,0,0,0),  # Transparent
            foreground_color=(0.2, 0.2, 0.2, 1),
            multiline=False,
            padding=[dp(15), dp(10)],
            size_hint=(0.85, 1)
        )
        
        # Circular action button
        self.action_button = CircleIconButton(
            text=button_icon,
            font_size=dp(20),
            bold=True
        )
        
        self.bind(
            pos=self._update_rect,
            size=self._update_rect
        )
        
        self.add_widget(self.text_input)
        self.add_widget(self.action_button)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    @property
    def text(self):
        return self.text_input.text
    
    @text.setter
    def text(self, value):
        self.text_input.text = value

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Title
        title = Label(
            text="Today's Nutrition",
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.6, 0.8, 1),
            bold=True
        )
        layout.add_widget(title)
        
        # Nutrition summary
        summary = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(10),
            padding=dp(10))
        
        macros = ["Calories: 1500/2000", "Protein: 120g", "Carbs: 150g", "Fat: 50g"]
        for macro in macros:
            macro_label = Label(
                text=macro,
                halign='center'
            )
            summary.add_widget(macro_label)
        
        layout.add_widget(summary)
        
        # Food log
        scroll = ScrollView()
        self.food_log = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=dp(15))
        self.food_log.bind(minimum_height=self.food_log.setter('height'))
        
        # Sample food entries
        foods = ["Breakfast: Oatmeal (300 cal)", "Lunch: Chicken Salad (450 cal)", "Snack: Protein Shake (250 cal)"]
        for food in foods:
            food_entry = Label(
                text=food,
                size_hint_y=None,
                height=dp(30),
                halign='left'
            )
            self.food_log.add_widget(food_entry)
        
        scroll.add_widget(self.food_log)
        layout.add_widget(scroll)
        
        # Add food input with circular button
        input_layout = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=(dp(10), dp(5), dp(10), dp(10)))
        
        self.food_input = RoundedTextInputWithButton("+")
        self.food_input.text_input.hint_text = "Add food..."
        self.food_input.action_button.bind(on_press=self.add_food)
        
        input_layout.add_widget(self.food_input)
        layout.add_widget(input_layout)
        
        self.add_widget(layout)
    
    def add_food(self, instance):
        food = self.food_input.text
        if food.strip():
            food_entry = Label(
                text=food,
                size_hint_y=None,
                height=dp(30),
                halign='left'
            )
            self.food_log.add_widget(food_entry)
            self.food_input.text = ''

class ScheduleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Schedule content
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(15),
            padding=dp(15))
        content.bind(minimum_height=content.setter('height'))
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        meals = ["Breakfast", "Lunch", "Dinner", "Snacks"]
        
        for day in days:
            day_card = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(150),
                spacing=dp(5),
                padding=dp(10))
            
            title = Label(
                text=day,
                size_hint_y=None,
                height=dp(30),
                color=(0.2, 0.6, 0.8, 1),
                bold=True
            )
            day_card.add_widget(title)
            
            for meal in meals:
                meal_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(25))
                
                meal_label = Label(
                    text=f"{meal}:",
                    size_hint_x=0.3,
                    halign='left'
                )
                
                meal_entry = Label(
                    text=f"Sample {meal.lower()} meal",
                    size_hint_x=0.7,
                    halign='left',
                    color=(0.4, 0.4, 0.4, 1)
                )
                
                meal_layout.add_widget(meal_label)
                meal_layout.add_widget(meal_entry)
                day_card.add_widget(meal_layout)
            
            content.add_widget(day_card)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Chat content
        scroll = ScrollView()
        self.chat_history = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=dp(15))
        self.chat_history.bind(minimum_height=self.chat_history.setter('height'))
        
        # Welcome message
        welcome_msg = Label(
            text="Welcome to NutriAI!\nHow can I help with your nutrition today?",
            size_hint_y=None,
            height=dp(80),
            halign='center',
            color=(0.2, 0.2, 0.2, 1)
        )
        self.chat_history.add_widget(welcome_msg)
        
        scroll.add_widget(self.chat_history)
        layout.add_widget(scroll)
        
        # Message input with circular send button
        input_layout = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=(dp(10), dp(5), dp(10), dp(10)))
        
        self.user_input = RoundedTextInputWithButton(">")
        self.user_input.text_input.hint_text = "Type your message..."
        self.user_input.action_button.bind(on_press=self.send_message)
        
        input_layout.add_widget(self.user_input)
        layout.add_widget(input_layout)
        
        self.add_widget(layout)
    
    def send_message(self, instance):
        message = self.user_input.text
        if message.strip():
            # Add user message
            user_msg = Label(
                text=message,
                size_hint_y=None,
                height=dp(40),
                halign='right',
                color=(0.2, 0.2, 0.2, 1)
            )
            self.chat_history.add_widget(user_msg)
            self.user_input.text = ''
            
            # Simulate AI response
            self.simulate_ai_response(message)
    
    def simulate_ai_response(self, message):
        def add_response(dt):
            response = Label(
                text="I'm your NutriAI assistant. Let me help with your nutrition goals!",
                size_hint_y=None,
                height=dp(40),
                halign='left',
                color=(0.2, 0.2, 0.2, 1)
            )
            self.chat_history.add_widget(response)
        Clock.schedule_once(add_response, 0.5)

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Profile content
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(15),
            padding=dp(15))
        content.bind(minimum_height=content.setter('height'))
        
        # Profile picture placeholder
        profile_pic = BoxLayout(
            size_hint_y=None,
            height=dp(100),
            orientation='vertical')
        
        with profile_pic.canvas:
            Color(0.8, 0.8, 0.8, 1)
            Ellipse(
                pos=(Window.width/2 - dp(40), Window.height/2 - dp(40)), 
                size=(dp(80), dp(80))
            )
        
        content.add_widget(profile_pic)
        
        # User info
        info_title = Label(
            text="Personal Information",
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.6, 0.8, 1),
            bold=True
        )
        content.add_widget(info_title)
        
        info_fields = [
            "Name: John Doe",
            "Age: 30",
            "Weight: 165 lbs",
            "Height: 5'10\"",
            "Diet: Balanced"
        ]
        
        for field in info_fields:
            field_label = Label(
                text=field,
                size_hint_y=None,
                height=dp(30),
                halign='left'
            )
            content.add_widget(field_label)
        
        # Goals
        goals_title = Label(
            text="Goals",
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.6, 0.8, 1),
            bold=True
        )
        content.add_widget(goals_title)
        
        goals = [
            "Target Weight: 160 lbs",
            "Daily Calories: 2000 kcal",
            "Protein: 150g",
            "Carbs: 200g",
            "Fat: 65g"
        ]
        
        for goal in goals:
            goal_label = Label(
                text=goal,
                size_hint_y=None,
                height=dp(30),
                halign='left'
            )
            content.add_widget(goal_label)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)