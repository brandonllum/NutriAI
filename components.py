from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty

class ProfileIconButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Transparent
        
        with self.canvas.before:
            # Blue background circle (matches app theme)
            Color(0.2, 0.6, 0.8, 1)
            self.bg_circle = Ellipse(pos=self.pos, size=self.size)
            
            # White user icon
            Color(1, 1, 1, 1)
            # Head (circle)
            self.head = Ellipse(
                pos=(self.center_x - dp(6), self.center_y + dp(4)),
                size=(dp(12), dp(12))
            )
            # Body (shoulders)
            self.body = Rectangle(
                pos=(self.center_x - dp(8), self.center_y - dp(8)),
                size=(dp(16), dp(12))
            )
        
        self.bind(
            pos=self._update_graphics,
            size=self._update_graphics
        )
    
    def _update_graphics(self, instance, value):
        self.bg_circle.pos = instance.pos
        self.bg_circle.size = instance.size
        self.head.pos = (instance.center_x - dp(6), instance.center_y + dp(4))
        self.body.pos = (instance.center_x - dp(8), instance.center_y - dp(8))

class TopBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)
        
        # App title
        title = Label(
            text="NutriAI",
            color=(0.2, 0.6, 0.8, 1),
            bold=True,
            font_size=dp(20),
            size_hint_x=0.8
        )
        
        # Profile icon button
        self.profile_btn = ProfileIconButton()
        
        self.add_widget(title)
        self.add_widget(self.profile_btn)

class NavBar(BoxLayout):
    def __init__(self, screen_manager, app, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.app = app
        self.size_hint_y = None
        self.height = dp(50)
        self.spacing = dp(5)
        self.padding = [dp(5), dp(5)]
        
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Nav buttons
        self.dashboard_btn = Button(
            text='Dashboard',
            background_normal='',
            background_color=(0.2, 0.6, 0.8, 1),  # Blue for active
            color=(1, 1, 1, 1),
            bold=True,
            on_press=lambda x: self.switch_screen('dashboard'))
        
        self.schedule_btn = Button(
            text='Schedule',
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(0.2, 0.2, 0.2, 1),
            bold=True,
            on_press=lambda x: self.switch_screen('schedule'))
        
        self.chat_btn = Button(
            text='Chat',
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(0.2, 0.2, 0.2, 1),
            bold=True,
            on_press=lambda x: self.switch_screen('chat'))
        
        self.add_widget(self.dashboard_btn)
        self.add_widget(self.schedule_btn)
        self.add_widget(self.chat_btn)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def switch_screen(self, screen_name):
        self.screen_manager.current = screen_name
        self.app.switch_screen(screen_name)
    
    def update_button_colors(self, current_screen):
        # Reset all buttons
        buttons = {
            'dashboard': self.dashboard_btn,
            'schedule': self.schedule_btn,
            'chat': self.chat_btn
        }
        
        for name, btn in buttons.items():
            btn.background_color = (0.2, 0.6, 0.8, 1) if name == current_screen else (0, 0, 0, 0)
            btn.color = (1, 1, 1, 1) if name == current_screen else (0.2, 0.2, 0.2, 1)
