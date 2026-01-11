from gui import ClickerApp
from pynput.keyboard import Listener, KeyCode

# Separate thread for hotkey listening or integrate?
# pynput listener is blocking if join() is called, but we can run it non-blocking.

def run_app():
    app = ClickerApp()
    
    # We need to bridge the hotkey listener to the app logic
    # The listener needs to run in the background
    
    def on_press(key):
        # Check against the current configured hotkey in the clicker backend
        try:
            current_hotkey = app.clicker.start_stop_key
            if key == current_hotkey:
                app.toggle_clicking()
            elif hasattr(key, 'char') and hasattr(current_hotkey, 'char') and key.char == current_hotkey.char:
                app.toggle_clicking()
        except AttributeError:
            pass
            
    listener = Listener(on_press=on_press)
    listener.start()
    
    app.mainloop()
    
    # Cleanup
    listener.stop()
    app.clicker.running = False # Stop backend thread

if __name__ == "__main__":
    run_app()
