import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import subprocess
import threading
import sys
import os

# --- Configuration ---
# Path to the python executable running this script.
# This ensures we use the same Python environment where all the dependencies are installed.
PYTHON_EXECUTABLE = sys.executable

class AdastreaDirectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Game Director")
        self.root.geometry("800x600")

        # --- Main Frame ---
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Top Frame for Buttons ---
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        self.ingest_button = tk.Button(top_frame, text="Update Knowledge Base", command=self.run_ingestion)
        self.ingest_button.pack(side=tk.LEFT)

        self.api_key_button = tk.Button(top_frame, text="Set OpenAI API Key", command=self.set_api_key)
        self.api_key_button.pack(side=tk.LEFT, padx=10)

        # --- Response Display Area ---
        response_label = tk.Label(main_frame, text="Assistant Response:")
        response_label.pack(fill=tk.X)
        self.response_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, state=tk.DISABLED)
        self.response_text.pack(fill=tk.BOTH, expand=True)

        # --- Query Input Area ---
        query_label = tk.Label(main_frame, text="Your Question:")
        query_label.pack(fill=tk.X, pady=(10, 0))
        self.query_entry = tk.Entry(main_frame, width=80)
        self.query_entry.pack(fill=tk.X)
        self.query_entry.bind("<Return>", self.run_query_event)

        self.ask_button = tk.Button(main_frame, text="Ask", command=self.run_query)
        self.ask_button.pack(pady=5)
        
        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Please set your OpenAI API Key if you haven't.")
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.check_api_key_on_startup()

    def set_api_key(self):
        """Opens a dialog to ask for the API key."""
        key = simpledialog.askstring("API Key", "Please enter your OpenAI API Key:", show='*')
        if key:
            os.environ['OPENAI_API_KEY'] = key
            self.status_var.set("API Key set successfully. Ready to ingest or query.")
            messagebox.showinfo("Success", "API Key has been set for this session.")

    def check_api_key_on_startup(self):
        """Checks if the API key is set and prompts the user if not."""
        if not os.getenv("OPENAI_API_KEY"):
            self.root.after(500, self.set_api_key)

    def run_ingestion(self):
        """Runs the ingest.py script in a separate thread."""
        self.run_script_in_thread('ingest.py', "Ingesting documents...")

    def run_query_event(self, event):
        """Handler for pressing Enter in the query box."""
        self.run_query()
        
    def run_query(self):
        """Runs the main.py query script in a separate thread."""
        query = self.query_entry.get()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a question.")
            return
        
        # Add quotes around the query to handle multi-word inputs correctly
        self.run_script_in_thread('main.py', f'Querying for: "{query}"', query)

    def run_script_in_thread(self, script_name, status_message, *args):
        """
        Generic function to run a python script in a thread to keep the GUI responsive.
        """
        self.ingest_button.config(state=tk.DISABLED)
        self.ask_button.config(state=tk.DISABLED)
        self.status_var.set(status_message)
        
        command = [PYTHON_EXECUTABLE, script_name] + list(args)

        thread = threading.Thread(target=self._execute_command, args=(command,))
        thread.start()

    def _execute_command(self, command):
        """The actual command execution logic."""
        try:
            # Use CREATE_NO_WINDOW on Windows to prevent console window from appearing
            kwargs = {'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE, 'text': True}
            if sys.platform == 'win32' and hasattr(subprocess, 'CREATE_NO_WINDOW'):
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            process = subprocess.Popen(command, **kwargs)
            stdout, stderr = process.communicate()
            
            output = stdout
            if process.returncode != 0:
                output += f"\n--- ERROR ---\n{stderr}"
            
            # Schedule the UI update to run on the main thread
            self.root.after(0, self._update_ui_after_execution, output, process.returncode)

        except Exception as e:
            self.root.after(0, self._update_ui_after_execution, str(e), 1)

    def _update_ui_after_execution(self, output, returncode):
        """Updates the GUI elements after the script has finished."""
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, output)
        self.response_text.config(state=tk.DISABLED)

        if returncode == 0:
            self.status_var.set("Ready.")
        else:
            self.status_var.set("An error occurred. Check the response window for details.")
            
        self.ingest_button.config(state=tk.NORMAL)
        self.ask_button.config(state=tk.NORMAL)

def main():
    root = tk.Tk()
    app = AdastreaDirectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
