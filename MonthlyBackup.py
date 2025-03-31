import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import queue
import sv_ttk
from tkinter.font import Font
import time
import json
from pathlib import Path

class BackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DevOps Monthly Backup Tool")
        self.root.geometry("1000x700")
        
        # Configuration file path
        self.CONFIG_FILE = "backup_config.json"
        
        # Hardcoded WinRAR path
        self.winrar_path = r"C:\Program Files\WinRAR\WinRAR.exe"
        
        # Initialize email settings
        self.smtp_server = ""
        self.smtp_port = "587"
        self.email_address = ""
        self.email_password = ""
        self.recipient_email = ""
        
        # Load configuration
        self.load_config()
        
        self.setup_ui()
        self.folder_vars = []
        
        # Queue for thread-safe GUI updates
        self.gui_queue = queue.Queue()
        self.root.after(100, self.process_queue)

    def load_config(self):
        """Load configuration from file"""
        config_path = Path(self.CONFIG_FILE)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.smtp_server = config.get('smtp_server', '')
                    self.smtp_port = config.get('smtp_port', '587')
                    self.email_address = config.get('email_address', '')
                    self.email_password = config.get('email_password', '')
                    self.recipient_email = config.get('recipient_email', '')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")

    def save_config(self):
        """Save configuration to file"""
        config = {
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'email_address': self.email_address,
            'email_password': self.email_password,
            'recipient_email': self.recipient_email
        }
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def setup_ui(self):
        # Apply modern theme
        sv_ttk.set_theme("dark")
        
        # Custom font
        title_font = Font(family="Segoe UI", size=14, weight="bold")
        button_font = Font(family="Segoe UI", size=10)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with logo and buttons
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # App title with icon
        ttk.Label(
            header_frame, 
            text="📦 DEVOPS MONTHLY BACKUP TOOL",
            font=title_font,
            foreground="#4fc3f7"
        ).pack(side=tk.LEFT)
        
        # Action buttons on right
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame, 
            text="⚙️", 
            command=self.show_settings,
            style="Accent.TButton",
            width=3
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame, 
            text="ℹ️", 
            command=self.show_about,
            style="Accent.TButton",
            width=3
        ).pack(side=tk.LEFT, padx=2)
        
        # Configuration Panel
        config_frame = ttk.LabelFrame(main_frame, text=" Settings ", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # WinRAR Path
        winrar_frame = ttk.Frame(config_frame)
        winrar_frame.pack(fill=tk.X, pady=2)
        ttk.Label(winrar_frame, text="WinRAR:").pack(side=tk.LEFT)
        self.winrar_entry = ttk.Entry(winrar_frame)
        self.winrar_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.winrar_entry.insert(0, self.winrar_path)
        ttk.Button(
            winrar_frame, 
            text="...", 
            command=self.browse_winrar,
            style="Accent.TButton",
            width=3
        ).pack(side=tk.LEFT)
        
        # Source and Destination
        source_frame = ttk.Frame(config_frame)
        source_frame.pack(fill=tk.X, pady=2)
        ttk.Label(source_frame, text="Source:").pack(side=tk.LEFT)
        self.source_entry = ttk.Entry(source_frame)
        self.source_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(
            source_frame, 
            text="...", 
            command=self.browse_source,
            style="Accent.TButton",
            width=3
        ).pack(side=tk.LEFT)
        
        dest_frame = ttk.Frame(config_frame)
        dest_frame.pack(fill=tk.X, pady=2)
        ttk.Label(dest_frame, text="Destination:").pack(side=tk.LEFT)
        self.destination_entry = ttk.Entry(dest_frame)
        self.destination_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(
            dest_frame, 
            text="...", 
            command=self.browse_destination,
            style="Accent.TButton",
            width=3
        ).pack(side=tk.LEFT)
        
        # Action Buttons
        action_frame = ttk.Frame(config_frame)
        action_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            action_frame, 
            text="🔄 Load", 
            command=self.load_folders,
            style="Accent.TButton",
            width=8
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            action_frame, 
            text="✅ All", 
            command=self.select_all_folders,
            style="Accent.TButton",
            width=8
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            action_frame, 
            text="🚀 Backup", 
            command=self.backup_folders,
            style="Accent.TButton",
            width=10
        ).pack(side=tk.RIGHT, padx=2)
        
        # Folder Selection Panel
        self.folder_frame = ttk.LabelFrame(main_frame, text=" Folders ", padding=10)
        self.folder_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas and Scrollbar for folders
        self.canvas = tk.Canvas(self.folder_frame, bg="#333333", highlightthickness=0, height=150)
        self.scrollbar = ttk.Scrollbar(self.folder_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Progress and Log Panel
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(bottom_frame, text=" Progress ", padding=10)
        progress_frame.pack(fill=tk.X, pady=(5, 5))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            orient="horizontal", 
            mode="determinate",
            style="success.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X, expand=True, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready", anchor=tk.W)
        self.progress_label.pack(fill=tk.X)
        
        # Log Frame
        log_frame = ttk.LabelFrame(bottom_frame, text=" Log ", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=8, 
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#333333",
            fg="white",
            insertbackground="white"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(
            main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            padding=(3, 3),
            style="Status.TLabel"
        ).pack(fill=tk.X, pady=(2, 0))
        
        # Configure weights
        config_frame.columnconfigure(0, weight=1)
        self.folder_frame.columnconfigure(0, weight=1)
        self.folder_frame.rowconfigure(0, weight=1)

    def browse_winrar(self):
        file = filedialog.askopenfilename(
            title="Select WinRAR executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")],
            initialdir=r"C:\Program Files\WinRAR"
        )
        if file:
            self.winrar_entry.delete(0, tk.END)
            self.winrar_entry.insert(0, file)
            self.winrar_path = file

    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, folder)
            self.status_var.set(f"Source: {folder}")

    def browse_destination(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.destination_entry.delete(0, tk.END)
            self.destination_entry.insert(0, folder)
            self.status_var.set(f"Destination: {folder}")

    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        
        # Create StringVars and set their values from loaded config
        smtp_server_var = tk.StringVar(value=self.smtp_server)
        smtp_port_var = tk.StringVar(value=self.smtp_port)
        email_var = tk.StringVar(value=self.email_address)
        password_var = tk.StringVar(value=self.email_password)
        recipient_var = tk.StringVar(value=self.recipient_email)
        
        ttk.Label(settings_window, text="Application Settings", font=("Segoe UI", 12)).pack(pady=10)
        
        email_frame = ttk.LabelFrame(settings_window, text="Email Notification", padding=10)
        email_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(email_frame, text="SMTP Server:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(email_frame, textvariable=smtp_server_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(email_frame, text="SMTP Port:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(email_frame, textvariable=smtp_port_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(email_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(email_frame, textvariable=email_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(email_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(email_frame, show="*", textvariable=password_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(email_frame, text="Recipient:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(email_frame, textvariable=recipient_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=2)
        
        def save_settings():
            self.smtp_server = smtp_server_var.get()
            self.smtp_port = smtp_port_var.get()
            self.email_address = email_var.get()
            self.email_password = password_var.get()
            self.recipient_email = recipient_var.get()
            
            self.save_config()  # Save to file
            messagebox.showinfo("Settings Saved", "Email settings have been saved.")
            settings_window.destroy()
        
        ttk.Button(
            settings_window, 
            text="Save Settings", 
            command=save_settings,
            style="Accent.TButton"
        ).pack(pady=10)

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("300x200")
        
        ttk.Label(about_window, text="📦 Backup Manager", font=("Segoe UI", 12, "bold")).pack(pady=10)
        ttk.Label(about_window, text="Version 1.0.0").pack()
        ttk.Label(about_window, text=" DevOps Backup Tool").pack(pady=10)
        
        ttk.Button(about_window, text="Close", command=about_window.destroy, style="Accent.TButton").pack()

    def load_folders(self):
        source_path = self.source_entry.get()
        if not source_path:
            messagebox.showerror("Error", "Please select a source folder first!")
            return
            
        if not os.path.exists(source_path):
            messagebox.showerror("Error", "Source folder does not exist!")
            return

        # Clear previous widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            folders = [f for f in os.listdir(source_path) if os.path.isdir(os.path.join(source_path, f))]
            
            if not folders:
                ttk.Label(
                    self.scrollable_frame, 
                    text="No folders found",
                    foreground="gray"
                ).pack(pady=20)
                return
            
            self.folder_vars = []
            
            # Organize folders into a grid (3 columns)
            for i, folder in enumerate(folders):
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(
                    self.scrollable_frame, 
                    text=folder, 
                    variable=var,
                    style="Toggle.TButton"
                )
                
                row = i // 3
                col = i % 3
                chk.grid(row=row, column=col, padx=5, pady=1, sticky=tk.W)
                self.folder_vars.append((folder, var))
                
            self.status_var.set(f"Loaded {len(folders)} folders")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load folders: {str(e)}")
            self.status_var.set("Error loading folders")

    def select_all_folders(self):
        for _, var in self.folder_vars:
            var.set(True)
        self.status_var.set("All folders selected")

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("Log cleared")

    def send_email_notification(self, subject, message):
        """Send email notification using saved settings"""
        if not all([self.smtp_server, self.smtp_port, self.email_address, 
                   self.email_password, self.recipient_email]):
            self.log_text.insert(tk.END, "\nEmail notification skipped - incomplete settings\n")
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            # Format the message with proper line breaks and formatting
            formatted_message = f""" DevOps Backup Notification

{message}

Backup completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            msg.attach(MIMEText(formatted_message, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, int(self.smtp_port)) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
                
            self.log_text.insert(tk.END, f"\nEmail notification sent to {self.recipient_email}\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"\nFailed to send email: {str(e)}\n")

    def backup_folders(self):
        # Validate inputs
        if not self.winrar_entry.get() or not os.path.exists(self.winrar_entry.get()):
            messagebox.showerror("Error", "Invalid WinRAR path!")
            return
            
        source_path = self.source_entry.get()
        destination_path = self.destination_entry.get()

        if not source_path or not destination_path:
            messagebox.showerror("Error", "Please select both folders!")
            return

        if not os.path.exists(source_path):
            messagebox.showerror("Error", "Source folder doesn't exist!")
            return

        # Create destination if needed
        if not os.path.exists(destination_path):
            try:
                os.makedirs(destination_path)
            except OSError as e:
                messagebox.showerror("Error", f"Can't create destination: {str(e)}")
                return

        # Create backup directory with timestamp
        now = datetime.now()
        backup_dir = os.path.join(
            destination_path, 
            f"Backup_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
        )
        
        try:
            os.makedirs(backup_dir)
        except OSError as e:
            messagebox.showerror("Error", f"Can't create backup folder: {str(e)}")
            return

        # Get selected folders
        selected_folders = [folder for folder, var in self.folder_vars if var.get()]
        if not selected_folders:
            messagebox.showwarning("Warning", "No folders selected!")
            return

        # Prepare UI for backup
        self.clear_log()
        self.progress_bar["value"] = 0
        self.progress_label.config(text="Starting...")
        self.status_var.set("Backup in progress...")
        
        # Run backup in a separate thread
        threading.Thread(
            target=self.perform_backup,
            args=(selected_folders, source_path, backup_dir),
            daemon=True
        ).start()

    def perform_backup(self, folders, source_path, backup_dir):
        total_folders = len(folders)
        success_count = 0
        backed_up_files = []  # List to store successfully backed up files
        
        for i, folder in enumerate(folders):
            folder_path = os.path.join(source_path, folder)
            archive_name = f"{folder}.rar"
            archive_path = os.path.join(backup_dir, archive_name)
            
            # Update UI
            self.gui_queue.put(("log", f"\nBacking up '{folder}'...\n"))
            self.gui_queue.put(("progress", (i / total_folders) * 100))
            self.gui_queue.put(("progress_text", f"{i+1}/{total_folders}"))
            
            # Build WinRAR command with more performance-friendly settings
            winrar_cmd = [
                self.winrar_entry.get(),
                "a",                    # Add to archive
                "-r",                   # Recurse subdirectories
                "-ep1",                 # Exclude base directory
                "-ibck",                # Run in background
                "-y",                   # Assume yes on all queries
                "-m1",                  # Use fastest compression (less CPU intensive)
                "-dh",                  # Disable hard links processing
                "-oi",                  # Disable "save NTFS security info"
                "-ol",                  # Store symbolic links as links
                "-os",                  # Save NTFS alternate streams
                "-t",                   # Test after archiving
                archive_path,
                folder_path
            ]
            
            try:
                # Configure process for minimal impact
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                # Create process with low priority
                process = subprocess.Popen(
                    winrar_cmd,
                    startupinfo=startupinfo,
                    creationflags=(
                        subprocess.CREATE_NO_WINDOW | 
                        subprocess.BELOW_NORMAL_PRIORITY_CLASS
                    )
                )
                
                # Monitor progress without blocking
                while process.poll() is None:
                    time.sleep(0.5)  # Longer sleep to reduce CPU usage
                    # Update progress if needed
                    if os.path.exists(archive_path):
                        try:
                            current_size = os.path.getsize(archive_path)
                            folder_size = sum(
                                os.path.getsize(os.path.join(dirpath, filename)) 
                                for dirpath, _, filenames in os.walk(folder_path) 
                                for filename in filenames
                            )
                            progress = (i + (current_size / max(folder_size, 1))) / total_folders * 100
                            self.gui_queue.put(("progress", progress))
                        except:
                            pass
                    
                    # Process GUI events in batches to reduce overhead
                    if i % 5 == 0:
                        self.root.update()
                
                if process.returncode == 0:
                    self.gui_queue.put(("log", f"✓ {folder} backed up\n"))
                    success_count += 1
                    backed_up_files.append(archive_name)  # Add to list of successful backups
                else:
                    self.gui_queue.put(("log", f"✗ {folder} failed (Error code: {process.returncode})\n"))
                    
            except Exception as e:
                self.gui_queue.put(("log", f"⚠ Error: {folder} - {str(e)}\n"))
            
            # Final update for this folder
            self.gui_queue.put(("progress", ((i + 1) / total_folders) * 100))
            self.root.update()

        # Final status with list of backup files
        result_message = f"Backup completed with {success_count}/{total_folders} successes.\n\n"
        result_message += f"Backup location: {backup_dir.replace('\\', '/')}\n\n"
        
        if success_count > 0:
            result_message += "Backup files created:\n"
            result_message += "\n".join(f"• {filename}" for filename in backed_up_files)
            result_message += "\n\n"
        
        # Send email notification
        email_subject = f"Backup Completed: {success_count}/{total_folders} successes"
        self.send_email_notification(email_subject, result_message)
        
        self.gui_queue.put(("log", result_message))
        self.gui_queue.put(("progress", 100))
        self.gui_queue.put(("progress_text", "Completed"))
        self.gui_queue.put(("status", "Backup finished"))
        self.gui_queue.put(("messagebox", f"Backup completed with {success_count}/{total_folders} successes"))
        self.root.update()  # Ensure final updates are processed

    def process_queue(self):
        try:
            while True:
                msg_type, msg = self.gui_queue.get_nowait()
                if msg_type == "log":
                    self.log_text.insert(tk.END, msg)
                    self.log_text.see(tk.END)
                elif msg_type == "progress":
                    self.progress_bar["value"] = msg
                elif msg_type == "progress_text":
                    self.progress_label.config(text=msg)
                elif msg_type == "status":
                    self.status_var.set(msg)
                elif msg_type == "messagebox":
                    messagebox.showinfo("Backup Complete", msg)
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()
