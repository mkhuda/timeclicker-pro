import tkinter as tk
import pyautogui
import threading
from datetime import datetime, time as dt_time, timedelta
from pynput import keyboard # Untuk Global Hotkey

# Variabel global untuk overlay
overlay_window = None

# --- Fungsi Inti (Logika Clicker) ---

def check_click_time(target_time_obj):
    """Memeriksa waktu klik secara presisi (1ms)."""
    if not (overlay_window and overlay_window.winfo_exists()):
        return

    now = datetime.now().time()
    
    if now >= target_time_obj:
        pyautogui.click()
        status_label.config(text=f"Clicked at {now.strftime('%H:%M:%S.%f')[:-3]}")
        
        # Hancurkan jendela setelah klik
        if overlay_window and overlay_window.winfo_exists():
            start_button.config(state=tk.NORMAL)
            overlay_window.destroy()
        
        # Kembalikan jendela utama setelah 2 detik
        root.after(2000, root.deiconify)
    else:
        root.after(1, check_click_time, target_time_obj)

def update_visual_countdown(target_datetime):
    """Mengelola countdown VISUAL (JJ:MM:DD) setiap detik."""
    if not (overlay_window and overlay_window.winfo_exists()):
        return

    now = datetime.now()
    time_diff = target_datetime - now
    seconds_left = int(time_diff.total_seconds())

    if seconds_left >= 0:
        hours = seconds_left // 3600
        minutes = (seconds_left % 3600) // 60
        seconds = seconds_left % 60
        display_text = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        overlay_window.label.config(text=display_text)
        root.after(1000, update_visual_countdown, target_datetime)
    else:
        overlay_window.label.config(text="GO!")

def update_mouse_position():
    """Menggerakkan overlay mengikuti mouse (setiap 50ms)."""
    if overlay_window and overlay_window.winfo_exists():
        x = root.winfo_pointerx()
        y = root.winfo_pointery()
        overlay_window.geometry(f"+{x+20}+{y+20}")
        root.after(50, update_mouse_position)

# --- Fungsi Baru (Flow & Kontrol) ---

def validate_time_input(*args):
    """Membaca input dari Spinbox/Entry dan memvalidasi waktu."""
    try:
        h = int(hour_spinbox.get())
        m = int(minute_spinbox.get())
        s = int(second_spinbox.get())
        # ms = int(ms_entry.get())

        now = datetime.now()
        target_time = now.replace(hour=h, minute=m, second=s, microsecond=0)

        if target_time < now:
            start_button.config(state=tk.DISABLED)
            status_label.config(text="Error: Waktu target sudah lewat.")
        else:
            # Hanya aktifkan jika tidak sedang countdown
            if not (overlay_window and overlay_window.winfo_exists()):
                start_button.config(state=tk.NORMAL)
                status_label.config(text="Ready.")
    except (ValueError, tk.TclError):
        start_button.config(state=tk.DISABLED)
        status_label.config(text="Error: Input tidak valid.")

def start_click():
    """Fungsi utama yang dipanggil tombol 'Start'."""
    global overlay_window
    
    if overlay_window and overlay_window.winfo_exists():
        status_label.config(text="Error: Operasi sudah berjalan.")
        return
    
    try:
        h = int(hour_spinbox.get())
        m = int(minute_spinbox.get())
        s = int(second_spinbox.get())
        ms = int(ms_var.get())
        target_time_obj = dt_time(h, m, s, ms * 1000)
    except ValueError:
        status_label.config(text="Error: Format waktu salah.")
        return

    now = datetime.now()
    target_datetime = datetime.combine(now.date(), target_time_obj)
    
    if target_datetime < now:
        target_datetime += timedelta(days=1)
        
    time_diff = target_datetime - now

    overlay_window = tk.Toplevel(root)
    overlay_window.overrideredirect(True)
    overlay_window.attributes("-topmost", True)
    overlay_window.label = tk.Label(overlay_window, text="", 
                                   font=("Arial", 20, "bold"), 
                                   bg="black", fg="white", padx=10, pady=5)
    overlay_window.label.pack()
    start_button.config(state=tk.DISABLED)
    status_label.config(text="Countdown running...")
    update_mouse_position()
    check_click_time(target_time_obj)
    update_visual_countdown(target_datetime)

# --- (sisa fungsi on_start_click_enter, reset_operations, on_press, start_hotkey_listener tetap sama) ---

def on_start_click_enter(event):
    """Wrapper untuk memanggil start_click() dari tombol Enter."""
    start_click()

def reset_operations():
    """Menghentikan semua operasi dan mengembalikan GUI."""
    global overlay_window
    if overlay_window and overlay_window.winfo_exists():
        overlay_window.destroy()
        overlay_window = None
    
    root.deiconify() 
    start_button.config(state=tk.NORMAL)
    status_label.config(text="Ready. Operasi dihentikan.")

# --- Logika Global Hotkey (Rem Darurat) ---

def on_press(key):
    """Fungsi ini berjalan di thread terpisah, memantau penekanan tombol."""
    if key == keyboard.Key.esc:
        print("Tombol 'Esc' (Reset) terdeteksi!")
        root.after(0, reset_operations)

def start_hotkey_listener():
    """Memulai listener keyboard."""
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# --- GUI Utama ---

# 1. Konfigurasi Tema & Font Modern
BG_COLOR = "#2E2E2E"
FG_COLOR = "#F0F0F0"
ACCENT_COLOR = "#007ACC"
SPIN_BG = "#3C3C3C"
BTN_HOVER_COLOR = "#555555"

FONT_FAMILY = "Segoe UI"
FONT_NORMAL = (FONT_FAMILY, 12)
FONT_BOLD = (FONT_FAMILY, 12, "bold")
FONT_LARGE_BOLD = (FONT_FAMILY, 18, "bold")
FONT_SPIN_DISPLAY = (FONT_FAMILY, 24, "bold")

# --- Fungsi Helper untuk UI ---
def on_enter(e):
    e.widget['background'] = BTN_HOVER_COLOR

def on_leave_main(e):
    e.widget['background'] = SPIN_BG

# --- Inisialisasi GUI ---
root = tk.Tk()
root.title("TimeClicker Pro")
root.geometry("420x280")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

# --- Judul Aplikasi ---
title_label = tk.Label(root, text="Set Target Time", font=FONT_LARGE_BOLD, bg=BG_COLOR, fg=FG_COLOR)
title_label.pack(pady=(20, 15))

# --- Frame untuk Input Waktu ---
time_frame = tk.Frame(root, bg=BG_COLOR)
time_frame.pack(pady=10, padx=20)

now = datetime.now()

# --- Widget Input dengan Gaya Modern (Spinbox Default) ---
spinbox_style = {
    "from_": 0, "width": 3, "format": "%02.0f",
    "font": FONT_SPIN_DISPLAY,
    "bg": SPIN_BG, "fg": FG_COLOR,
    "buttonbackground": SPIN_BG, # Warna tombol panah
    "readonlybackground": SPIN_BG,
    "highlightthickness": 0,
    "borderwidth": 0,
    "command": validate_time_input
}

hour_spinbox = tk.Spinbox(time_frame, to=23, **spinbox_style)
hour_spinbox.delete(0, "end")
hour_spinbox.insert(0, f"{now.hour:02}")
hour_spinbox.pack(side=tk.LEFT, padx=(0, 5))

tk.Label(time_frame, text=":", font=FONT_SPIN_DISPLAY, bg=BG_COLOR, fg=ACCENT_COLOR).pack(side=tk.LEFT)

minute_spinbox = tk.Spinbox(time_frame, to=59, **spinbox_style)
minute_spinbox.delete(0, "end")
minute_spinbox.insert(0, f"{now.minute:02}")
minute_spinbox.pack(side=tk.LEFT, padx=5)

tk.Label(time_frame, text=":", font=FONT_SPIN_DISPLAY, bg=BG_COLOR, fg=ACCENT_COLOR).pack(side=tk.LEFT)

second_spinbox = tk.Spinbox(time_frame, to=59, **spinbox_style)
second_spinbox.delete(0, "end")
second_spinbox.insert(0, f"{now.second:02}")
second_spinbox.pack(side=tk.LEFT, padx=5)

# --- Frame untuk Milidetik ---
ms_frame = tk.Frame(root, bg=BG_COLOR)
ms_frame.pack(pady=(0, 20))
tk.Label(ms_frame, text="Milliseconds:", font=FONT_NORMAL, bg=BG_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=5)
ms_var = tk.StringVar(value="000")
ms_entry = tk.Entry(ms_frame, width=5, textvariable=ms_var, font=FONT_NORMAL,
                    bg=SPIN_BG, fg=FG_COLOR, insertbackground=FG_COLOR,
                    highlightthickness=0, borderwidth=0, justify='center')
ms_entry.pack(side=tk.LEFT)
ms_var.trace_add("write", validate_time_input)

# --- Tombol & Status ---
button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=10)

button_style = { "font": FONT_BOLD, "bg": SPIN_BG, "fg": ACCENT_COLOR,
                 "activebackground": ACCENT_COLOR, "activeforeground": FG_COLOR,
                 "relief": tk.FLAT, "borderwidth": 0, "highlightthickness": 0, "padx": 20, "pady": 8 }

start_button = tk.Button(button_frame, text="START", **button_style, command=start_click)
start_button.pack(side=tk.LEFT, padx=10)

reset_button = tk.Button(button_frame, text="RESET", **button_style, command=reset_operations)
reset_button.pack(side=tk.LEFT, padx=10)

for btn in [start_button, reset_button]:
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave_main)

status_label = tk.Label(root, text="Ready.", font=FONT_NORMAL, bg=ACCENT_COLOR, fg=BG_COLOR, padx=5)
status_label.pack(side=tk.BOTTOM, fill=tk.X, ipady=5)

root.after(100, validate_time_input)

hotkey_thread = threading.Thread(target=start_hotkey_listener, daemon=True)
hotkey_thread.start()

root.mainloop()