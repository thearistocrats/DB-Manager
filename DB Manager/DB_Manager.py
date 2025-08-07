import os
import sqlite3
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk

DB_NAME = "file_manager.db"

# --- Database functions ---

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS file_tags (
        file_id INTEGER,
        tag_id INTEGER,
        PRIMARY KEY (file_id, tag_id),
        FOREIGN KEY (file_id) REFERENCES files(id),
        FOREIGN KEY (tag_id) REFERENCES tags(id))''')
    conn.commit()
    conn.close()

def add_file(file_path):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO files (path) VALUES (?)", (file_path,))
    conn.commit()
    conn.close()

def add_tag(tag_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
    conn.commit()
    conn.close()

def get_all_tags():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name FROM tags ORDER BY name")
    tags = [row[0] for row in c.fetchall()]
    conn.close()
    return tags

def get_all_files():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT path FROM files ORDER BY path")
    files = [row[0] for row in c.fetchall()]
    conn.close()
    return files

def get_files_by_tag(tag_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT files.path FROM files
        JOIN file_tags ON files.id = file_tags.file_id
        JOIN tags ON tags.id = file_tags.tag_id
        WHERE tags.name = ?
        ORDER BY files.path
    ''', (tag_name,))
    files = [row[0] for row in c.fetchall()]
    conn.close()
    return files

def tag_file(file_path, tag_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Ensure tag and file exist
    c.execute("INSERT OR IGNORE INTO files (path) VALUES (?)", (file_path,))
    c.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
    c.execute("SELECT id FROM files WHERE path = ?", (file_path,))
    file_id = c.fetchone()[0]
    c.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    tag_id = c.fetchone()[0]
    c.execute("INSERT OR IGNORE INTO file_tags (file_id, tag_id) VALUES (?, ?)", (file_id, tag_id))
    conn.commit()
    conn.close()

def scan_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for f in files:
            full_path = os.path.abspath(os.path.join(root, f))
            add_file(full_path)

# --- GUI ---

class FileTaggerApp:
    def __init__(self, master):
        self.master = master
        master.title("File Tagger")

        # Layout
        self.frame = ttk.Frame(master, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.folder_button = ttk.Button(self.frame, text="📁 Scan Folder", command=self.scan_folder)
        self.folder_button.grid(row=0, column=0, sticky="ew")

        self.add_tag_button = ttk.Button(self.frame, text="🏷️ Add Tag to Selected", command=self.tag_selected_file)
        self.add_tag_button.grid(row=0, column=1, sticky="ew")

        self.filter_label = ttk.Label(self.frame, text="Filter by tag:")
        self.filter_label.grid(row=1, column=0, sticky="w")

        self.tag_var = tk.StringVar()
        self.tag_combo = ttk.Combobox(self.frame, textvariable=self.tag_var, postcommand=self.refresh_tags)
        self.tag_combo.bind("<<ComboboxSelected>>", self.filter_files_by_tag)
        self.tag_combo.grid(row=1, column=1, sticky="ew")

        self.file_listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE, width=80, height=20)
        self.file_listbox.grid(row=2, column=0, columnspan=2, sticky="nsew")

        # Configure resizing
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=2)
        self.frame.rowconfigure(2, weight=1)

        # Load initial file list
        self.refresh_file_list()

    def refresh_file_list(self, files=None):
        self.file_listbox.delete(0, tk.END)
        if files is None:
            files = get_all_files()
        for f in files:
            self.file_listbox.insert(tk.END, f)

    def refresh_tags(self):
        tags = get_all_tags()
        self.tag_combo['values'] = [""] + tags

    def scan_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            scan_folder(folder)
            self.refresh_file_list()
            self.refresh_tags()

    def tag_selected_file(self):
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showwarning("No selection", "Select a file to tag.")
            return

        file_path = self.file_listbox.get(selected[0])
        tag = simpledialog.askstring("Add Tag", f"Enter tag for:\n{file_path}")
        if tag:
            tag_file(file_path, tag)
            self.refresh_tags()
            messagebox.showinfo("Tagged", f"Tagged:\n{file_path}\nwith '{tag}'")

    def filter_files_by_tag(self, event=None):
        tag = self.tag_var.get()
        if tag:
            files = get_files_by_tag(tag)
            self.refresh_file_list(files)
        else:
            self.refresh_file_list()

# --- Main ---
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = FileTaggerApp(root)
    root.mainloop()
