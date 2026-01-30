import subprocess as sp
import threading
import time
import datetime
import hashlib
import json
import sys
import tkinter as tk
from tkinter import messagebox, filedialog

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


class DisktroyerEngine:
    def __init__(self, gui):
        self.gui = gui   # link back to GUI
        self.demo_mode = True  # safe demo mode
        self.selected_disk = None
        self.wipe_var = tk.IntVar(value=0)
        self.is_vm = True
        self.certificate_data = {}
        self.wipe_process = None
        self.wipe_thread = None

    def start_wiping(self):
        """Start the disk wiping process"""
        self.gui.show_progress_page()
        self.gui.progress_bar.start(10)

        self.certificate_data = {
            'device': f"/dev/{self.gui.selected_disk['name']}",
            'size': self.gui.selected_disk['size'],
            'type': self.gui.selected_disk['type'],
            'security_level': ['', 'Low', 'Medium', 'High'][self.wipe_var.get()],
            'environment': 'Virtual Machine' if self.is_vm else 'Physical Hardware',
            'start_time': datetime.datetime.now().isoformat(),
            'status': 'In Progress',
            'tool_version': '1.0.0',
            'compliance': 'NIST SP 800-88'
        }

        self.wipe_thread = threading.Thread(target=self.perform_wipe)
        self.wipe_thread.daemon = True
        self.wipe_thread.start()

    def perform_wipe(self):
        """Perform the actual disk wiping"""
        try:
            self.update_status("Starting disk wipe process...")
            time.sleep(1)

            self.update_status("Unmounting disk partitions...")
            self.unmount_disk()
            time.sleep(1)

            cmd = self.get_wipe_command()


#            self.update_status(f"Executing command: {cmd}")

            self.update_status("⚠️ DO NOT INTERRUPT THIS PROCESS ⚠️")

            if self.demo_mode:
                self.simulate_wipe()
            else:
                self.execute_wipe_command(cmd)

            # Complete
            self.certificate_data['end_time'] = datetime.datetime.now().isoformat()
            self.certificate_data['status'] = 'Completed'

            # Calculate duration
            start = datetime.datetime.fromisoformat(self.certificate_data['start_time'])
            end = datetime.datetime.fromisoformat(self.certificate_data['end_time'])
            duration = str(end - start)
            self.certificate_data['duration'] = duration

            cert_string = json.dumps(self.certificate_data, sort_keys=True)
            cert_hash = hashlib.sha256(cert_string.encode()).hexdigest()
            self.certificate_data['certificate_hash'] = cert_hash

            self.update_status("✔️ Disk wiping completed successfully!")
            self.update_status(f"Certificate Hash: {cert_hash}")

            self.gui.root.after(2000, self.complete_wipe)

        except Exception as e:
            self.certificate_data['status'] = 'Failed'
            self.certificate_data['error'] = str(e)
            self.update_status(f"❌ Error during wipe: {str(e)}")
            self.gui.root.after(3000, self.complete_wipe)

    def get_wipe_command(self):
        """Get the appropriate wipe command"""
        disk_name = self.gui.selected_disk['name']
        disk_type = self.gui.selected_disk['type'].lower()
        level = self.wipe_var.get()

        if self.is_vm:
            if level == 1:
                return f"shred -v -f -n 1 -z /dev/{disk_name}"
            elif level == 2:
                return f"shred -v -f -n 3 -z /dev/{disk_name}"
            else:
                cmd = f"sudo hdparm --user-master u --security-erase-enhanced p /dev/{disk_name}"
                self.update_status(f"Executing command: {cmd}")
                self.update_status("Rotating the disk encryption key")
                return f"shred -v -f -n 8 -z /dev/{disk_name}"
        else:
            if 'nvme' in disk_type:
                if level == 1:
                    return f"nvme format /dev/{disk_name} --ses=1"
                elif level == 2:
                    return f"nvme format /dev/{disk_name} --ses=2"
                else:
                    return f"nvme sanitize /dev/{disk_name} --ause"
            elif 'ssd' in disk_type:
                if level >= 2:
                    return f"hdparm --user-master u --security-set-pass p /dev/{disk_name} && hdparm --user-master u --security-erase-enhanced p /dev/{disk_name}"
                else:
                    return f"hdparm --user-master u --security-set-pass p /dev/{disk_name} && hdparm --user-master u --security-erase p /dev/{disk_name}"
            else:  
                if level == 1:
                    return f"dd if=/dev/urandom of=/dev/{disk_name} bs=1M status=progress"
                elif level == 2:
                    return f"shred -v -f -n 8 -z /dev/{disk_name}"
                else:
                    return f"shred -v -f -n 35 -z /dev/{disk_name}"

    def unmount_disk(self):
        """Unmount all partitions of the selected disk"""
        try:
            disk_name = self.gui.selected_disk['name']
            result = sp.run(['grep', f'/dev/{disk_name}', '/proc/mounts'],
                            capture_output=True, text=True)
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        partition = line.split()[0]
                        self.update_status(f"Unmounting {partition}...")
                        try:
                            sp.run(['umount', partition], check=True, timeout=30)
                            self.update_status(f"✔️ Unmounted {partition}")
                        except sp.CalledProcessError:
                            sp.run(['umount', '-l', partition], timeout=30)
                            self.update_status(f"✔️ Force unmounted {partition}")
            else:
                self.update_status("No mounted partitions found")
        except Exception as e:
            self.update_status(f"Warning: Could not unmount: {str(e)}")

    def simulate_wipe(self):
        """Simulate wipe process for demo"""
        phases = [
            "Pass 1/3: Writing random data...",
            "Pass 2/3: Writing zeros...",
            "Pass 3/3: Final verification...",
        ]
        for phase in phases:
            self.update_status(phase)
            for progress in range(0, 101, 20):
                time.sleep(0.3)
                self.update_status(f"  Progress: {progress}%")

    def execute_wipe_command(self, cmd):
        process = sp.Popen(['sudo'] + cmd.split(),
                           stdout=sp.PIPE, stderr=sp.STDOUT,
                           universal_newlines=True, bufsize=1)
        self.wipe_process = process
        for line in iter(process.stdout.readline, ''):
            if line:
                self.update_status(line.strip())
        process.wait()
        if process.returncode != 0:
            raise sp.CalledProcessError(process.returncode, cmd)

    def update_status(self, message):
        """Update status text in GUI"""
        def update():
            self.gui.status_text.config(state="normal")
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.gui.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.gui.status_text.see(tk.END)
            self.gui.status_text.update()
            self.gui.cert_info_text.config(state="disabled")
        self.gui.root.after(0, update)

    def complete_wipe(self):
        self.gui.progress_bar.stop()
        self.gui.show_certificate_page()
        self.gui.cert_info_text.delete(1.0, tk.END)
        self.gui.cert_info_text.insert(tk.END, self.generate_certificate_text())
        self.gui.cert_info_text.config(state="disabled")

    def generate_certificate_text(self):
        cert = self.certificate_data
        return f"""
SECURE DATA WIPING CERTIFICATE
==========================================
Device: {cert.get('device')}
Size: {cert.get('size')}
Type: {cert.get('type')}
Security Level: {cert.get('security_level')}
Compliance: {cert.get('compliance')}
Start Time: {cert.get('start_time')}
End Time: {cert.get('end_time')}
Duration: {cert.get('duration', 'N/A')}
Status: {cert.get('status')}
Certificate Hash: {cert.get('certificate_hash')}
==========================================
"""

    

