# DevOps-Monthly-Backup-Tool
A powerful GUI application for creating monthly backups of folders using WinRAR, with email notification capabilities.

## Features

- 📂 Select multiple folders for backup
- 🗄️ Create compressed RAR archives
- 📧 Email notifications with backup status
- 📊 Progress tracking with visual indicators
- ⚙️ Configurable email settings
- 🕒 Automatic timestamped backup folders
- 🖥️ Modern dark/light theme support

## Prerequisites

- Windows OS (tested on Windows 10/11)
- Python 3.8+ (if running from source)
- [WinRAR](https://www.win-rar.com/) installed (default path: `C:\Program Files\WinRAR\WinRAR.exe`)
- SMTP email credentials for notifications (optional)

## Installation

### Option 1: Download Pre-built EXE
1. Download the latest release from the [Releases page](https://github.com/kuldipgajjar/DevOps-Monthly-Backup-Tool/releases)
2. Run `Backup_Tool.exe`

## Usage Guide

1. **Configure WinRAR Path**:
   - Click the `...` button to locate WinRAR.exe if not in default location

2. **Select Folders**:
   - Set Source folder containing items to backup
   - Set Destination folder for backup archives
   - Click "Load" to see available folders
   - Select folders to backup (or "All" to select all)

3. **Email Settings (Optional)**:
   - Click the ⚙️ icon
   - Enter SMTP server details (e.g., smtp.gmail.com)
   - Set port (587 for TLS)
   - Enter sender email and password
   - Set recipient email
   - Click "Save Settings"

4. **Run Backup**:
   - Click "Backup" to start the process
   - Progress will be shown in real-time
   - Email notification will be sent upon completion

## Email Notification Format

You'll receive emails with this format:

```
Subject: Backup Completed: 5/5 successes

DevOps Backup Notification

Backup completed with 5/5 successes.

Backup location: D:/Backups/Backup_2025-03-31_15-38-22

Backup files created:
• Project1.rar
• Project2.rar
• Database.rar
• Configs.rar
• Documents.rar

Backup completed at: 2025-03-31 15:38:22
```

## Configuration

Settings are saved in `backup_config.json`:
```json
{
    "smtp_server": "smtp.gmail.com",
    "smtp_port": "587",
    "email_address": "your.email@gmail.com",
    "email_password": "yourpassword",
    "recipient_email": "recipient@example.com"
}
```

## Building from Source

To build the EXE yourself:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=app.ico backuptool.py
```

## Troubleshooting

**Problem**: Email not sending  
**Solution**: 
- Verify SMTP settings (use app passwords for Gmail)
- Check firewall isn't blocking SMTP traffic

**Problem**: WinRAR not found  
**Solution**: 
- Install WinRAR or provide correct path
- Default path: `C:\Program Files\WinRAR\WinRAR.exe`

**Problem**: Backup fails  
**Solution**:
- Check source folders exist
- Ensure destination has enough space
- Verify no files are locked/in use
