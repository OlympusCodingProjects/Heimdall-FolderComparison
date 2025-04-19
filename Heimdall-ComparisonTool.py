import tkinter as tk
from tkinter import filedialog, ttk
import os
import shutil
from pathlib import Path


class DirectoryComparisonTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Directory Comparison Tool")
        self.root.geometry("1000x600")

        # Source directory variables
        self.source_dir = tk.StringVar()
        self.source_files = []

        # Target directory variables
        self.target_dir = tk.StringVar()
        self.target_files = []

        # Missing files (in source but not in target)
        self.missing_files = []

        # Create the main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create directory selection frame
        self.create_directory_selection_frame()

        # Create directories comparison frame
        self.create_directories_comparison_frame()

        # Create buttons frame
        self.create_buttons_frame()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_directory_selection_frame(self):
        # Create directory selection frame
        dir_frame = ttk.LabelFrame(self.main_frame, text="Directory Selection", padding="10")
        dir_frame.pack(fill=tk.X, padx=5, pady=5)

        # Source directory selection
        ttk.Label(dir_frame, text="Source Directory:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(dir_frame, textvariable=self.source_dir, width=50).grid(row=0, column=1, sticky=tk.W + tk.E, padx=5,
                                                                          pady=5)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_source_directory).grid(row=0, column=2, padx=5,
                                                                                           pady=5)

        # Target directory selection
        ttk.Label(dir_frame, text="Target Directory:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(dir_frame, textvariable=self.target_dir, width=50).grid(row=1, column=1, sticky=tk.W + tk.E, padx=5,
                                                                          pady=5)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_target_directory).grid(row=1, column=2, padx=5,
                                                                                           pady=5)

        dir_frame.columnconfigure(1, weight=1)

    def create_directories_comparison_frame(self):
        # Create comparison frame
        comp_frame = ttk.LabelFrame(self.main_frame, text="Directories Comparison", padding="10")
        comp_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create two panes side by side
        paned_window = ttk.PanedWindow(comp_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Source files frame
        source_frame = ttk.LabelFrame(paned_window, text="Source Files")
        paned_window.add(source_frame, weight=1)

        # Source files treeview
        self.source_tree = ttk.Treeview(source_frame, columns=("size", "modified"), selectmode="extended")
        self.source_tree.heading("#0", text="Filename")
        self.source_tree.heading("size", text="Size")
        self.source_tree.heading("modified", text="Modified")
        self.source_tree.column("#0", width=200)
        self.source_tree.column("size", width=100)
        self.source_tree.column("modified", width=150)

        # Add scrollbar to source treeview
        source_scrollbar = ttk.Scrollbar(source_frame, orient="vertical", command=self.source_tree.yview)
        self.source_tree.configure(yscrollcommand=source_scrollbar.set)

        source_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.source_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Target files frame
        target_frame = ttk.LabelFrame(paned_window, text="Target Files")
        paned_window.add(target_frame, weight=1)

        # Target files treeview
        self.target_tree = ttk.Treeview(target_frame, columns=("size", "modified"), selectmode="extended")
        self.target_tree.heading("#0", text="Filename")
        self.target_tree.heading("size", text="Size")
        self.target_tree.heading("modified", text="Modified")
        self.target_tree.column("#0", width=200)
        self.target_tree.column("size", width=100)
        self.target_tree.column("modified", width=150)

        # Add scrollbar to target treeview
        target_scrollbar = ttk.Scrollbar(target_frame, orient="vertical", command=self.target_tree.yview)
        self.target_tree.configure(yscrollcommand=target_scrollbar.set)

        target_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.target_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Missing files frame
        missing_frame = ttk.LabelFrame(self.main_frame, text="Files Missing in Target")
        missing_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Missing files treeview
        self.missing_tree = ttk.Treeview(missing_frame, columns=("size", "path"), selectmode="extended")
        self.missing_tree.heading("#0", text="Filename")
        self.missing_tree.heading("size", text="Size")
        self.missing_tree.heading("path", text="Path")
        self.missing_tree.column("#0", width=200)
        self.missing_tree.column("size", width=100)
        self.missing_tree.column("path", width=400)

        # Add scrollbar to missing files treeview
        missing_scrollbar = ttk.Scrollbar(missing_frame, orient="vertical", command=self.missing_tree.yview)
        self.missing_tree.configure(yscrollcommand=missing_scrollbar.set)

        missing_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.missing_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def create_buttons_frame(self):
        # Create buttons frame
        buttons_frame = ttk.Frame(self.main_frame, padding="10")
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        # Compare button
        self.compare_btn = ttk.Button(buttons_frame, text="Compare Directories", command=self.compare_directories)
        self.compare_btn.pack(side=tk.LEFT, padx=5)

        # Copy missing files button
        self.copy_btn = ttk.Button(buttons_frame, text="Copy Missing Files", command=self.copy_missing_files)
        self.copy_btn.pack(side=tk.LEFT, padx=5)
        self.copy_btn["state"] = "disabled"

        # Exit button
        ttk.Button(buttons_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)

    def browse_source_directory(self):
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.source_dir.set(directory)
            self.status_var.set(f"Source directory set to: {directory}")

    def browse_target_directory(self):
        directory = filedialog.askdirectory(title="Select Target Directory")
        if directory:
            self.target_dir.set(directory)
            self.status_var.set(f"Target directory set to: {directory}")

    def compare_directories(self):
        source_dir = self.source_dir.get()
        target_dir = self.target_dir.get()

        if not source_dir or not os.path.isdir(source_dir):
            self.status_var.set("Error: Please select a valid source directory")
            return

        if not target_dir or not os.path.isdir(target_dir):
            self.status_var.set("Error: Please select a valid target directory")
            return

        # Clear previous data
        self.source_tree.delete(*self.source_tree.get_children())
        self.target_tree.delete(*self.target_tree.get_children())
        self.missing_tree.delete(*self.missing_tree.get_children())
        self.source_files = []
        self.target_files = []
        self.missing_files = []

        # Get files from source directory
        self.status_var.set("Loading source directory files...")
        self.populate_tree(self.source_tree, source_dir, self.source_files)

        # Get files from target directory
        self.status_var.set("Loading target directory files...")
        self.populate_tree(self.target_tree, target_dir, self.target_files)

        # Find missing files (in source but not in target)
        self.status_var.set("Finding missing files...")
        target_relative_paths = set()
        for file_info in self.target_files:
            target_relative_paths.add(file_info["relative_path"])

        for file_info in self.source_files:
            if file_info["relative_path"] not in target_relative_paths:
                self.missing_files.append(file_info)
                size_str = self.format_size(file_info["size"])
                self.missing_tree.insert("", tk.END, text=file_info["name"],
                                         values=(size_str, file_info["relative_path"]))

        # Update status and enable/disable copy button
        if self.missing_files:
            self.status_var.set(f"Found {len(self.missing_files)} files missing in target directory")
            self.copy_btn["state"] = "normal"
        else:
            self.status_var.set("No missing files found - directories are in sync")
            self.copy_btn["state"] = "disabled"

    def populate_tree(self, tree, directory, file_list):
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, directory)

                try:
                    file_stat = os.stat(file_path)
                    size = file_stat.st_size
                    modified = self.format_time(file_stat.st_mtime)

                    # Add to tree
                    file_info = {
                        "name": file,
                        "path": file_path,
                        "relative_path": rel_path,
                        "size": size,
                        "modified": modified
                    }
                    file_list.append(file_info)

                    size_str = self.format_size(size)
                    tree.insert("", tk.END, text=file, values=(size_str, modified))
                except Exception as e:
                    print(f"Error accessing file {file_path}: {e}")

    def format_size(self, size):
        # Convert bytes to human-readable format
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0

    def format_time(self, timestamp):
        # Convert timestamp to date-time string
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def copy_missing_files(self):
        if not self.missing_files:
            return

        source_dir = self.source_dir.get()
        target_dir = self.target_dir.get()

        copied_count = 0
        failed_count = 0

        for file_info in self.missing_files:
            source_file = os.path.join(source_dir, file_info["relative_path"])
            target_file = os.path.join(target_dir, file_info["relative_path"])

            # Create directory if it doesn't exist
            target_dir_path = os.path.dirname(target_file)
            if not os.path.exists(target_dir_path):
                os.makedirs(target_dir_path)

            try:
                shutil.copy2(source_file, target_file)
                copied_count += 1
            except Exception as e:
                print(f"Error copying {source_file} to {target_file}: {e}")
                failed_count += 1

        # Update status
        if failed_count == 0:
            self.status_var.set(f"Successfully copied {copied_count} files to target directory")
        else:
            self.status_var.set(f"Copied {copied_count} files, {failed_count} failed. See console for details.")

        # Refresh the target directory listing
        self.compare_directories()


if __name__ == "__main__":
    root = tk.Tk()
    app = DirectoryComparisonTool(root)
    root.mainloop()