import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import subprocess as sp
from GUI_backend import DisktroyerEngine


def create_rounded_button(parent, text, command, min_width_chars, height, font_size, radius=10, fill_color="#337AB7", text_color="white"):
    """Creates a custom button with rounded corners using Canvas."""
    frame = tk.Frame(parent)
    
    text_width_factor = 10 
    button_width = min_width_chars * text_width_factor + 35 
    button_height = height * font_size + 20 

    canvas = tk.Canvas(frame, width=button_width, height=button_height, bd=0, highlightthickness=0)
    canvas.pack(side="left")

    def round_rectangle(x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    rect = round_rectangle(2, 2, button_width - 2, button_height - 2, radius, outline=fill_color, fill=fill_color)
    
    text_item = canvas.create_text(button_width // 2, button_height // 2, 
                                   text=text, fill=text_color, 
                                   font=("Arial", font_size, "bold"))
    
    def on_click(event):
        command()
        
    def on_enter(event):
        canvas.itemconfig(rect, fill="#4A8FCE")
        
    def on_leave(event):
        canvas.itemconfig(rect, fill=fill_color)

    canvas.tag_bind(rect, '<Button-1>', on_click)
    canvas.tag_bind(text_item, '<Button-1>', on_click)
    canvas.tag_bind(rect, '<Enter>', on_enter)
    canvas.tag_bind(text_item, '<Enter>', on_enter)
    canvas.tag_bind(rect, '<Leave>', on_leave)
    canvas.tag_bind(text_item, '<Leave>', on_leave)
    
    return frame


def list_disks():
    op = sp.run(["lsblk", "-dno", "name,size,tran,type"], capture_output=True)
    fop = sp.run(["grep", "disk"], input=op.stdout, capture_output=True).stdout
    sop = fop.split()
    disks = []
    temp = []
    for i in sop:
        temp.append(i.decode())
        if i.decode() == "disk":
            temp.append(i.decode())
            disks.append((temp[0], temp[1], temp[2], temp[3]))
            temp = []
    return disks


def get_disk_details(disk_name):
    """Get additional disk details using various system commands"""
    details = {}
    
    try:
        result = sp.run(["lsblk", "-dno", "model,serial", f"/dev/{disk_name}"], 
                       capture_output=True, text=True)
        if result.returncode == 0:
            parts = result.stdout.strip().split()
            details['model'] = parts[0] if len(parts) > 0 else "Unknown"
            details['serial'] = parts[1] if len(parts) > 1 else "Unknown"
        
        result = sp.run(["lsblk", "-no", "fstype", f"/dev/{disk_name}1"], 
                       capture_output=True, text=True)
        details['filesystem'] = result.stdout.strip() if result.returncode == 0 else "Unknown"
        
        result = sp.run(["lsblk", "-no", "name", f"/dev/{disk_name}"], 
                       capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            details['partitions'] = len(lines) - 1  # Subtract 1 for the disk itself
        else:
            details['partitions'] = 0
            
        result = sp.run(["findmnt", "-rno", "target", f"/dev/{disk_name}1"], 
                       capture_output=True, text=True)
        details['mounted'] = "Yes" if result.returncode == 0 else "No"
        details['mount_point'] = result.stdout.strip() if result.returncode == 0 else "None"
            
    except Exception as e:
        details.setdefault('model', 'Unknown')
        details.setdefault('serial', 'Unknown')
        details.setdefault('filesystem', 'Unknown')
        details.setdefault('partitions', 0)
        details.setdefault('mounted', 'Unknown')
        details.setdefault('mount_point', 'None')
    
    return details


def detect_drive_type(tran):
    if tran is None:
        return "HDD"
    tran = tran.lower()
    if "nvme" in tran or "ssd" in tran:
        return "SSD"
    if "sata" in tran or "ata" in tran:
        return "HDD"
    return "HDD"


class DisktroyerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Disktroyer")
        self.root.attributes("-fullscreen", True)

        self.selected_disk = None
        self.engine = DisktroyerEngine(self)

        self.logo_photo = ImageTk.PhotoImage(Image.open("img/Disk_WIPE.png").resize((120, 120)))
        self.hdd_photo = ImageTk.PhotoImage(Image.open("img/HDD.png").resize((100, 100)))
        self.ssd_photo = ImageTk.PhotoImage(Image.open("img/SSD.png").resize((100, 100)))
        self.shutdown = ImageTk.PhotoImage(Image.open("img/shutdown.png").resize((100,100)))
        self.restart = ImageTk.PhotoImage(Image.open("img/restart.png").resize((100,100)))

        self.build_welcome_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def add_logo(self):
        logo_frame = tk.Frame(self.root)
        logo_label = tk.Label(logo_frame, image=self.logo_photo)
        logo_label.pack()
        logo_frame.pack(side="top", pady=30) 

    
    
    def build_welcome_screen(self):
        self.clear_screen()
        self.add_logo()

        tk.Label(self.root, text="Welcome to Disktroyer", font=("Arial", 28, "bold")).pack(pady=15) 
        tk.Label(self.root, text="Select your disk", font=("Arial", 20, "bold")).pack(pady=10) 

        disks = list_disks()

        frame_disk = tk.Frame(self.root)
        frame_disk.pack(pady=50) 

        for disk in disks:
            drive_type = detect_drive_type(disk[2])
            icon = self.ssd_photo if drive_type == "SSD" else self.hdd_photo

            disk_frame = tk.Frame(frame_disk, bd=3, relief="groove", padx=20, pady=20) 
            disk_frame.pack(side="left", padx=40) 

            tk.Label(disk_frame, image=icon).pack()
            tk.Label(disk_frame, text=f"{disk[0]} - {disk[1]} ({drive_type})",
                     font=("Arial", 16)).pack(pady=10) 

            btn_frame = create_rounded_button(disk_frame, text="Select", 
                                                command=lambda d=disk: self.select_disk(d), 
                                                min_width_chars=8, height=1, font_size=14, fill_color="#4CAF50") # Custom button
            btn_frame.pack(pady=10)
        

    def select_disk(self, disk):
        disk_details = get_disk_details(disk[0])
        
        self.selected_disk = {
            "name": disk[0], 
            "size": disk[1], 
            "type": detect_drive_type(disk[2]),
            "transport": disk[2] if disk[2] else "Unknown",
            "model": disk_details.get('model', 'Unknown'),
            "serial": disk_details.get('serial', 'Unknown'),
            "filesystem": disk_details.get('filesystem', 'Unknown'),
            "partitions": disk_details.get('partitions', 0),
            "mounted": disk_details.get('mounted', 'Unknown'),
            "mount_point": disk_details.get('mount_point', 'None'),
        }
        self.build_level_screen()

    def build_level_screen(self):
        self.clear_screen()
        self.add_logo()

        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=30, padx=60, fill="both", expand=True) 

        details_frame = tk.LabelFrame(main_frame, text="Selected Disk Details", 
                                    font=("Arial", 20, "bold"), padx=30, pady=30) 
        details_frame.pack(side="right", fill="both", expand=True, padx=(25, 0)) 

        icon_frame = tk.Frame(details_frame)
        icon_frame.pack(pady=(0, 30)) 
        
        icon = self.ssd_photo if self.selected_disk['type'] == "SSD" else self.hdd_photo
        tk.Label(icon_frame, image=icon).pack(side="left", padx=(0, 25)) 
        
        basic_info_frame = tk.Frame(icon_frame)
        basic_info_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(basic_info_frame, text=f"/dev/{self.selected_disk['name']}", 
                font=("Arial", 22, "bold")).pack(anchor="w") # Increased font
        tk.Label(basic_info_frame, text=f"Size: {self.selected_disk['size']}", 
                font=("Arial", 16)).pack(anchor="w") # Increased font
        tk.Label(basic_info_frame, text=f"Type: {self.selected_disk['type']}", 
                font=("Arial", 16)).pack(anchor="w") # Increased font

        details_container = tk.Frame(details_frame)
        details_container.pack(fill="both", expand=True)

        disk_info_frame = tk.LabelFrame(details_container, text="Disk Information", 
                                       font=("Arial", 14, "bold"), padx=15, pady=10) # Increased font/padding
        disk_info_frame.pack(fill="x", pady=(0, 15)) # Increased padding

        disk_info_items = [
            ("Device Path:", f"/dev/{self.selected_disk['name']}"),
            ("Disk Size:", self.selected_disk['size']),
            ("Drive Type:", self.selected_disk['type']),
            ("Transport:", self.selected_disk['transport']),
            ("Model:", self.selected_disk['model']),
            ("Serial Number:", self.selected_disk['serial'])
        ]

        for i, (label, value) in enumerate(disk_info_items):
            tk.Label(disk_info_frame, text=label, font=("Arial", 12, "bold"), 
                    anchor="w").grid(row=i, column=0, sticky="w", padx=(0, 15), pady=3) # Increased font/padding
            tk.Label(disk_info_frame, text=value, font=("Arial", 12), 
                    anchor="w", fg="navy").grid(row=i, column=1, sticky="w", pady=3) # Increased font/padding

        partition_info_frame = tk.LabelFrame(details_container, text="Partition Information", 
                                           font=("Arial", 14, "bold"), padx=15, pady=10) # Increased font/padding
        partition_info_frame.pack(fill="x", pady=(0, 15)) # Increased padding

        partition_info_items = [
            ("Partitions:", str(self.selected_disk['partitions'])),
            ("Filesystem:", self.selected_disk['filesystem']),
            ("Mounted:", self.selected_disk['mounted']),
            ("Mount Point:", self.selected_disk['mount_point'])
        ]

        for i, (label, value) in enumerate(partition_info_items):
            tk.Label(partition_info_frame, text=label, font=("Arial", 12, "bold"), 
                    anchor="w").grid(row=i, column=0, sticky="w", padx=(0, 15), pady=3) # Increased font/padding
            color = "red" if value == "Yes" and label == "Mounted:" else "green" if value == "No" and label == "Mounted:" else "navy"
            tk.Label(partition_info_frame, text=value, font=("Arial", 12), 
                    anchor="w", fg=color).grid(row=i, column=1, sticky="w", pady=3) # Increased font/padding


        warning_frame = tk.LabelFrame(details_container, text="⚠️ Security Notice", 
                                     font=("Arial", 14, "bold"), padx=15, pady=10, fg="red") # Increased font/padding
        warning_frame.pack(fill="x", pady=(0, 10)) # Increased padding

        warning_text = tk.Label(warning_frame, 
                               text="WARNING: This operation will permanently delete ALL data on this disk!\n\n"
                                   "✓ Ensure you have backups of important data\n"
                                   "✓ Verify this is the correct disk\n"
                                   "✓ Unmount any mounted partitions", 
                               font=("Arial", 12), justify="left", fg="red") # Increased font
        warning_text.pack(anchor="w")

        level_frame = tk.LabelFrame(main_frame, text="Choose Data Erasure Level", 
                                  font=("Arial", 20, "bold"), padx=30, pady=30) # Increased font/padding
        level_frame.pack(side="left", fill="both", expand=True, padx=(0, 25)) # Moved to left

        level_descriptions = {
            1: ("Low Level (Fast)", "Single pass with random data\nSuitable for: Non-sensitive data"),
            2: ("Medium Level (Moderate)", "Multiple passes with different patterns\nSuitable for: Business data"),
            3: ("High Level (Slow)", "Military-grade multiple passes\nSuitable for: Classified data")
        }

        def start(level):
            if self.selected_disk['mounted'] == "Yes":
                result = messagebox.askyesno(
                    "Disk Mounted", 
                    f"The selected disk is currently mounted at {self.selected_disk['mount_point']}.\n\n"
                    "The system will attempt to unmount it automatically.\n\n"
                    "Do you want to continue?"
                )
                if not result:
                    return
            
            result = messagebox.askyesno(
                "Final Confirmation", 
                f"Are you absolutely sure you want to wipe:\n\n"
                f"Device: /dev/{self.selected_disk['name']}\n"
                f"Size: {self.selected_disk['size']}\n"
                f"Model: {self.selected_disk['model']}\n\n"
                f"Security Level: {level_descriptions[level][0]}\n\n"
                f"THIS ACTION CANNOT BE UNDONE!"
            )
            if result:
                self.engine.wipe_var.set(level)
                self.engine.start_wiping()

        for level, (title, description) in level_descriptions.items():
            level_box_frame = tk.Frame(level_frame, bd=2, relief="groove", 
                                       padx=15, pady=15, bg="#F0F0F0") 
            level_box_frame.pack(fill="x", pady=15) 
            
            button_frame = tk.Frame(level_box_frame, bg="#F0F0F0")
            button_frame.pack(fill="x")
            
            level_btn_frame = create_rounded_button(button_frame, text=title.split(" (")[0], # Use only the main title
                                command=lambda l=level: start(l), 
                                min_width_chars=12, height=1, font_size=16, # Increased min_width_chars
                                fill_color=["#4CAF50", "#FF9800", "#F44336"][level-1]) # Color coded buttons
            level_btn_frame.pack(side="left", padx=(0, 20)) # Increased padding
            
            desc_label = tk.Label(button_frame, text=description, 
                                font=("Arial", 12), justify="left", bg="#F0F0F0") # Increased font, set background
            desc_label.pack(side="left", fill="both", expand=True)

        back_frame = tk.Frame(level_frame)
        back_frame.pack(fill="x", pady=(30, 0)) # Increased padding
        create_rounded_button(back_frame, text="← Back to Disk Selection", 
                             command=self.build_welcome_screen, 
                             min_width_chars=18, height=1, font_size=12, fill_color="#607D8B").pack(side="left")

    def show_progress_page(self):
        self.clear_screen()
        self.add_logo()
        tk.Label(self.root, text="Wiping in progress...", font=("Arial", 28, "bold")).pack(pady=30) # Increased font
        self.status_text = tk.Text(self.root, height=18, width=90, font=("Courier", 12)) # Increased size/font
        self.status_text.pack(pady=20)
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=600, mode="indeterminate") # Increased length
        self.progress_bar.pack(pady=20)

    def show_certificate_page(self):
        self.clear_screen()
        self.add_logo()
        tk.Label(self.root, text="Certificate of Erasure", font=("Arial", 28, "bold")).pack(pady=30) # Increased font
        self.cert_info_text = tk.Text(self.root, height=25, width=90, font=("Courier", 12)) # Increased size/font
        self.cert_info_text.pack(pady=20)

        


if __name__ == "__main__":
    root = tk.Tk()
    app = DisktroyerApp(root)
    root.mainloop()
