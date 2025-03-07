import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime, timedelta

# File path
FILE_PATH = "sd1.txt"
IMAGE_PATH = "IsroImg.png"

def read_file():
    """ Reads the file and separates ongoing and upcoming passes based on the current time """
    try:
        with open(FILE_PATH, "r") as file:
            lines = file.readlines()
        
        now = datetime.now()
        ongoing_passes = []
        upcoming_passes = []

        for line in lines:
            parts = line.strip().split()
            if len(parts) < 7:
                continue  # Skip invalid lines

            # Parse date and time
            year, month, day, sd, code, start_time, end_time, *_ = parts
            try:
                pass_start = datetime(int(year), int(month), int(day), 
                                      int(start_time[:2]), int(start_time[3:5]), int(start_time[6:8]))
                pass_end = datetime(int(year), int(month), int(day), 
                                    int(end_time[:2]), int(end_time[3:5]), int(end_time[6:8]))
            except ValueError:
                continue  # Skip invalid date entries

            formatted_date = f"{day}-{month}-{year}"  # Merging date

            # Categorize passes
            if pass_start <= now <= pass_end:
                ongoing_passes.append((formatted_date, sd, code, start_time, end_time))  # Ongoing
            elif pass_start > now:
                upcoming_passes.append((formatted_date, sd, code, start_time, end_time, pass_start))  # Upcoming

        # Sort by time and return
        upcoming_passes = sorted(upcoming_passes, key=lambda x: x[5])[:6]
        return ongoing_passes, upcoming_passes
    
    except FileNotFoundError:
        return [], []

def update_display():
    """ Updates the tables and current time label """
    now = datetime.now()
    current_time_label.config(text=f"{now.strftime('%H:%M:%S')}")
    current_date_label.config(text=f"{now.strftime('%A, %d %B %Y')}")  # Full date format

    # Clear previous data
    for row in ongoing_tree.get_children():
        ongoing_tree.delete(row)
    for row in upcoming_tree.get_children():
        upcoming_tree.delete(row)

    # Fetch data
    ongoing, upcoming = read_file()

    # Insert into tables
    for item in ongoing:
        ongoing_tree.insert("", "end", values=item[:5])  # Display first 5 columns
    for item in upcoming:
        upcoming_tree.insert("", "end", values=item[:5])  # Display first 5 columns

    # Update the next pass timer
    update_next_pass_timer(upcoming)

    root.after(1000, update_display)  # Refresh every second

def update_next_pass_timer(upcoming):
    """ Updates the countdown timer for the next upcoming pass """
    now = datetime.now()
    if upcoming:
        next_pass_time = upcoming[0][5]  # Extract datetime object
        time_diff = next_pass_time - now

        if time_diff.total_seconds() > 0:
            hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            countdown_label.config(text=f"Next Pass in: {hours:02d}:{minutes:02d}:{seconds:02d}", fg="lime")
        else:
            countdown_label.config(text="Next Pass in: Starting Now!", fg="red")
    else:
        countdown_label.config(text="No Upcoming Passes", fg="yellow")

# Tkinter Window
root = tk.Tk()
root.title("Satellite Pass Tracker")
root.geometry("630x500")
root.configure(bg="#1e1e1e")  # Dark Theme

# --- Top Frame (Date, Time on Left, Image on Right) ---
top_frame = tk.Frame(root, bg="#1e1e1e")
top_frame.pack(fill="x", pady=10)

# Current Date Label (Stylish)
current_date_label = tk.Label(top_frame, text="", font=("Arial", 14, "bold"), fg="lightblue", bg="#1e1e1e")
current_date_label.pack(side="left", padx=20)

# Current Time Label (Big and Bold)
current_time_label = tk.Label(top_frame, text="", font=("Arial", 18, "bold"), fg="cyan", bg="#1e1e1e")
current_time_label.pack(side="left", padx=20)

# Load and Display Image (Right Side)
try:
    img = Image.open(IMAGE_PATH)
    img = img.resize((160, 100))  # Resize for display
    img = ImageTk.PhotoImage(img)

    img_label = tk.Label(top_frame, image=img, bg="#1e1e1e")
    img_label.pack(side="right", padx=20)
except Exception:
    img_label = tk.Label(top_frame, text="Image Not Found", font=("Arial", 12, "bold"), fg="red", bg="#1e1e1e")
    img_label.pack(side="right", padx=20)

# --- Ongoing Passes Section ---
tk.Label(root, text="🔴 Ongoing Passes", font=("Arial", 12, "bold"), fg="red", bg="#1e1e1e").pack()
frame1 = tk.Frame(root, bg="#1e1e1e")
frame1.pack(pady=5)

ongoing_columns = ("Date", "SD", "Code", "Start Time", "End Time")
ongoing_tree = ttk.Treeview(frame1, columns=ongoing_columns, show="headings", height=3, style="Treeview")

for col in ongoing_columns:
    ongoing_tree.heading(col, text=col, anchor="center")
    ongoing_tree.column(col, width=120, anchor="center")

ongoing_tree.pack()

# --- Upcoming Passes Section ---
tk.Label(root, text="🟢 Upcoming Passes", font=("Arial", 12, "bold"), fg="green", bg="#1e1e1e").pack()
frame2 = tk.Frame(root, bg="#1e1e1e")
frame2.pack(pady=5)

upcoming_columns = ("Date", "SD", "Code", "Start Time", "End Time")
upcoming_tree = ttk.Treeview(frame2, columns=upcoming_columns, show="headings", height=6, style="Treeview")

for col in upcoming_columns:
    upcoming_tree.heading(col, text=col, anchor="center")
    upcoming_tree.column(col, width=120, anchor="center")

upcoming_tree.pack()

# --- Countdown Timer at the Bottom ---
countdown_label = tk.Label(root, text="Next Pass in: --:--:--", font=("Arial", 14, "bold"), fg="yellow", bg="#1e1e1e")
countdown_label.pack(pady=10)

# Start the UI update loop
update_display()

root.mainloop()

