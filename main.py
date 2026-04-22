import time
import tkinter as tk
from tkinter import ttk
from pynput import mouse, keyboard
from threading import Thread
import winsound
from plyer import notification

# 🎨 GEIST STYLE
BG = "#0A0A0A"
CARD = "#111111"
TEXT = "#EAEAEA"
SUBTEXT = "#888888"

SUCCESS = "#22c55e"
WARNING = "#f59e0b"
DANGER = "#ef4444"


last_activity_time = time.time()
start_time = time.time()
active_time = 0

WARNING_TIME = 35
INACTIVE_TIME = 60

alert_triggered = False
last_beep_time = 0
BEEP_INTERVAL = 2  # segundos


def on_input(*args):
    global last_activity_time
    last_activity_time = time.time()


def monitor(percent_label, status_label, idle_label, progress, dot, root):
    global active_time, alert_triggered, last_beep_time

    while True:
        now = time.time()
        idle_time = now - last_activity_time
        total_time = now - start_time

        
        if idle_time < 1:
            active_time += 1

        
        activity_percent = int((active_time / total_time) * 100) if total_time > 0 else 0
        activity_percent = max(0, min(100, activity_percent))

        
        if idle_time < WARNING_TIME:
            estado = "Active"
            color = SUCCESS
            alert_triggered = False

        elif idle_time < INACTIVE_TIME:
            estado = "Dropping"
            color = WARNING

        else:
            estado = "Idle"
            color = DANGER

            
            if now - last_beep_time > BEEP_INTERVAL:
                winsound.Beep(1000, 400)
                last_beep_time = now

            
            if not alert_triggered:
                try:
                    notification.notify(
                        title="Inactividad detectada",
                        message="Llevás más de 1 minuto sin actividad",
                        timeout=3
                    )
                except:
                    pass

                alert_triggered = True

        idle_seconds = int(idle_time)

        def update_ui():
            percent_label.config(text=f"{activity_percent}%")
            status_label.config(text=estado)
            idle_label.config(text=f"{idle_seconds}s idle")

            progress['value'] = activity_percent
            dot.config(bg=color)

        root.after(0, update_ui)
        time.sleep(1)



root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.configure(bg=BG)
root.geometry("200x130+300+200")
root.attributes("-alpha", 0.95)

container = tk.Frame(root, bg=CARD)
container.pack(fill="both", expand=True, padx=8, pady=8)


def close_app():
    root.destroy()

close_btn = tk.Label(
    container,
    text="✕",
    fg=SUBTEXT,
    bg=CARD,
    font=("Segoe UI", 10)
)
close_btn.place(relx=1.0, x=-10, y=5, anchor="ne")
close_btn.bind("<Button-1>", lambda e: close_app())


dot = tk.Frame(container, bg=SUCCESS, width=8, height=8)
dot.place(x=8, y=8)


percent_label = tk.Label(
    container,
    text="0%",
    font=("Segoe UI", 22, "bold"),
    fg=TEXT,
    bg=CARD
)
percent_label.pack(pady=(12, 0))

status_label = tk.Label(
    container,
    text="Active",
    font=("Segoe UI", 9),
    fg=SUBTEXT,
    bg=CARD
)
status_label.pack()


idle_label = tk.Label(
    container,
    text="0s idle",
    font=("Segoe UI", 8),
    fg=SUBTEXT,
    bg=CARD
)
idle_label.pack(pady=(0, 5))


style = ttk.Style()
style.theme_use('default')
style.configure(
    "TProgressbar",
    troughcolor=CARD,
    background=SUCCESS,
    thickness=4
)

progress = ttk.Progressbar(
    container,
    orient="horizontal",
    length=150,
    mode="determinate",
    style="TProgressbar"
)
progress.pack(pady=(0, 8))


def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

container.bind("<Button-1>", start_move)
container.bind("<B1-Motion>", do_move)


mouse.Listener(on_move=on_input, on_click=on_input, on_scroll=on_input).start()
keyboard.Listener(on_press=on_input).start()


Thread(
    target=monitor,
    args=(percent_label, status_label, idle_label, progress, dot, root),
    daemon=True
).start()

root.mainloop()