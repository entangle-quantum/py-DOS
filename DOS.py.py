# A simple GUI Bash (shell) emulator in Python using Tkinter and subprocess.
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import subprocess
import threading
import os
import pickle
import glob

command_history = []
history_index = -1
SESSION_FILE = "gui_bash_session.pkl"

def run_command():
    global history_index
    cmd = entry.get()
    if not cmd.strip():
        return
    command_history.append(cmd)
    history_index = len(command_history)
    output_text.insert(tk.END, f"C:\\{os.getcwd().split(os.sep)[-1]}> {cmd}\n")
    entry.delete(0, tk.END)
    if cmd.lower() == "exit":
        root.quit()
        return
    elif cmd.lower().startswith("cd "):
        path = cmd[3:].strip()
        try:
            os.chdir(path)
            output_text.insert(tk.END, f"Changed directory to {os.getcwd()}\n")
        except Exception as e:
            output_text.insert(tk.END, f"cd: {e}\n")
        output_text.insert(tk.END, f"C:\\{os.getcwd().split(os.sep)[-1]}> ")
        output_text.see(tk.END)
        return
    elif cmd.lower() == "cls":
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, f"Microsoft(R) MS-DOS(R) Shell\nCopyright (C) Microsoft Corp 1990-2025.\n\nC:\\{os.getcwd().split(os.sep)[-1]}> ")
        output_text.see(tk.END)
        return
    elif cmd.lower() == "help":
        output_text.insert(tk.END, "Built-in commands:\n  cd <dir>\n  cls\n  exit\n  help\n")
        output_text.insert(tk.END, f"C:\\{os.getcwd().split(os.sep)[-1]}> ")
        output_text.see(tk.END)
        return
    def worker():
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
            output = result.stdout + result.stderr
        except Exception as e:
            output = str(e)
        output_text.insert(tk.END, output)
        output_text.insert(tk.END, f"C:\\{os.getcwd().split(os.sep)[-1]}> ")
        output_text.see(tk.END)
    threading.Thread(target=worker, daemon=True).start()

def on_enter(event):
    run_command()

def change_dir():
    path = simpledialog.askstring("cd", "Enter directory:", initialvalue=os.getcwd())
    if path:
        try:
            os.chdir(path)
            output_text.insert(tk.END, f"Changed directory to {os.getcwd()}\n")
        except Exception as e:
            output_text.insert(tk.END, f"cd: {e}\n")
        output_text.see(tk.END)

def set_terminal_theme():
    # Set colors for a classic MS-DOS look
    root.configure(bg="black")
    output_text.configure(bg="black", fg="white", insertbackground="white", font=("Consolas", 11))
    entry.configure(bg="black", fg="white", insertbackground="white", font=("Consolas", 11))

def on_key(event):
    global history_index
    if event.keysym == "Up":
        if command_history:
            history_index = max(0, history_index - 1)
            entry.delete(0, tk.END)
            entry.insert(0, command_history[history_index])
    elif event.keysym == "Down":
        if command_history:
            history_index = min(len(command_history) - 1, history_index + 1)
            entry.delete(0, tk.END)
            entry.insert(0, command_history[history_index])

def save_session():
    with open(SESSION_FILE, "wb") as f:
        pickle.dump({
            "history": command_history,
            "output": output_text.get(1.0, tk.END),
            "cwd": os.getcwd()
        }, f)

def load_session():
    global command_history, history_index
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "rb") as f:
            data = pickle.load(f)
            command_history = data.get("history", [])
            history_index = len(command_history)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, data.get("output", ""))
            try:
                os.chdir(data.get("cwd", os.getcwd()))
            except Exception:
                pass

def open_settings():
    color = simpledialog.askstring("Color", "Enter text color (e.g., white, lime, yellow):", initialvalue="white")
    bg = simpledialog.askstring("Background", "Enter background color:", initialvalue="black")
    font = simpledialog.askstring("Font", "Enter font (e.g., Consolas, Courier):", initialvalue="Consolas")
    try:
        output_text.configure(fg=color, bg=bg, font=(font, 11))
        entry.configure(fg=color, bg=bg, font=(font, 11))
    except Exception as e:
        messagebox.showerror("Settings Error", str(e))

def show_about():
    messagebox.showinfo("About", "GUI Bash\nA Python MS-DOS style shell\nBy CherryDev 2025")

def show_easter_egg():
    output_text.insert(tk.END, r"""
      ________   ________   ________   ________     
     /  _____/  /  _____/  /  _____/  /  _____/     
    /  /       /  /       /  /       /  /           
   /  /       /  /       /  /       /  /            
  /  /____   /  /____   /  /____   /  /____         
 /_______/  /_______/  /_______/  /_______/         
    """)
    output_text.see(tk.END)

def on_tab(event):
    text = entry.get()
    if text.strip().startswith("cd "):
        partial = text[3:].strip()
        matches = glob.glob(partial + "*")
        if matches:
            entry.delete(0, tk.END)
            entry.insert(0, "cd " + matches[0])
    return "break"

def log_output():
    with open("gui_bash_output.log", "a", encoding="utf-8") as f:
        f.write(output_text.get(1.0, tk.END))

root = tk.Tk()
root.title("GUI Bash (Python)")

output_text = scrolledtext.ScrolledText(root, width=80, height=24, font=("Consolas", 10))
output_text.pack(padx=5, pady=5)

entry = tk.Entry(root, width=80, font=("Consolas", 10))
entry.pack(padx=5, pady=5)
entry.bind("<Return>", on_enter)
entry.bind("<Up>", on_key)
entry.bind("<Down>", on_key)
entry.bind("<Tab>", on_tab)

set_terminal_theme()

output_text.insert(tk.END, f"Microsoft(R) MS-DOS(R) Shell\nCopyright (C) Microsoft Corp 1990-2025.\n\nC:\\{os.getcwd().split(os.sep)[-1]}> \n")
output_text.see(tk.END)

root.protocol("WM_DELETE_WINDOW", lambda: (save_session(), root.destroy()))
load_session()
root.bind("<Control-s>", lambda e: open_settings())
root.bind("<F1>", lambda e: show_about())
root.bind("<F2>", lambda e: show_easter_egg())
root.bind("<Control-l>", lambda e: log_output())

root.mainloop()