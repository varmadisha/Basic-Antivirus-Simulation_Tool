import os
import hashlib
import shutil
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import webbrowser
import threading
from datetime import datetime

# SOUND
try:
    import winsound
    def play_alert():
        winsound.Beep(1000, 300)
except:
    def play_alert():
        pass

# WATCHDOG
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# CONFIG
SCAN_PATH = ""
IS_FILE_MODE = False
QUARANTINE_FOLDER = "quarantine"
REAL_TIME = False
observer = None

if not os.path.exists(QUARANTINE_FOLDER):
    os.makedirs(QUARANTINE_FOLDER)

malware_hashes = {
    "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824": "Trojan Sample"
}

HIGH_RISK_EXT = [".exe", ".bat", ".scr", ".dll", ".cmd", ".vbs"]

# STATS
total_files = 0
threat_count = 0
suspicious_count = 0

# HASH
def get_hash(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except:
        return None

# STATUS
def get_status_text():
    if threat_count > 0:
        return "🔴 Infected", "red"
    elif suspicious_count > 0:
        return "🟡 At Risk", "orange"
    else:
        return "🟢 Protected", "lime"

def update_stats(scanned):
    status_text, color = get_status_text()
    stats_label.config(
        text=f"Scanned: {scanned}/{total_files} | Threats: {threat_count} | Suspicious: {suspicious_count} | Status: {status_text}",
        fg=color
    )

# LOG
def log(msg, level="INFO"):
    colors = {"INFO":"#00ffe0","SAFE":"lime","WARN":"orange","ALERT":"red"}
    time_now = datetime.now().strftime("%H:%M:%S")
    output.insert(tk.END, f"[{time_now}] [{level}] {msg}\n", level)
    output.tag_config(level, foreground=colors.get(level,"white"))
    output.see(tk.END)

# ANALYSIS
def analyze_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return "HIGH RISK" if ext in HIGH_RISK_EXT else "NORMAL"

# ALERT
def show_alert(title, msg):
    play_alert()
    messagebox.showwarning(title, msg)

# SCAN FILE
def scan_file(file_path):
    global threat_count, suspicious_count

    if not os.path.exists(file_path):
        return

    name = os.path.basename(file_path)
    log(f"Scanning: {name}")

    file_hash = get_hash(file_path)
    risk = analyze_file(file_path)

    if file_hash in malware_hashes:
        threat_count += 1
        log(f"🚨 Malware Detected: {name}", "ALERT")
        try:
            new_name = f"{int(datetime.now().timestamp())}_{name}"
            shutil.move(file_path, os.path.join(QUARANTINE_FOLDER, new_name))
            show_alert("Malware", f"{name} blocked!")
        except:
            log("Quarantine Failed", "ALERT")

    elif risk == "HIGH RISK":
        suspicious_count += 1
        log(f"⚠ Suspicious File: {name}", "WARN")
        show_alert("Warning", f"{name} suspicious!")

    else:
        log(f"✔ Safe File: {name}", "SAFE")

# WATCHDOG
class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            scan_file(event.src_path)
            update_stats(total_files)

# REAL TIME
def toggle_real_time():
    global REAL_TIME, observer

    if not SCAN_PATH:
        messagebox.showwarning("Warning", "Select path first")
        return

    REAL_TIME = not REAL_TIME

    if REAL_TIME:
        log("Real-Time ON", "SAFE")
        watch = os.path.dirname(SCAN_PATH) if os.path.isfile(SCAN_PATH) else SCAN_PATH
        observer = Observer()
        observer.schedule(Handler(), watch, recursive=True)
        observer.start()
    else:
        log("Real-Time OFF", "ALERT")
        if observer:
            observer.stop()
            observer.join()

# SCAN
def start_scan():
    threading.Thread(target=scan).start()

def scan():
    global total_files, threat_count, suspicious_count

    output.delete(1.0, tk.END)
    total_files = threat_count = suspicious_count = 0

    files = []
    if os.path.isfile(SCAN_PATH):
        files.append(SCAN_PATH)
    else:
        for r, d, f in os.walk(SCAN_PATH):
            for file in f:
                files.append(os.path.join(r, file))

    total_files = len(files)
    progress["maximum"] = total_files

    for i, file in enumerate(files):
        scan_file(file)
        progress["value"] = i + 1
        update_stats(i + 1)
        root.update_idletasks()

    messagebox.showinfo("Scan Completed",
                        f"Total: {total_files}\nThreats: {threat_count}\nSuspicious: {suspicious_count}")

# SELECT
def select_file():
    global SCAN_PATH
    SCAN_PATH = filedialog.askopenfilename()
    path_label.config(text=SCAN_PATH)

def select_folder():
    global SCAN_PATH
    SCAN_PATH = filedialog.askdirectory()
    path_label.config(text=SCAN_PATH)

# FOOTER LINKS
def open_email(e): webbrowser.open("mailto:dishavarma910@gmail.com")
def open_linkedin(e): webbrowser.open("https://github.com/varmadisha")
def open_github(e): webbrowser.open("linkedin.com/in/disha-varma-28a771310")

# UI
root = tk.Tk()
root.title("CyberShield Pro")
root.geometry("1100x700")
root.configure(bg="#0b1220")

main = tk.Frame(root, bg="#0b1220")
main.pack(fill="both", expand=True)

tk.Label(main, text="🛡️ CyberShield Pro Antivirus",
         font=("Segoe UI", 28, "bold"),
         bg="#0b1220", fg="#00ffe0").pack(pady=10)

btn_frame = tk.Frame(main, bg="#0b1220")
btn_frame.pack()

def create_btn(text, cmd):
    return tk.Button(btn_frame, text=text, command=cmd,
                     font=("Segoe UI", 13, "bold"),
                     bg="#1e293b", fg="white",
                     activebackground="#334155",
                     relief="raised", bd=4,
                     padx=15, pady=8)

create_btn("Select File", select_file).grid(row=0, column=0, padx=8)
create_btn("Select Folder", select_folder).grid(row=0, column=1, padx=8)
create_btn("Start Scan", start_scan).grid(row=0, column=2, padx=8)
create_btn("Real-Time ON/OFF", toggle_real_time).grid(row=0, column=3, padx=8)

path_label = tk.Label(main, text="No path selected",
                      bg="#0b1220", fg="gray",
                      font=("Segoe UI", 11))
path_label.pack()

progress = ttk.Progressbar(main, length=650)
progress.pack(pady=10)

stats_label = tk.Label(main,
    text="Scanned: 0 | Threats: 0 | Suspicious: 0 | Status: 🟢 Protected",
    bg="#0b1220", fg="lime",
    font=("Segoe UI", 13, "bold"))
stats_label.pack()

output = scrolledtext.ScrolledText(main,
                                   bg="#020617", fg="#00ffe0",
                                   font=("Consolas", 11),
                                   height=15)
output.pack(fill="both", expand=True, padx=10, pady=10)

# FOOTER
footer = tk.Frame(root, bg="#020617")
footer.pack(fill="x", side="bottom")

tk.Label(footer, text="👩‍💻 Disha Varma",
         fg="#00ffe0", bg="#020617",
         font=("Segoe UI", 14, "bold")).pack()

link_frame = tk.Frame(footer, bg="#020617")
link_frame.pack()

email = tk.Label(link_frame, text="📧 dishavarma910@gmail.com", fg="white",
                 bg="#020617", cursor="hand2",
                 font=("Segoe UI", 12))
linkedin = tk.Label(link_frame, text="🔗 LinkedIn", fg="white",
                    bg="#020617", cursor="hand2",
                    font=("Segoe UI", 12))
github = tk.Label(link_frame, text="💻 GitHub", fg="white",
                  bg="#020617", cursor="hand2",
                  font=("Segoe UI", 12))

email.grid(row=0, column=0, padx=12)
linkedin.grid(row=0, column=1, padx=12)
github.grid(row=0, column=2, padx=12)

email.bind("<Button-1>", open_email)
linkedin.bind("<Button-1>", open_linkedin)
github.bind("<Button-1>", open_github)

root.mainloop()