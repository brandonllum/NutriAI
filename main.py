from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from screens import DashboardScreen, ScheduleScreen, ChatScreen, ProfileScreen
from components import TopBar, NavBar

# Set mobile aspect ratio (9:16) and white background
Window.size = (360, 640)
Window.clearcolor = (1, 1, 1, 1)  # White background

class MainApp(App):
    def build(self):
        # Create screen manager
        self.sm = ScreenManager()
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        self.sm.add_widget(ScheduleScreen(name='schedule'))
        self.sm.add_widget(ChatScreen(name='chat'))
        self.sm.add_widget(ProfileScreen(name='profile'))
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Add top bar
        top_bar = TopBar()
        top_bar.profile_btn.bind(on_press=lambda x: self.switch_screen('profile'))
        main_layout.add_widget(top_bar)
        
        # Add screen manager
        main_layout.add_widget(self.sm)
        
        # Create navigation bar
        self.nav_bar = NavBar(self.sm, self)
        main_layout.add_widget(self.nav_bar)
        
        return main_layout
    
    def switch_screen(self, screen_name):
        self.sm.current = screen_name
        # Update button colors
        self.nav_bar.update_button_colors(screen_name)

if __name__ == '__main__':
    MainApp().run()