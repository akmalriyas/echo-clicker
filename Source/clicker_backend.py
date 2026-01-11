import time
import threading
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode

class AutoClicker:
    def __init__(self):
        self.mouse = Controller()
        self.clicking = False
        self.running = False  # Used to kill the thread if needed
        self.thread = None
        
        
        # Settings
        self.delay = 0.1
        self.button = Button.left
        self.click_type = "Single" # or "Double"
        self.start_stop_key = KeyCode(char='s')
        
        # Position Settings
        self.position_mode = "Current" # or "Fixed"
        self.fixed_x = 0
        self.fixed_y = 0

        # Advanced Settings
        self.repeat_mode = "Infinite" # or "Count"
        self.repeat_count = 1
        self.random_range = 0 # in seconds
        
    def set_hotkey(self, key):
        self.start_stop_key = key
    
    def update_settings(self, delay, button_str, click_type, pos_mode, x=0, y=0, 
                        repeat_mode="Infinite", repeat_count=1, random_range=0):
        self.delay = delay
        
        # Map string to Button object
        if button_str == "Left": self.button = Button.left
        elif button_str == "Right": self.button = Button.right
        elif button_str == "Middle": self.button = Button.middle
        
        self.click_type = click_type
        self.position_mode = pos_mode
        self.fixed_x = int(x)
        self.fixed_y = int(y)
        
        self.repeat_mode = repeat_mode
        self.repeat_count = int(repeat_count)
        self.random_range = float(random_range)
        
    def start_clicking(self):
        self.clicking = True
        self.clicks_done = 0
        
    def stop_clicking(self):
        self.clicking = False
        
    def toggle_clicking(self):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def run(self):
        """Main loop for the clicking thread"""
        self.running = True
        import random
        while self.running:
            if self.clicking:
                # Handle Position
                if self.position_mode == "Fixed":
                    self.mouse.position = (self.fixed_x, self.fixed_y)
                
                # Handle Click Type
                if self.click_type == "Double":
                    self.mouse.click(self.button, 2)
                else:
                    self.mouse.click(self.button, 1)
                
                # Handle Repeat
                if self.repeat_mode == "Count":
                    self.clicks_done += 1
                    if self.clicks_done >= self.repeat_count:
                        self.stop_clicking()
                
                # Handle Delay + Random
                actual_delay = self.delay
                if self.random_range > 0:
                    # random offset between -range and +range
                    offset = random.uniform(-self.random_range, self.random_range)
                    actual_delay += offset
                    if actual_delay < 0: actual_delay = 0

                time.sleep(actual_delay)
            else:
                time.sleep(0.01)

    def start_thread(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run)
            self.thread.daemon = True
            self.thread.start()
