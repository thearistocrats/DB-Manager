import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
import platform

# Image metadata
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# 🎵 Music metadata
try:
    from mutagen import File as MutagenFile
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3, ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

def get_file_metadata(file_path):
    stats = os.stat(file_path)
    return {
        "Name": os.path.basename(file_path),
        "Full Path": file_path,
        "Created": time.ctime(stats.st_ctime),
        "Modified": time.ctime(stats.st_mtime),
        "Accessed": time.ctime(stats.st_atime),
    }

def set_file_times(file_path, created=None, modified=None, accessed=None):
    current = os.stat(file_path)
    atime = time.mktime(time.strptime(accessed, "%a %b %d %H:%M:%S %Y")) if accessed else current.st_atime
    mtime = time.mktime(time.strptime(modified, "%a %b %d %H:%M:%S %Y")) if modified else current.st_mtime
    os.utime(file_path, (atime, mtime))
    if platform.system() == 'Windows' and created:
        try:
            import pywintypes
            import win32file
            import win32con
            fh = win32file.CreateFile(
                file_path, win32con.GENERIC_WRITE,
                0, None, win32con.OPEN_EXISTING,
                win32con.FILE_ATTRIBUTE_NORMAL, None
            )
            ctime = pywintypes.Time(time.mktime(time.strptime(created, "%a %b %d %H:%M:%S %Y")))
            win32file.SetFileTime(fh, ctime, None, None)
            fh.close()
        except Exception as e:
            print("Failed to set creation time:", e)

def get_image_exif(file_path):
    if not PIL_AVAILABLE:
        return {}
    try:
        image = Image.open(file_path)
        info = image._getexif()
        if not info:
            return {}
        return {TAGS.get(tag): val for tag, val in info.items() if TAGS.get(tag)}
    except Exception:
        return {}

# 🎵 Read music metadata
def get_music_metadata(file_path):
    if not MUTAGEN_AVAILABLE:
        return {}
    try:
        audio = MutagenFile(file_path, easy=True)
        if audio is None:
            return {}
        fields = ["title", "artist", "album", "date", "genre"]
        return {field: ", ".join(audio.get(field, [""])) for field in fields}
    except Exception as e:
        print("Music metadata error:", e)
        return {}

# 🎵 Write music metadata
def set_music_metadata(file_path, metadata):
    if not MUTAGEN_AVAILABLE:
        return
    try:
        audio = EasyID3(file_path)
    except ID3NoHeaderError:
        audio = EasyID3()
        audio.save(file_path)
        audio = EasyID3(file_path)

    for key, value in metadata.items():
        audio[key] = value
    audio.save()

class MetadataEditorApp:
    def __init__(self, master):
        self.master = master
        master.title("File Metadata Editor")

        self.frame = ttk.Frame(master, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.select_button = ttk.Button(self.frame, text="📁 Select File", command=self.select_file)
        self.select_button.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Standard file metadata
        self.entries = {}
        row = 1
        for field in ["Name", "Full Path", "Created", "Modified", "Accessed"]:
            ttk.Label(self.frame, text=field + ":").grid(row=row, column=0, sticky="e")
            entry = ttk.Entry(self.frame, width=60)
            entry.grid(row=row, column=1, sticky="ew")
            self.entries[field] = entry
            row += 1

        # 🎵 Music metadata fields
        self.music_entries = {}
        for field in ["Title", "Artist", "Album", "Year", "Genre"]:
            ttk.Label(self.frame, text=field + ":").grid(row=row, column=0, sticky="e")
            entry = ttk.Entry(self.frame, width=60)
            entry.grid(row=row, column=1, sticky="ew")
            self.music_entries[field.lower()] = entry
            row += 1

        self.apply_button = ttk.Button(self.frame, text="✅ Apply Changes", command=self.apply_changes)
        self.apply_button.grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1

        self.exif_box = tk.Text(self.frame, height=10, width=80)
        self.exif_box.grid(row=row, column=0, columnspan=2, sticky="nsew")

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(row, weight=1)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        self.selected_file = file_path
        metadata = get_file_metadata(file_path)
        for field, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, metadata.get(field, ""))

        self.load_exif(file_path)
        self.load_music_metadata(file_path)

    def load_exif(self, file_path):
        self.exif_box.delete(1.0, tk.END)
        if PIL_AVAILABLE:
            exif_data = get_image_exif(file_path)
            if exif_data:
                for key, value in exif_data.items():
                    self.exif_box.insert(tk.END, f"{key}: {value}\n")
            else:
                self.exif_box.insert(tk.END, "No EXIF data found.")
        else:
            self.exif_box.insert(tk.END, "Pillow not installed. Cannot load EXIF data.")

    def load_music_metadata(self, file_path):
        for entry in self.music_entries.values():
            entry.delete(0, tk.END)
        if MUTAGEN_AVAILABLE and file_path.lower().endswith((".mp3", ".flac", ".m4a", ".ogg")):
            data = get_music_metadata(file_path)
            for key, val in data.items():
                if key in self.music_entries:
                    self.music_entries[key].insert(0, val)

    def apply_changes(self):
        if not hasattr(self, 'selected_file'):
            messagebox.showwarning("No file", "Please select a file first.")
            return

        name = self.entries["Name"].get()
        full_path = self.entries["Full Path"].get()
        new_path = os.path.join(os.path.dirname(full_path), name)

        created = self.entries["Created"].get()
        modified = self.entries["Modified"].get()
        accessed = self.entries["Accessed"].get()

        try:
            if new_path != self.selected_file:
                os.rename(self.selected_file, new_path)
                self.selected_file = new_path

            set_file_times(new_path, created, modified, accessed)

            # 🎵 Apply music tag changes
            if MUTAGEN_AVAILABLE and new_path.lower().endswith((".mp3", ".flac", ".m4a", ".ogg")):
                metadata = {key: entry.get() for key, entry in self.music_entries.items()}
                set_music_metadata(new_path, metadata)

            messagebox.showinfo("Success", "Metadata updated.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply changes:\n{e}")

# --- Main ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MetadataEditorApp(root)
    root.mainloop()
