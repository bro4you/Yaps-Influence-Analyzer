import requests
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Function to get Yaps score
def get_yaps_score(username):
    url = f"https://api.kaito.ai/api/v1/yaps?username={username}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None

# Function to analyze influence
def analyze_influence(yaps_data):
    if yaps_data is None:
        return "Error: Unable to retrieve data"
    yaps_all = yaps_data.get("yaps_all", 0)
    yaps_7d = yaps_data.get("yaps_l7d", 0)
    if yaps_all > 1000 and yaps_7d > 100:
        return "High Influence"
    elif yaps_all > 500:
        return "Medium Influence"
    else:
        return "Low Influence"

# Function to clear chart frame
def clear_chart_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

# Function to display influence chart
def display_chart(frame, yaps_data):
    clear_chart_frame(frame)
    if not yaps_data:
        return
    
    fig, ax = plt.subplots(figsize=(4, 3))
    values = [yaps_data.get("yaps_all", 0), yaps_data.get("yaps_l7d", 0)]
    labels = ["Total Yaps", "Yaps Last 7 Days"]
    colors = ["#4CAF50", "#2196F3"]
    
    bars = ax.bar(labels, values, color=colors)
    ax.set_title(f"Stats for {yaps_data.get('username', 'user')}")
    ax.set_facecolor("#f9f9f9")
    fig.patch.set_facecolor("#f9f9f9")
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                f"{height:.1f}", ha='center', va='bottom', fontsize=9)
    
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

# Function to clear results
def clear_results():
    result_text.set("")
    influence_label.config(text="")
    clear_chart_frame(chart_frame)

# Function to clear comparison results
def clear_compare_results():
    compare_result_text.set("")
    clear_chart_frame(compare_chart_frame)

# Function to check a single user
def check_user():
    username = entry_user.get().strip()
    if not username:
        messagebox.showwarning("Warning", "Please enter a username!")
        return
    
    clear_results()
    
    loading_label = tk.Label(result_card, text="Loading data...", font=("Arial", 11), bg="white")
    loading_label.pack(pady=10)
    root.update()
    
    yaps_data = get_yaps_score(username)
    
    loading_label.destroy()
    
    if yaps_data:
        influence_level = analyze_influence(yaps_data)
        influence_color = "#4CAF50" if influence_level == "High Influence" else \
                         "#FFC107" if influence_level == "Medium Influence" else "#F44336"
        
        result = (f"User: {yaps_data['username']}\n"
                 f"Total Yaps: {yaps_data['yaps_all']:.2f}\n"
                 f"Yaps Last 7 Days: {yaps_data['yaps_l7d']:.2f}\n"
                 f"Influence Level: {influence_level}")
        result_text.set(result)
        
        influence_label.config(text=influence_level, fg=influence_color)
        
        display_chart(chart_frame, yaps_data)
        
        copy_button.pack(pady=10, padx=10)
    else:
        result_text.set("Unable to retrieve data.\nCheck username or internet connection.")
        influence_label.config(text="No Data", fg="#999999")

# Function to compare two users
def compare_users():
    user1 = entry_user1.get().strip()
    user2 = entry_user2.get().strip()
    if not user1 or not user2:
        messagebox.showwarning("Warning", "Please enter both usernames!")
        return
    
    clear_compare_results()
    
    loading_label = tk.Label(compare_result_card, text="Loading data...", font=("Arial", 11), bg="white")
    loading_label.pack(pady=10)
    root.update()
    
    yaps_data1 = get_yaps_score(user1)
    yaps_data2 = get_yaps_score(user2)
    
    loading_label.destroy()
    
    if yaps_data1 and yaps_data2:
        winner = user1 if yaps_data1['yaps_all'] > yaps_data2['yaps_all'] else user2
        result = (f"{user1}: {yaps_data1['yaps_all']:.2f} Yaps (7 days: {yaps_data1['yaps_l7d']:.2f})\n"
                  f"{user2}: {yaps_data2['yaps_all']:.2f} Yaps (7 days: {yaps_data2['yaps_l7d']:.2f})\n"
                  f"Comparison: {winner} has more influence.")
        compare_result_text.set(result)
        
        fig, ax = plt.subplots(figsize=(4, 3))
        
        labels = ['Total Yaps', 'Yaps Last 7 Days']
        user1_data = [yaps_data1['yaps_all'], yaps_data1['yaps_l7d']]
        user2_data = [yaps_data2['yaps_all'], yaps_data2['yaps_l7d']]
        
        x = range(len(labels))
        width = 0.35
        
        bars1 = ax.bar([i - width/2 for i in x], user1_data, width, label=user1, color='#4CAF50')
        bars2 = ax.bar([i + width/2 for i in x], user2_data, width, label=user2, color='#2196F3')
        
        ax.set_title('User Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        ax.set_facecolor("#f9f9f9")
        fig.patch.set_facecolor("#f9f9f9")
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                        f"{height:.1f}", ha='center', va='bottom', fontsize=8)
        
        canvas = FigureCanvasTkAgg(fig, master=compare_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)
        
        compare_copy_button.pack(pady=10, padx=10)
    elif yaps_data1:
        compare_result_text.set(f"Data only for {user1}: {yaps_data1['yaps_all']:.2f} Yaps.")
    elif yaps_data2:
        compare_result_text.set(f"Data only for {user2}: {yaps_data2['yaps_all']:.2f} Yaps.")
    else:
        compare_result_text.set("Unable to retrieve data for both users.")

# Functions for copy/paste
def copy_text(widget):
    try:
        widget.event_generate("<<Copy>>")
    except tk.TclError:
        pass

def paste_text(widget):
    try:
        widget.event_generate("<<Paste>>")
    except tk.TclError:
        pass

def setup_copy_paste(entry_widget):
    # Bindings for Windows/Linux
    entry_widget.bind("<Control-c>", lambda event: copy_text(entry_widget))
    entry_widget.bind("<Control-v>", lambda event: paste_text(entry_widget))
    # Bindings for Mac
    entry_widget.bind("<Command-c>", lambda event: copy_text(entry_widget))
    entry_widget.bind("<Command-v>", lambda event: paste_text(entry_widget))
    # Context menu
    add_context_menu(entry_widget)

def add_context_menu(widget):
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Copy", command=lambda: copy_text(widget))
    menu.add_command(label="Paste", command=lambda: paste_text(widget))
    
    def show_menu(event):
        menu.post(event.x_root, event.y_root)
    
    widget.bind("<Button-3>", show_menu)  # Windows/Linux
    widget.bind("<Button-2>", show_menu)  # Mac

# Main window setup
root = tk.Tk()
root.title("Yaps Influence Analyzer")
root.geometry("600x650")
root.configure(bg="#f0f0f0")

# Styling
style = ttk.Style()
style.theme_use('clam')
style.configure("TFrame", background="#f9f9f9")
style.configure("TNotebook", background="#f0f0f0")
style.configure("TNotebook.Tab", background="#e0e0e0", padding=[10, 5], font=('Arial', 9))
style.map("TNotebook.Tab", background=[("selected", "#f9f9f9")])
style.configure("TButton", background="#4CAF50", foreground="white", font=('Arial', 10, 'bold'), padding=5)

# Header
header_frame = tk.Frame(root, bg="#2196F3", height=80)
header_frame.pack(fill=tk.X)

tk.Label(header_frame, text="Yaps Influence Analyzer", font=("Arial", 18, "bold"), 
        fg="white", bg="#2196F3").pack(pady=20)

# Load logo
try:
    logo_image = Image.open("yaps_logo.png")
    logo_image = logo_image.resize((60, 60), Image.Resampling.LANCZOS)
    logo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(header_frame, image=logo, bg="#2196F3")
    logo_label.place(x=20, y=10)
except Exception as e:
    print(f"Logo not found: {e}")

# Notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(pady=10, fill="both", expand=True, padx=15)

# Tab 1: User Check
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="User Check")

form_frame1 = ttk.Frame(tab1)
form_frame1.pack(pady=10, padx=20, fill="x")

ttk.Label(form_frame1, text="Enter X Username:", font=("Arial", 12)).pack(pady=5, anchor="w")
entry_user = ttk.Entry(form_frame1, width=30, font=("Arial", 11))
entry_user.pack(pady=5, fill="x")
setup_copy_paste(entry_user)

button_frame1 = ttk.Frame(form_frame1)
button_frame1.pack(pady=10, fill="x")
check_button = ttk.Button(button_frame1, text="Check", command=check_user, style="TButton")
check_button.pack(side="left", padx=5)
clear_button = ttk.Button(button_frame1, text="Clear", command=clear_results)
clear_button.pack(side="left", padx=5)

result_frame = ttk.Frame(tab1)
result_frame.pack(pady=10, padx=20, fill="both", expand=True)

result_card = tk.Frame(result_frame, bg="white", bd=1, relief="solid")
result_card.pack(pady=10, padx=10, fill="both")

result_text = tk.StringVar()
result_label = ttk.Label(result_card, textvariable=result_text, wraplength=500, justify="left", 
                        font=("Arial", 11), background="white")
result_label.pack(pady=10, padx=10, anchor="w")

influence_label = tk.Label(result_card, text="", font=("Arial", 14, "bold"), bg="white")
influence_label.pack(pady=5)

chart_frame = tk.Frame(result_card, bg="white")
chart_frame.pack(pady=10, padx=10, fill="both", expand=True)

def copy_results():
    root.clipboard_clear()
    root.clipboard_append(result_text.get())
    messagebox.showinfo("Info", "Results copied to clipboard")

copy_button = ttk.Button(result_card, text="Copy Results", command=copy_results)

# Tab 2: User Comparison
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="User Comparison")

form_frame2 = ttk.Frame(tab2)
form_frame2.pack(pady=10, padx=20, fill="x")

ttk.Label(form_frame2, text="User 1:", font=("Arial", 12)).pack(pady=5, anchor="w")
entry_user1 = ttk.Entry(form_frame2, width=30, font=("Arial", 11))
entry_user1.pack(pady=5, fill="x")
setup_copy_paste(entry_user1)

ttk.Label(form_frame2, text="User 2:", font=("Arial", 12)).pack(pady=5, anchor="w")
entry_user2 = ttk.Entry(form_frame2, width=30, font=("Arial", 11))
entry_user2.pack(pady=5, fill="x")
setup_copy_paste(entry_user2)

button_frame2 = ttk.Frame(form_frame2)
button_frame2.pack(pady=10, fill="x")
compare_button = ttk.Button(button_frame2, text="Compare", command=compare_users, style="TButton")
compare_button.pack(side="left", padx=5)
clear_compare_button = ttk.Button(button_frame2, text="Clear", command=clear_compare_results)
clear_compare_button.pack(side="left", padx=5)

compare_result_frame = ttk.Frame(tab2)
compare_result_frame.pack(pady=10, padx=20, fill="both", expand=True)

compare_result_card = tk.Frame(compare_result_frame, bg="white", bd=1, relief="solid")
compare_result_card.pack(pady=10, padx=10, fill="both")

compare_result_text = tk.StringVar()
compare_result_label = ttk.Label(compare_result_card, textvariable=compare_result_text, 
                                wraplength=500, justify="left", font=("Arial", 11), background="white")
compare_result_label.pack(pady=10, padx=10, anchor="w")

compare_chart_frame = tk.Frame(compare_result_card, bg="white")
compare_chart_frame.pack(pady=10, padx=10, fill="both", expand=True)

def copy_compare_results():
    root.clipboard_clear()
    root.clipboard_append(compare_result_text.get())
    messagebox.showinfo("Info", "Comparison results copied to clipboard")

compare_copy_button = ttk.Button(compare_result_card, text="Copy Results", command=copy_compare_results)

# Tab switch handler
def on_tab_changed(event):
    tab_id = notebook.index(notebook.select())
    if tab_id == 0:
        clear_results()
    else:
        clear_compare_results()

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

# Footer
footer_frame = tk.Frame(root, bg="#e0e0e0", height=30)
footer_frame.pack(side="bottom", fill="x")
tk.Label(footer_frame, text="© 2025 Yaps Influence Analyzer", font=("Arial", 8), 
        fg="#666", bg="#e0e0e0").pack(pady=5)

# Run the application
root.mainloop()