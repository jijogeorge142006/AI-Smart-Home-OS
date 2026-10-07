import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
from datetime import datetime
import threading

try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
    def speak_text(text):
        def _speak():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 130)  
                engine.setProperty('volume', 1.0)
                voices = engine.getProperty('voices')
                for voice in voices:
                    if "female" in voice.name.lower() or "zira" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"Audio Error: {e}")
        threading.Thread(target=_speak, daemon=True).start()
except ImportError:
    TTS_AVAILABLE = False
    def speak_text(text):
        pass


class SmartHomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Smart Home OS - English Voice & Hybrid Edition")
        self.root.geometry("980x1050")
        self.root.minsize(860, 920)

        self.t = {
            "bg": "#0b0f19", "card_bg": "#1e293b", "card_border": "#334155",
            "fg": "#f8fafc", "muted": "#94a3b8", "accent": "#38bdf8",
            "on_green": "#22c55e", "on_green_bg": "#14532d",
            "alarm_red": "#ef4444", "alarm_red_bg": "#7f1d1d",
            "off_bg": "#334155", "off_fg": "#94a3b8"
        }

        # Room-wise Independent Appliance States
        self.rooms = {
            "living": {"name": "Living Room", "light": "OFF", "ac": "OFF", "fan": "OFF"},
            "bedroom": {"name": "Bedroom", "light": "OFF", "ac": "OFF", "fan": "OFF"},
            "kitchen": {"name": "Kitchen", "light": "OFF", "exhaust": "OFF"},
            "security": {"name": "Security Zone", "alarm": "OFF"}
        }

        self.current_bars = {"light": 0, "fan": 0, "ac": 0, "alarm": 0}
        self.target_bars = {"light": 0, "fan": 0, "ac": 0, "alarm": 0}

        self.fan_frame = 0
        self.fan_icons = ["🌀", "🔄", "⚙️", "🔃"]
        self.alarm_flashing = False
        self.alarm_state = False
        self.auto_sim = False
        self.is_auto_listening = False

        self._init_layout()
        self._animate_loops()

    def _init_layout(self):
        self.root.configure(bg=self.t["bg"])

        header = tk.Frame(self.root, bg=self.t["bg"])
        header.pack(fill="x", padx=16, pady=(10, 4))
        tk.Label(header, text="AI SMART HOME OS - ENGLISH VOICE COMMANDS", font=("Segoe UI", 16, "bold"),
                 bg=self.t["bg"], fg=self.t["accent"]).pack(anchor="w")
        tk.Label(header, text="Strictly English Voice Processing & Natural English Audio Output",
                 font=("Segoe UI", 8), bg=self.t["bg"], fg=self.t["on_green"]).pack(anchor="w")

        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=self.t["bg"], borderwidth=0)
        style.configure('TNotebook.Tab', background=self.t["card_bg"], foreground=self.t["fg"], padding=[10, 6], font=("Segoe UI", 9, "bold"))
        style.map('TNotebook.Tab', background=[('selected', self.t["accent"])], foreground=[('selected', '#000000')])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=4)

        self.tab_dashboard = tk.Frame(self.notebook, bg=self.t["bg"])
        self.tab_voice = tk.Frame(self.notebook, bg=self.t["bg"])
        self.tab_blueprint = tk.Frame(self.notebook, bg=self.t["bg"])
        self.tab_analytics = tk.Frame(self.notebook, bg=self.t["bg"])
        self.tab_history = tk.Frame(self.notebook, bg=self.t["bg"])

        self.notebook.add(self.tab_dashboard, text="Dashboard & Percepts")
        self.notebook.add(self.tab_voice, text="English Voice Control")
        self.notebook.add(self.tab_blueprint, text="House Floor Plan")
        self.notebook.add(self.tab_analytics, text="Energy & Power")
        self.notebook.add(self.tab_history, text="AI Logs")

        self._build_dashboard_tab()
        self._build_voice_tab()
        self._build_blueprint_tab()
        self._build_analytics_tab()
        self._build_history_tab()

    def _build_dashboard_tab(self):
        f = self.tab_dashboard

        sensor_card = self._create_card(f, "ENVIRONMENT SENSOR PERCEPTS (RULE ENGINE INPUTS)")
        sensor_card.pack(fill="x", pady=4)

        s_grid = tk.Frame(sensor_card, bg=self.t["card_bg"])
        s_grid.pack(fill="x", padx=10, pady=4)
        s_grid.grid_columnconfigure((1, 3), weight=1)

        self.temp_var = tk.StringVar(value="25")
        self.light_var = tk.StringVar(value="Bright")
        self.motion_var = tk.StringVar(value="Not Detected")
        self.occupied_var = tk.StringVar(value="Yes")
        self.smoke_var = tk.StringVar(value="No")
        self.mode_var = tk.StringVar(value="Normal Mode")

        self._add_input(s_grid, 0, 0, "Temperature (°C):", tk.Spinbox(s_grid, from_=0, to=50, textvariable=self.temp_var, width=8, font=("Segoe UI", 9)))
        self._add_input(s_grid, 0, 2, "Lighting:", ttk.Combobox(s_grid, textvariable=self.light_var, values=["Bright", "Dark"], state="readonly", width=12))
        self._add_input(s_grid, 1, 0, "Motion:", ttk.Combobox(s_grid, textvariable=self.motion_var, values=["Detected", "Not Detected"], state="readonly", width=12))
        self._add_input(s_grid, 1, 2, "Occupancy:", ttk.Combobox(s_grid, textvariable=self.occupied_var, values=["Yes", "No"], state="readonly", width=12))
        self._add_input(s_grid, 2, 0, "Smoke:", ttk.Combobox(s_grid, textvariable=self.smoke_var, values=["Yes", "No"], state="readonly", width=12))
        self._add_input(s_grid, 2, 2, "Profile:", ttk.Combobox(s_grid, textvariable=self.mode_var, values=["Normal Mode", "Energy Saving Mode", "Away Mode"], state="readonly", width=12))

        btn_bar = tk.Frame(f, bg=self.t["bg"])
        btn_bar.pack(fill="x", pady=4)
        self.run_btn = tk.Button(btn_bar, text="Run Agent Decision Engine", command=self.trigger_agent_rules, bg=self.t["accent"], fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=3, cursor="hand2")
        self.run_btn.pack(side="left", padx=(0, 4))
        self.sim_btn = tk.Button(btn_bar, text="Auto Simulation: OFF", command=self.toggle_sim, bg=self.t["card_bg"], fg=self.t["fg"], font=("Segoe UI", 8, "bold"), relief="solid", bd=1, padx=8, pady=3, cursor="hand2")
        self.sim_btn.pack(side="left", padx=4)

        rooms_card = self._create_card(f, "ROOM-WISE MANUAL APPLIANCE TOGGLES")
        rooms_card.pack(fill="x", pady=4)

        r_grid = tk.Frame(rooms_card, bg=self.t["card_bg"])
        r_grid.pack(fill="x", padx=10, pady=6)
        for i in range(3): r_grid.grid_columnconfigure(i, weight=1)

        self.room_tiles = {}
        room_keys = [("living", "🛋️ Living Room"), ("bedroom", "🛏️ Bedroom"), ("kitchen", "🍳 Kitchen")]

        for col, (r_key, r_name) in enumerate(room_keys):
            box = tk.Frame(r_grid, bg=self.t["bg"], bd=1, relief="solid")
            box.grid(row=0, column=col, sticky="nsew", padx=4, pady=4)

            tk.Label(box, text=r_name, font=("Segoe UI", 9, "bold"), bg=self.t["bg"], fg=self.t["accent"]).pack(pady=(4, 2))
            
            self.room_tiles[r_key] = {}
            for app_key in self.rooms[r_key]:
                if app_key == "name": continue
                btn = tk.Button(box, text=f"{app_key.upper()}: OFF", font=("Segoe UI", 8, "bold"),
                                bg=self.t["off_bg"], fg=self.t["off_fg"], relief="flat",
                                command=lambda r=r_key, a=app_key: self.toggle_room_appliance(r, a), cursor="hand2")
                btn.pack(fill="x", padx=8, pady=2)
                self.room_tiles[r_key][app_key] = btn

        sc_card = self._create_card(f, "QUICK SCENARIOS & SYSTEM RESET")
        sc_card.pack(fill="x", pady=4)

        sc_top = tk.Frame(sc_card, bg=self.t["card_bg"])
        sc_top.pack(fill="x", padx=10, pady=4)
        for name, cmd in [("Fire Hazard", self._preset_fire), ("Intruder", self._preset_intruder), ("Hot Summer", self._preset_summer), ("Night Rest", self._preset_night)]:
            tk.Button(sc_top, text=name, command=cmd, font=("Segoe UI", 8, "bold"), bg=self.t["bg"], fg=self.t["fg"], relief="flat", padx=6, pady=2, cursor="hand2").pack(side="left", padx=3)

        tk.Button(sc_top, text="Reset All", command=self.reset_system, bg="#7f1d1d", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=2, cursor="hand2").pack(side="right", padx=3)

        self.alert_ribbon = tk.Label(f, text="ALL SYSTEMS NOMINAL - HOUSE SECURE", font=("Segoe UI", 9, "bold"), bg=self.t["on_green_bg"], fg=self.t["on_green"], pady=6)
        self.alert_ribbon.pack(fill="x", pady=4)

    def _build_voice_tab(self):
        f = self.tab_voice
        card = self._create_card(f, "ENGLISH VOICE CONTROL CENTER")
        card.pack(fill="both", expand=True, pady=10)

        v_inner = tk.Frame(card, bg=self.t["card_bg"])
        v_inner.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(v_inner, text="🗣️ English Voice Assistant (Strictly English Input & Output)", font=("Segoe UI", 11, "bold"),
                 bg=self.t["card_bg"], fg=self.t["accent"]).pack(pady=(10, 5))
        tk.Label(v_inner, text="Speak English commands clearly:\n• 'Turn on the living room light'\n• 'Turn on the bedroom AC'\n• 'Turn off the fan'\n• 'Fire hazard' / 'Intruder alert'", font=("Segoe UI", 9),
                 bg=self.t["card_bg"], fg=self.t["muted"], justify="center").pack(pady=(0, 20))

        self.auto_voice_btn = tk.Button(v_inner, text="🟢 English Voice Assistant: OFF", command=self.toggle_auto_voice,
                                        bg="#37474f", fg="#ffffff", font=("Segoe UI", 11, "bold"), padx=20, pady=10, cursor="hand2")
        self.auto_voice_btn.pack(pady=10)

        self.voice_status_lbl = tk.Label(v_inner, text="Status: Assistant is offline.", font=("Segoe UI", 10, "bold"),
                                         bg=self.t["card_bg"], fg=self.t["muted"])
        self.voice_status_lbl.pack(pady=10)

        tk.Label(v_inner, text="Text Command Backup (English Only):", font=("Segoe UI", 9, "bold"),
                 bg=self.t["card_bg"], fg=self.t["fg"]).pack(pady=(20, 5))
        
        cmd_box_frame = tk.Frame(v_inner, bg=self.t["card_bg"])
        cmd_box_frame.pack()

        self.cmd_entry = tk.Entry(cmd_box_frame, font=("Segoe UI", 10), width=35)
        self.cmd_entry.pack(side="left", padx=5)
        
        tk.Button(cmd_box_frame, text="Execute", command=lambda: self.process_voice_command(self.cmd_entry.get()),
                  bg=self.t["off_bg"], fg=self.t["fg"], font=("Segoe UI", 9, "bold"), padx=10, pady=2).pack(side="left", padx=5)

    def _build_blueprint_tab(self):
        f = self.tab_blueprint
        card = self._create_card(f, "HOUSE FLOOR PLAN & ROOM STATUS")
        card.pack(fill="both", expand=True, pady=10)
        self.house_canvas = tk.Canvas(card, bg=self.t["card_bg"], highlightthickness=0)
        self.house_canvas.pack(fill="both", expand=True, padx=12, pady=12)

    def _build_analytics_tab(self):
        f = self.tab_analytics
        card = self._create_card(f, "REAL-TIME ENERGY & POWER ANALYTICS")
        card.pack(fill="both", expand=True, pady=10)

        inner = tk.Frame(card, bg=self.t["card_bg"])
        inner.pack(fill="both", expand=True, padx=12, pady=12)
        inner.grid_columnconfigure((0, 1), weight=1)

        self.analytics_chart_canvas = tk.Canvas(inner, height=250, bg=self.t["bg"], highlightthickness=0)
        self.analytics_chart_canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        stats_frame = tk.Frame(inner, bg=self.t["card_bg"])
        stats_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.stat_labels = {}
        for lbl, val in [("Current Load", "0 W"), ("Today's Usage", "5.0 kWh"), ("Energy Saved", "24%"), ("AI Confidence", "95%")]:
            lbl_box = tk.Frame(stats_frame, bg=self.t["bg"], bd=1, relief="solid")
            lbl_box.pack(fill="x", pady=6, padx=6)
            tk.Label(lbl_box, text=lbl, font=("Segoe UI", 9, "bold"), bg=self.t["bg"], fg=self.t["muted"]).pack(anchor="w", padx=8, pady=(4, 0))
            v = tk.Label(lbl_box, text=val, font=("Segoe UI", 13, "bold"), bg=self.t["bg"], fg=self.t["accent"])
            v.pack(anchor="w", padx=8, pady=(0, 4))
            self.stat_labels[lbl] = v

    def _build_history_tab(self):
        f = self.tab_history
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(0, weight=1)
        hc = self._create_card(f, "TIMESTAMPED ROOM ACTIVITY HISTORY")
        hc.pack(fill="both", expand=True, pady=10)
        self.history_box = tk.Text(hc, height=12, font=("Consolas", 9), bg=self.t["bg"], fg=self.t["muted"], relief="flat", state="disabled", padx=8, pady=6)
        self.history_box.pack(fill="both", expand=True, padx=10, pady=6)

    def _create_card(self, parent, title):
        card = tk.Frame(parent, bg=self.t["card_bg"], bd=1, relief="solid")
        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg=self.t["card_bg"], fg=self.t["muted"], anchor="w").pack(fill="x", padx=10, pady=(6, 2))
        return card

    def _add_input(self, parent, r, c, text, widget):
        tk.Label(parent, text=text, font=("Segoe UI", 9), bg=self.t["card_bg"], fg=self.t["fg"]).grid(row=r, column=c, sticky="w", padx=(0, 4), pady=2)
        widget.grid(row=r, column=c + 1, sticky="w", padx=(0, 16), pady=2)

    def _draw_house_blueprint(self):
        c = self.house_canvas
        c.delete("all")

        w, h = 180, 180
        rooms_layout = [
            ("LIVING ROOM", self.rooms["living"], 40, 40),
            ("BEDROOM", self.rooms["bedroom"], 250, 40),
            ("KITCHEN", self.rooms["kitchen"], 460, 40),
            ("SECURITY ZONE", self.rooms["security"], 670, 40)
        ]

        for title, r_data, x, y in rooms_layout:
            active_items = [k.upper() for k, v in r_data.items() if v == "ON"]
            color = self.t["on_green_bg"] if active_items else self.t["off_bg"]
            if title == "SECURITY ZONE" and r_data.get("alarm") == "ON":
                color = self.t["alarm_red_bg"]

            c.create_rectangle(x, y, x + w, y + h, fill=color, outline=self.t["muted"], width=2)
            c.create_text(x + w//2, y + 30, text=title, font=("Segoe UI", 9, "bold"), fill=self.t["fg"])
            
            status_str = " | ".join(active_items) if active_items else "All OFF / Idle"
            c.create_text(x + w//2, y + 90, text=status_str, font=("Segoe UI", 8), fill=self.t["muted"], width=w-20)

    def _animate_loops(self):
        self._draw_house_blueprint()

        total_watts = 0
        self.target_bars = {"light": 0, "fan": 0, "ac": 0, "alarm": 0}

        for r_key, r_data in self.rooms.items():
            for app, state in r_data.items():
                if state == "ON":
                    if app == "light": total_watts += 20; self.target_bars["light"] += 20
                    elif app == "fan": total_watts += 75; self.target_bars["fan"] += 75
                    elif app == "ac": total_watts += 1450; self.target_bars["ac"] += 1450
                    elif app == "alarm": total_watts += 30; self.target_bars["alarm"] += 30
                    elif app == "exhaust": total_watts += 40

        cc = self.analytics_chart_canvas
        cc.delete("all")
        keys = ["light", "fan", "ac", "alarm"]
        labels = ["Light", "Fan", "AC", "Siren"]
        colors = ["#facc15", "#38bdf8", "#3b82f6", "#ef4444"]
        
        for k in self.target_bars:
            diff = self.target_bars[k] - self.current_bars[k]
            if abs(diff) > 2: self.current_bars[k] += diff * 0.2
            else: self.current_bars[k] = self.target_bars[k]

        x_start, bw, base_y = 60, 50, 200
        for i, k in enumerate(keys):
            x = x_start + i * (bw + 30)
            bh = (self.current_bars[k] / 1500.0) * 140
            cc.create_rectangle(x, base_y - bh, x + bw, base_y, fill=colors[i], outline="")
            cc.create_text(x + bw//2, base_y + 12, text=labels[i], font=("Segoe UI", 8, "bold"), fill=self.t["muted"])
            if self.current_bars[k] > 5:
                cc.create_text(x + bw//2, base_y - bh - 10, text=f"{int(self.current_bars[k])}W", font=("Segoe UI", 8), fill=self.t["fg"])

        self.stat_labels["Current Load"].config(text=f"{total_watts} W")
        self.stat_labels["Today's Usage"].config(text=f"{round(5.0 + (total_watts/1000)*1.5, 2)} kWh")

        self.root.after(100, self._animate_loops)

    def trigger_agent_rules(self):
        try: temp = float(self.temp_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid temperature.")
            return

        is_dark = (self.light_var.get() == "Dark")
        is_occupied = (self.occupied_var.get() == "Yes")
        is_smoke = (self.smoke_var.get() == "Yes")
        is_motion = (self.motion_var.get() == "Detected")
        mode = self.mode_var.get()

        ac_thresh = 30 if mode == "Energy Saving Mode" else 28

        if is_occupied and is_dark:
            self.rooms["living"]["light"] = "ON"
        else:
            self.rooms["living"]["light"] = "OFF"

        if is_occupied and temp > ac_thresh:
            self.rooms["bedroom"]["ac"] = "ON"
        else:
            self.rooms["bedroom"]["ac"] = "OFF"

        if is_occupied and 24 <= temp <= 28:
            self.rooms["bedroom"]["fan"] = "ON"
        else:
            self.rooms["bedroom"]["fan"] = "OFF"

        if is_smoke or (mode == "Away Mode" and is_motion):
            self.rooms["security"]["alarm"] = "ON"
        else:
            self.rooms["security"]["alarm"] = "OFF"

        speak_text("AI Rule engine executed successfully.")
        self.refresh_ui()

    def toggle_room_appliance(self, room_key, app_key):
        curr = self.rooms[room_key][app_key]
        new_state = "OFF" if curr == "ON" else "ON"
        self.rooms[room_key][app_key] = new_state
        
        speak_text(f"{self.rooms[room_key]['name']} {app_key} is now {new_state}")
        self.refresh_ui()

    def process_voice_command(self, cmd):
        cmd = cmd.lower().strip()
        self.voice_status_lbl.config(text=f"Status: Heard -> '{cmd}'", fg=self.t["accent"])
        
        target_room = None
        if "living" in cmd: target_room = "living"
        elif "bedroom" in cmd: target_room = "bedroom"
        elif "kitchen" in cmd: target_room = "kitchen"
        elif "security" in cmd or "alarm" in cmd: target_room = "security"

        if not target_room:
            if "bedroom" in cmd: target_room = "bedroom"
            elif "kitchen" in cmd: target_room = "kitchen"
            else: target_room = "living"

        state_val = "OFF" if "off" in cmd else "ON"

        if "ac" in cmd:
            if target_room in self.rooms and "ac" in self.rooms[target_room]:
                self.rooms[target_room]["ac"] = state_val
                speak_text(f"Air conditioner in {target_room} turned {state_val}")
        elif "fan" in cmd:
            if target_room in self.rooms and "fan" in self.rooms[target_room]:
                self.rooms[target_room]["fan"] = state_val
                speak_text(f"Fan in {target_room} turned {state_val}")
        elif "light" in cmd:
            if target_room in self.rooms and "light" in self.rooms[target_room]:
                self.rooms[target_room]["light"] = state_val
                speak_text(f"Light in {target_room} turned {state_val}")
        elif "exhaust" in cmd:
            if "exhaust" in self.rooms["kitchen"]:
                self.rooms["kitchen"]["exhaust"] = state_val
                speak_text(f"Kitchen exhaust turned {state_val}")
        elif "fire" in cmd or "hazard" in cmd:
            self._preset_fire()
            return
        elif "intruder" in cmd:
            self._preset_intruder()
            return
        else:
            speak_text("Command not recognized. Please speak in English.")
            return

        self.refresh_ui()

    def refresh_ui(self):
        for r_key, apps in self.room_tiles.items():
            for app_key, btn in apps.items():
                val = self.rooms[r_key][app_key]
                btn.config(text=f"{app_key.upper()}: {val}")
                if val == "ON":
                    btn.config(bg=self.t["on_green_bg"], fg=self.t["on_green"])
                else:
                    btn.config(bg=self.t["off_bg"], fg=self.t["off_fg"])

        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] Room States Updated Successfully.\n"
        self.history_box.config(state="normal")
        self.history_box.insert("1.0", entry)
        self.history_box.config(state="disabled")

    def toggle_auto_voice(self):
        if not SPEECH_AVAILABLE:
            messagebox.showwarning("Error", "SpeechRecognition module not found.")
            return
        self.is_auto_listening = not self.is_auto_listening
        if self.is_auto_listening:
            self.auto_voice_btn.config(text="🔴 English Voice Assistant: ON", bg="#22c55e")
            self.voice_status_lbl.config(text="Status: Listening for English commands...", fg=self.t["on_green"])
            speak_text("English voice assistant is now active.")
            self.start_background_listening()
        else:
            self.auto_voice_btn.config(text="🟢 English Voice Assistant: OFF", bg="#37474f")
            self.voice_status_lbl.config(text="Status: Assistant is offline.", fg=self.t["muted"])
            if self.stop_listening_callback:
                self.stop_listening_callback(wait_for_stop=False)

    def start_background_listening(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)

        def background_callback(recognizer, audio):
            if not self.is_auto_listening: return
            try:
                cmd = recognizer.recognize_google(audio, language="en-US")
                self.root.after(0, lambda: self.process_voice_command(cmd))
            except: pass

        self.stop_listening_callback = self.recognizer.listen_in_background(self.microphone, background_callback)

    def _preset_fire(self):
        self.rooms["security"]["alarm"] = "ON"
        speak_text("Warning! Fire hazard emergency detected.")
        self.refresh_ui()

    def _preset_intruder(self):
        self.rooms["security"]["alarm"] = "ON"
        speak_text("Security alert! Unauthorized intruder detected.")
        self.refresh_ui()

    def _preset_summer(self):
        self.rooms["living"]["ac"] = "ON"
        self.rooms["bedroom"]["ac"] = "ON"
        speak_text("Hot summer mode activated. Air conditioners turned on.")
        self.refresh_ui()

    def _preset_night(self):
        self.rooms["living"]["light"] = "ON"
        self.rooms["bedroom"]["light"] = "ON"
        speak_text("Night rest mode activated. Lights turned on.")
        self.refresh_ui()

    def toggle_sim(self):
        self.auto_sim = not self.auto_sim
        if self.auto_sim:
            self.sim_btn.config(text="Auto Sim: ON", bg="#22c55e", fg="#ffffff")
            self._sim_tick()
        else:
            self.sim_btn.config(text="Auto Simulation: OFF", bg=self.t["card_bg"], fg=self.t["fg"])

    def _sim_tick(self):
        if not self.auto_sim: return
        self.temp_var.set(str(random.choice([23, 27, 33, 38])))
        self.trigger_agent_rules()
        self.root.after(3500, self._sim_tick)

    def reset_system(self):
        self.auto_sim = False
        self.is_auto_listening = False
        self.sim_btn.config(text="Auto Simulation: OFF", bg=self.t["card_bg"], fg=self.t["fg"])
        for r_key in self.rooms:
            for app in self.rooms[r_key]:
                if app != "name": self.rooms[r_key][app] = "OFF"
        self.refresh_ui()
        speak_text("System reset complete.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeApp(root)
    root.mainloop()