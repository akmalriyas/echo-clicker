import customtkinter as ctk
import time
from pynput import mouse
from pynput.keyboard import KeyCode, Key
from clicker_backend import AutoClicker
from config_manager import ConfigManager

class ClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("ECHO CLICKER @akmalriyas")
        self.geometry("450x650") 
        self.resizable(False, False)
        
        # Theme
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color="#0A0A0A") 
        
        # Load Config
        self.config_data = ConfigManager.load_config()
        
        # Backend
        self.clicker = AutoClicker()
        self.clicker.start_thread()
        
        # Restore Hotkey from config
        hk_str = self.config_data.get("hotkey_char", "s")
        new_key = getattr(Key, hk_str, None) # Check if it's a special key (f1, enter...)
        if not new_key:
            if len(hk_str) == 1:
                new_key = KeyCode(char=hk_str)
            else:
                new_key = KeyCode(char='s') # Fallback
        self.clicker.set_hotkey(new_key)
        
        # UI State
        self.is_running = False
        self.picking_location = False
        self.pick_listener = None
        
        # Variables (linked to Config)
        self.init_variables()
        
        # Layout
        self.create_widgets()
        
        # Apply Logic
        self.toggle_always_on_top() # Initial apply
        
        # Update Loop
        self.update_gui_loop()
        
        # Save on close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def init_variables(self):
        c = self.config_data
        self.h_var = ctk.StringVar(value=c["h"])
        self.m_var = ctk.StringVar(value=c["m"])
        self.s_var = ctk.StringVar(value=c["s"])
        self.ms_var = ctk.StringVar(value=c["ms"])
        
        self.btn_var = ctk.StringVar(value=c["btn"])
        self.type_var = ctk.StringVar(value=c["type"])
        self.pos_mode_var = ctk.StringVar(value=c["pos_mode"])
        self.fixed_x_var = ctk.StringVar(value=c["x"])
        self.fixed_y_var = ctk.StringVar(value=c["y"])
        
        self.rand_var = ctk.BooleanVar(value=c["random_enabled"])
        self.rand_amt_var = ctk.StringVar(value=c["random_amt"])
        
        self.repeat_mode_var = ctk.StringVar(value=c["repeat_mode"]) # Infinite, Count
        self.repeat_count_var = ctk.StringVar(value=c["repeat_count"])
        
        self.top_var = ctk.BooleanVar(value=c["on_top"])

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Tabs
        self.grid_rowconfigure(2, weight=0) # Footer (Start)

        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(15, 10), sticky="ew", padx=20)
        
        title_lbl = ctk.CTkLabel(header_frame, text="ECHO CLICKER", font=("Segoe UI Variable Display", 24, "bold"), text_color="#FFFFFF")
        title_lbl.pack(side="left")
        
        self.about_btn = ctk.CTkButton(
            header_frame, text="?", width=30, height=30, 
            fg_color="#222222", hover_color="#333333", 
            command=self.show_about, corner_radius=15
        )
        self.about_btn.pack(side="right")
        
        # Always on Top Switch (Moved to Options Tab per request)
        # top_switch ... removed from header

        # --- TABS ---
        self.tab_view = ctk.CTkTabview(
            self, 
            fg_color="#141414", 
            bg_color="transparent",
            segmented_button_fg_color="#080808",
            segmented_button_selected_color="#00838F", # Slightly brighter Cyan/Teal
            segmented_button_selected_hover_color="#006064",
            segmented_button_unselected_color="#080808",
            segmented_button_unselected_hover_color="#181818",
            text_color="#FFFFFF",
            corner_radius=10,
            width=400,
            height=400
        )
        self.tab_view._segmented_button.configure(font=("Segoe UI", 14, "bold"), height=40)
        
        self.tab_view.grid(row=1, column=0, padx=20, pady=0, sticky="nsew")
        self.tab_view.add("RUN")
        self.tab_view.add("OPTIONS")
        
        self.setup_run_tab()
        self.setup_options_tab()
        
        # --- Footer ---
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=15)
        footer_frame.columnconfigure(0, weight=1)
        
        # Start Button logic
        k = self.clicker.start_stop_key
        if hasattr(k, 'char') and k.char:
            hk_display = k.char.upper()
        else:
            hk_display = k.name.upper()
            
        self.toggle_btn = ctk.CTkButton(
            footer_frame, 
            text=f"START ({hk_display})", 
            font=("Segoe UI", 18, "bold"),
            height=60,
            fg_color="#00F0FF", text_color="black", hover_color="#00D0DF",
            corner_radius=15,
            command=self.toggle_clicking
        )
        self.toggle_btn.grid(row=0, column=0, sticky="ew")

    def setup_run_tab(self):
        tab = self.tab_view.tab("RUN")
        
        # Card 1: Interval
        time_card = self.create_card(tab, "Click Interval")
        time_card.pack(fill="x", padx=10, pady=(10, 5))
        
        time_frame = ctk.CTkFrame(time_card, fg_color="transparent")
        time_frame.pack(pady=10)
        self.create_time_input(time_frame, "Hours", self.h_var)
        self.create_time_input(time_frame, "Mins", self.m_var)
        self.create_time_input(time_frame, "Secs", self.s_var)
        self.create_time_input(time_frame, "Millis", self.ms_var)
        
        # Randomize (Inside Interval Card)
        rand_frame = ctk.CTkFrame(time_card, fg_color="transparent")
        rand_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        rand_chk = ctk.CTkCheckBox(rand_frame, text="Randomize", variable=self.rand_var, font=("Segoe UI", 12), fg_color="#00F0FF", hover_color="#00D0DF", width=80)
        rand_chk.pack(side="left", padx=(10, 5))
        
        ctk.CTkLabel(rand_frame, text="+/-").pack(side="left")
        ctk.CTkEntry(rand_frame, textvariable=self.rand_amt_var, width=40, height=24, fg_color="#0A0A0A").pack(side="left", padx=5)
        ctk.CTkLabel(rand_frame, text="ms").pack(side="left")

        # Card 2: Repeat
        rep_card = self.create_card(tab, "Click Limits")
        rep_card.pack(fill="x", padx=10, pady=10)
        
        # Infinite
        r1 = ctk.CTkRadioButton(rep_card, text="Repeat until stopped", variable=self.repeat_mode_var, value="Infinite", fg_color="#00F0FF")
        r1.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Count
        r2_frame = ctk.CTkFrame(rep_card, fg_color="transparent")
        r2_frame.pack(anchor="w", padx=0, pady=(0, 10))
        
        r2 = ctk.CTkRadioButton(r2_frame, text="Repeat", variable=self.repeat_mode_var, value="Count", fg_color="#00F0FF")
        r2.pack(side="left", padx=15)
        
        ctk.CTkEntry(r2_frame, textvariable=self.repeat_count_var, width=50, height=24, fg_color="#0A0A0A").pack(side="left", padx=5)
        ctk.CTkLabel(r2_frame, text="times").pack(side="left")

    def setup_options_tab(self):
        tab = self.tab_view.tab("OPTIONS")
        
        # Card 1: Mouse Settings
        mouse_card = self.create_card(tab, "Mouse Settings")
        mouse_card.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(mouse_card, text="Mouse Button:").pack(side="left", padx=15, pady=10)
        ctk.CTkOptionMenu(mouse_card, variable=self.btn_var, values=["Left", "Right", "Middle"], width=80, fg_color="#0A0A0A", button_color="#222222").pack(side="left", padx=5)
        
        ctk.CTkOptionMenu(mouse_card, variable=self.type_var, values=["Single", "Double"], width=80, fg_color="#0A0A0A", button_color="#222222").pack(side="right", padx=15)
        ctk.CTkLabel(mouse_card, text="Type:").pack(side="right", padx=5)
        
        # Card 2: Position
        pos_card = self.create_card(tab, "Positioning")
        pos_card.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkRadioButton(pos_card, text="Current Cursor", variable=self.pos_mode_var, value="Current", fg_color="#00F0FF").pack(anchor="w", padx=15, pady=10)
        
        fix_frame = ctk.CTkFrame(pos_card, fg_color="transparent")
        fix_frame.pack(anchor="w", padx=0, pady=(0, 10))
        ctk.CTkRadioButton(fix_frame, text="Fixed", variable=self.pos_mode_var, value="Fixed", fg_color="#00F0FF").pack(side="left", padx=15)
        
        self.pick_btn = ctk.CTkButton(fix_frame, text="Pick", width=50, height=24, fg_color="#333333", command=self.start_pick_location)
        self.pick_btn.pack(side="left", padx=10)
        
        ctk.CTkLabel(fix_frame, text="X:").pack(side="left")
        ctk.CTkEntry(fix_frame, textvariable=self.fixed_x_var, width=40, height=24, fg_color="#0A0A0A").pack(side="left", padx=2)
        ctk.CTkLabel(fix_frame, text="Y:").pack(side="left")
        ctk.CTkEntry(fix_frame, textvariable=self.fixed_y_var, width=40, height=24, fg_color="#0A0A0A").pack(side="left", padx=2)
        
        # Card 3: System
        sys_card = self.create_card(tab, "System Attributes")
        sys_card.pack(fill="x", padx=10, pady=10)
        
        # Hotkey Config
        hk_frame = ctk.CTkFrame(sys_card, fg_color="transparent")
        hk_frame.pack(fill="x", padx=0, pady=10)
        ctk.CTkLabel(hk_frame, text="Hotkey:").pack(side="left", padx=15)
        self.hk_btn = ctk.CTkButton(hk_frame, text="Change", command=self.change_hotkey_request, fg_color="#222222", hover_color="#333333", width=80, height=24)
        self.hk_btn.pack(side="right", padx=15)
        
        # Top Config
        top_frame = ctk.CTkFrame(sys_card, fg_color="transparent")
        top_frame.pack(fill="x", padx=0, pady=(0, 10))
        
        top_switch = ctk.CTkSwitch(top_frame, text="Keep window always on top", variable=self.top_var, command=self.toggle_always_on_top, font=("Segoe UI", 12), progress_color="#00F0FF")
        top_switch.pack(side="left", padx=15)

    def create_card(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color="#181818", corner_radius=8, border_width=1, border_color="#252525")
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 11, "bold"), text_color="#666666").pack(anchor="w", padx=10, pady=(5, 0))
        return card

    def show_about(self):
        # Create a Toplevel window
        about = ctk.CTkToplevel(self)
        about.title("About")
        about.geometry("300x250") # Increased height
        about.resizable(False, False)
        about.attributes("-topmost", True)
        about.configure(fg_color="#101010")
        
        ctk.CTkLabel(about, text="ECHO CLICKER", font=("Segoe UI", 20, "bold"), text_color="white").pack(pady=(30, 5))
        ctk.CTkLabel(about, text="v2.1", font=("Segoe UI", 14, "bold"), text_color="#FFFFFF").pack(pady=(0, 15)) # Pure white, larger
        ctk.CTkLabel(about, text="Created by Akmal Riyas", font=("Segoe UI", 14), text_color="#00F0FF").pack()


    # --- Logic ---
    def sync_settings(self):
        # Calculate Delay
        try:
            h = int(self.h_var.get() or 0)
            m = int(self.m_var.get() or 0)
            s = int(self.s_var.get() or 0)
            ms = int(self.ms_var.get() or 0)
            delay = (h * 3600) + (m * 60) + s + (ms / 1000.0)
        except:
            delay = 0.1
            
        # Random
        rand_range = 0
        if self.rand_var.get():
            try:
                rand_range = float(self.rand_amt_var.get()) / 1000.0
            except: pass
            
        # Repeat
        rep_mode = self.repeat_mode_var.get()
        try:
            rep_cnt = int(self.repeat_count_var.get())
        except: rep_cnt = 1
        
        self.clicker.update_settings(
            delay=delay,
            button_str=self.btn_var.get(),
            click_type=self.type_var.get(),
            pos_mode=self.pos_mode_var.get(),
            x=self.fixed_x_var.get() or 0,
            y=self.fixed_y_var.get() or 0,
            repeat_mode=rep_mode,
            repeat_count=rep_cnt,
            random_range=rand_range
        )

    def on_close(self):
        # Determine hotkey string to save
        k = self.clicker.start_stop_key
        if hasattr(k, 'char') and k.char:
            hk_str = k.char
        else:
            hk_str = k.name
            
        # Save settings
        cfg = {
            "h": self.h_var.get(), "m": self.m_var.get(), "s": self.s_var.get(), "ms": self.ms_var.get(),
            "btn": self.btn_var.get(), "type": self.type_var.get(),
            "pos_mode": self.pos_mode_var.get(), "x": self.fixed_x_var.get(), "y": self.fixed_y_var.get(),
            "hotkey_char": hk_str, # Save the robust string
            "random_enabled": self.rand_var.get(), "random_amt": self.rand_amt_var.get(),
            "repeat_mode": self.repeat_mode_var.get(), "repeat_count": self.repeat_count_var.get(),
            "on_top": self.top_var.get()
        }
        ConfigManager.save_config(cfg)
        self.clicker.running = False
        self.destroy()

    # Reuse previous helpers for Pick, Hotkey, Top, TimeInput, StartToggle...
    def create_time_input(self, parent, label, var):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=5)
        ctk.CTkEntry(frame, textvariable=var, width=60, height=40, font=("Segoe UI", 18), justify="center", fg_color="#0A0A0A", border_color="#333333").pack()
        ctk.CTkLabel(frame, text=label, font=("Segoe UI", 10), text_color="#666666").pack()
        
    def show_about(self):
        about = ctk.CTkToplevel(self)
        about.title("About")
        about.geometry("300x200")
        about.attributes("-topmost", True)
        ctk.CTkLabel(about, text="ECHO CLICKER", font=("Segoe UI", 20, "bold")).pack(pady=(30, 10))
        ctk.CTkLabel(about, text="Created by Akmal Riyas", font=("Segoe UI", 14), text_color="#00F0FF").pack()
        
    def toggle_always_on_top(self):
        self.attributes("-topmost", self.top_var.get())
        
    def start_pick_location(self):
        self.pick_btn.configure(text="...", fg_color="#E5C07B", text_color="black")
        self.picking_location = True
        self.pick_listener = mouse.Listener(on_click=self.on_pick_click)
        self.pick_listener.start()

    def on_pick_click(self, x, y, button, pressed):
        if pressed and self.picking_location:
            self.picking_location = False
            self.after(10, lambda: self.finish_pick(x, y))
            return False

    def finish_pick(self, x, y):
        self.fixed_x_var.set(str(int(x)))
        self.fixed_y_var.set(str(int(y)))
        self.pos_mode_var.set("Fixed")
        self.pick_btn.configure(text="Pick", fg_color="#333333", text_color="white")

    def change_hotkey_request(self):
        self.hk_btn.configure(text="Press now...", fg_color="#E5C07B", text_color="black")
        self.focus_set()
        self.bind("<Key>", self.on_hotkey_press)
        
    def on_hotkey_press(self, event):
        new_char = event.char
        keysym = event.keysym.lower()
        from pynput.keyboard import Key
        new_key = None
        display_text = ""
        if len(new_char) == 1 and new_char.isprintable():
            new_key = KeyCode(char=new_char)
            display_text = new_char.upper()
        else:
            display_text = keysym.upper()
            try: new_key = getattr(Key, keysym, None)
            except: pass
            if new_key is None:
                if keysym == "return": new_key = Key.enter
                elif keysym == "escape": new_key = Key.esc
                elif keysym == "space": new_key = Key.space
        
        if new_key or display_text:
            if not new_key: new_key = KeyCode(char=display_text.lower())
            self.clicker.set_hotkey(new_key)
            self.hk_btn.configure(text="Change Hotkey", fg_color="#222222", text_color="white")
            self.toggle_btn.configure(text=f"START ({display_text})")
        self.unbind("<Key>")

    def toggle_clicking(self):
        self.sync_settings()
        self.clicker.toggle_clicking()
        self.update_ui_state()

    def update_ui_state(self):
        if self.clicker.clicking:
            self.toggle_btn.configure(text="STOP", fg_color="#FF3333", hover_color="#CC2222")
        else:
            hk_display = self.clicker.start_stop_key.char.upper() if hasattr(self.clicker.start_stop_key, 'char') else '?'
            self.toggle_btn.configure(text=f"START ({hk_display})", fg_color="#00F0FF", hover_color="#00D0DF")

    def update_gui_loop(self):
        if self.clicker.clicking != self.is_running:
            self.is_running = self.clicker.clicking
            self.update_ui_state()
        self.after(50, self.update_gui_loop)
