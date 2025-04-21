import os
import shutil
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import win32com.client
import datetime


def format_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


class DirectoryComparisonTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Heimdall Directory Comparison Tool")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f5f5f5")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "heimdall-banner.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.source_dir = ""
        self.target_dir = ""
        self.missing_files = []

        self.checkmark_img = self.create_checkmark(color="green", size=15)
        self.x_mark_img = self.create_x_mark(color="red", size=15)

        self.setup_ui()

    def create_checkmark(self, color="green", size=15):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        for x in range(size):
            for y in range(size):
                if (y == int(size / 2 + x / 2) and x < size / 2) or (
                        y == int(size / 2 - (x - size / 2) / 2) and x >= size / 2):
                    if color == "green":
                        img.putpixel((x, y), (0, 200, 0, 255))
        return ImageTk.PhotoImage(img)

    def create_x_mark(self, color="red", size=15):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        for x in range(size):
            for y in range(size):
                if abs(x - y) < 2 or abs(x + y - size) < 2:
                    if color == "red":
                        img.putpixel((x, y), (200, 0, 0, 255))
        return ImageTk.PhotoImage(img)

    def setup_ui(self):
        banner_frame = ttk.Frame(self.root)
        banner_frame.pack(fill=tk.X)
        try:
            banner_image = Image.open("heimdall-banner.png")
            banner_image = banner_image.resize((466, 192), Image.LANCZOS)
            self.banner_photo = ImageTk.PhotoImage(banner_image)
            banner_label = ttk.Label(banner_frame, image=self.banner_photo)
            banner_label.pack()
        except Exception as e:
            print("Failed to load banner image:", e)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=10)

        ttk.Label(dir_frame, text="Source Directory:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.source_entry = ttk.Entry(dir_frame, width=50)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_source).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(dir_frame, text="Target Directory:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.target_entry = ttk.Entry(dir_frame, width=50)
        self.target_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_target).grid(row=1, column=2, padx=5, pady=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.compare_btn = ttk.Button(btn_frame, text="Compare Directories", command=self.compare_directories)
        self.compare_btn.pack(side=tk.LEFT, padx=5)

        self.copy_btn = ttk.Button(btn_frame, text="Copy Missing Files", command=self.copy_missing_files,
                                   state=tk.DISABLED)
        self.copy_btn.pack(side=tk.LEFT, padx=5)

        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        left_frame = ttk.LabelFrame(result_frame, text="Source Directory Files")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        right_frame = ttk.LabelFrame(result_frame, text="Comparison Results")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.source_listbox = tk.Listbox(left_frame, selectmode=tk.EXTENDED)
        self.source_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        source_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.source_listbox.yview)
        source_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.source_listbox.config(yscrollcommand=source_scrollbar.set)

        columns = ("file", "date", "status")
        self.result_tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        self.result_tree.heading("file", text="File Name")
        self.result_tree.heading("date", text="Modified Date")
        self.result_tree.heading("status", text="Status")
        self.result_tree.column("file", width=250)
        self.result_tree.column("date", width=150)
        self.result_tree.column("status", width=100, anchor=tk.CENTER)
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        result_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_tree.config(yscrollcommand=result_scrollbar.set)

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_dir = path
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, path)
            self.populate_source_list()

    def browse_target(self):
        path = filedialog.askdirectory()
        if path:
            self.target_dir = path
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, path)

    def populate_source_list(self):
        self.source_listbox.delete(0, tk.END)
        if not self.source_dir or not os.path.isdir(self.source_dir):
            return

        for root_dir, _, files in os.walk(self.source_dir):
            for file in files:
                full_path = os.path.relpath(os.path.join(root_dir, file), self.source_dir)
                self.source_listbox.insert(tk.END, full_path)

    def compare_directories(self):
        if not self.source_dir or not self.target_dir:
            self.status_var.set("Please select both source and target directories")
            return

        if not os.path.isdir(self.source_dir) or not os.path.isdir(self.target_dir):
            self.status_var.set("Invalid directory path")
            return

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        self.missing_files = []

        for root_dir, _, files in os.walk(self.source_dir):
            for file in files:
                source_path = os.path.join(root_dir, file)
                rel_path = os.path.relpath(source_path, self.source_dir)
                target_path = os.path.join(self.target_dir, rel_path)

                try:
                    mtime = os.path.getmtime(source_path)
                except:
                    mtime = 0

                if not os.path.exists(target_path):
                    self.missing_files.append(rel_path)
                    status = "Missing"
                    tag = "missing"
                    img = self.x_mark_img
                else:
                    status = "Exists"
                    tag = "exists"
                    img = self.checkmark_img

                self.result_tree.insert("", tk.END, values=(rel_path, format_date(mtime), status), image=img, tags=(tag,))

        self.result_tree.tag_configure("exists", foreground="green")
        self.result_tree.tag_configure("missing", foreground="red")

        if self.missing_files:
            self.copy_btn.config(state=tk.NORMAL)
            self.status_var.set(f"Comparison complete. {len(self.missing_files)} files missing in target directory.")
        else:
            self.copy_btn.config(state=tk.DISABLED)
            self.status_var.set("Comparison complete. All files exist in target directory.")

    def copy_missing_files(self):
        if not self.missing_files:
            return

        copied_count = 0
        for rel_path in self.missing_files:
            source_path = os.path.join(self.source_dir, rel_path)
            target_path = os.path.join(self.target_dir, rel_path)
            target_folder = os.path.dirname(target_path)
            try:
                os.makedirs(target_folder, exist_ok=True)
                shutil.copy2(source_path, target_path)
                copied_count += 1
            except Exception as e:
                print(f"Error copying {rel_path}: {e}")

        self.status_var.set(f"Copied {copied_count} files to target directory")
        self.compare_directories()


if __name__ == "__main__":
    root = tk.Tk()
    app = DirectoryComparisonTool(root)
    root.mainloop()
