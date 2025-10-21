from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class CounterApp(App):
    def build(self):
        # Create the layout (vertical)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Create a label to display the count
        self.count = 0
        self.label = Label(text=str(self.count), font_size=48)

        # Create a button to increment the count
        button = Button(text='Increment', font_size=24, size_hint=(1, 0.4))
        button.bind(on_press=self.increment_count)

        # Add widgets to the layout
        layout.add_widget(self.label)
        layout.add_widget(button)

        return layout

    def increment_count(self, instance):
        self.count += 1
        self.label.text = str(self.count)

if __name__ == '__main__':
    CounterApp().run()

