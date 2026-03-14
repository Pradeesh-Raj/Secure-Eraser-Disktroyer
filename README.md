# Disktroyer

## Introduction

**Disktroyer** is a secure disk erasure tool designed to permanently wipe data from storage devices.  
When a file is deleted normally, the operating system only removes references to it, leaving the actual data still recoverable with forensic tools. Disktroyer solves this problem by **securely overwriting the storage medium**, ensuring that previously stored information cannot be recovered.

The project was built as a proof-of-concept secure erasure system with a graphical interface that allows users to identify storage devices, choose a wiping strategy, and monitor the progress of the wiping process.

Disktroyer is designed with simplicity and transparency in mind so that users can confidently sanitize storage devices before disposal, reuse, or transfer.

---

### Key Capabilities

- **Disk Detection**
  - Identifies available storage devices connected to the system
  - Displays device name, size, and type

- **Disk Type Identification**
  - Distinguishes between **HDD** and **SSD/NVMe** devices
  - Allows appropriate wiping strategies depending on the device type

- **Secure Data Erasure**
  - Overwrites the disk with configurable wiping passes
  - Prevents recovery of deleted data through standard recovery tools

- **Multiple Security Levels**
  - **Low Priority** – Single overwrite pass (fast)
  - **Medium Priority** – Multiple overwrite passes
  - **High Priority** – Maximum overwrite passes for stronger sanitization

- **Real-time Status Monitoring**
  - Displays the wiping progress and logs operations in the GUI

- **Certificate Generation**
  - Generates a certificate showing that the wiping process was completed successfully
  - Includes disk information, wipe level, and timestamps

---

## Technical Stack

Disktroyer is built using the following technologies:

### Programming Language
- Python 3

### GUI Framework
- Tkinter

### Image Handling
- Pillow (PIL)

### System Utilities
- Linux disk utilities such as:
  - `dd`
  - `shred`
  - `lsblk`

### PDF Generation
- ReportLab

### QR Code Generation
- qrcode (Python library)

### System Interaction
- Python `subprocess` module

---

## How to Run Disktroyer

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/disktroyer.git
cd disktroyer
```
### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install pillow qrcode reportlab PyPDF2
```
### 4. Run the Application
```bash
python disktroyer_gui.py
```
