import tkinter as tk
from tkinter import messagebox
import functions 
import webbrowser

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HRMS Face Recognition")
        self.root.geometry("500x600")
        self.root.configure(bg="#1e272e")

        # Header with Logo/Title
        header = tk.Frame(self.root, bg="#05c46b", height=100)
        header.pack(fill="x")
        tk.Label(header, text="SMART ATTENDANCE", font=("Impact", 24), fg="white", bg="#05c46b").pack(pady=20)

        # Buttons Container
        content = tk.Frame(self.root, bg="#1e272e")
        content.pack(expand=True)

        self.add_button(content, "1. REGISTER FACE", functions.generate_dataset)
        self.add_button(content, "2. TRAIN MODELS", functions.train_classifier)
        self.add_button(content, "3. START CAMERA", functions.start_attendance, is_main=True)
        self.add_button(content, "4. VIEW WEB FORM", lambda: webbrowser.open("http://127.0.0.1:5000"), is_web=True)

    def add_button(self, parent, text, command, is_main=False, is_web=False):
        color = "#05c46b" if is_main else "#3c6382"
        if is_web: color = "#f39c12"
        
        btn = tk.Button(parent, text=text, command=command, width=30, height=2,
                        font=("Arial", 10, "bold"), fg="white", bg=color, 
                        cursor="hand2", relief="flat", activebackground="#2ecc71")
        btn.pack(pady=12)

if __name__ == "__main__":
    print("--- DEBUG START ---")
    try:
        print("1. Attempting to create Tkinter root...")
        root = tk.Tk()
        
        print("2. Attempting to initialize AttendanceApp class...")
        app = AttendanceApp(root)
        
        print("3. Success! Calling root.mainloop(). Check your taskbar now.")
        root.mainloop()
    except Exception as e:
        print(f"!!! CRITICAL UI ERROR: {e}")
    finally:
        print("--- DEBUG END ---")
        input("Press Enter to close this terminal...")