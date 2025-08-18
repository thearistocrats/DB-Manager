import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class MassRenamerApp:
    def __init__(self, master):
        self.master = master
        master.title("Mass File Renamer")

        self.folder_path = ""
        self.files = []

        # UI Layout
        self.frame = ttk.Frame(master, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Folder selection
        self.select_button = ttk.Button(self.frame, text="📁 Select Folder", command=self.select_folder)
        self.select_button.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Find/Replace inputs
        ttk.Label(self.frame, text="Find:").grid(row=1, column=0, sticky="e")
        self.find_entry = ttk.Entry(self.frame, width=30)
        self.find_entry.grid(row=1, column=1, sticky="ew")

        ttk.Label(self.frame, text="Replace with:").grid(row=2, column=0, sticky="e")
        self.replace_entry = ttk.Entry(self.frame, width=30)
        self.replace_entry.grid(row=2, column=1, sticky="ew")

        # Preview and rename
        self.preview_button = ttk.Button(self.frame, text="🔍 Preview", command=self.preview_renames)
        self.preview_button.grid(row=3, column=0, sticky="ew")

        self.rename_button = ttk.Button(self.frame, text="✏️ Rename", command=self.rename_files)
        self.rename_button.grid(row=3, column=1, sticky="ew")

        # Preview area
        self.listbox = tk.Listbox(self.frame, width=60, height=15)
        self.listbox.grid(row=4, column=0, columnspan=2, sticky="nsew")

        # Make rows/columns resizable
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(4, weight=1)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            self.files = os.listdir(folder)
            self.listbox.delete(0, tk.END)
            self.listbox.insert(tk.END, f"Selected folder: {folder}")
            self.listbox.insert(tk.END, f"{len(self.files)} files loaded.")

    def preview_renames(self):
        self.listbox.delete(0, tk.END)
        if not self.folder_path:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return

        find_str = self.find_entry.get()
        replace_str = self.replace_entry.get()
        if not find_str:
            messagebox.showwarning("Missing input", "Please enter a string to find.")
            return

        preview_count = 0
        self.preview_map = {}

        for filename in self.files:
            if find_str in filename:
                new_name = filename.replace(find_str, replace_str)
                self.preview_map[filename] = new_name
                self.listbox.insert(tk.END, f"{filename}  ➡  {new_name}")
                preview_count += 1

        if preview_count == 0:
            self.listbox.insert(tk.END, "No matches found.")

    def rename_files(self):
        if not hasattr(self, 'preview_map') or not self.preview_map:
            messagebox.showinfo("Nothing to rename", "Preview changes before renaming.")
            return

        success = 0
        errors = 0

        for old_name, new_name in self.preview_map.items():
            old_path = os.path.join(self.folder_path, old_name)
            new_path = os.path.join(self.folder_path, new_name)

            try:
                if not os.path.exists(new_path):  # prevent overwrite
                    os.rename(old_path, new_path)
                    success += 1
                else:
                    errors += 1
            except Exception as e:
                errors += 1

        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, f"Renamed {success} file(s). {errors} error(s).")

        self.preview_map = {}
        self.files = os.listdir(self.folder_path)

def launch_mass_renamer():
    root = tk.Toplevel()
    app = MassRenamerApp(root)
