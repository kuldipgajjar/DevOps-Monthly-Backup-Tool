# DevOps-Monthly-Backup-Tool
A powerful GUI application for creating monthly backups of folders using WinRAR, with email notification capabilities.

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

### Option 2: Run from Source
```bash
git clone https://github.com/kuldipgajjar/DevOps-Monthly-Backup-Tool/backuptool.git
cd backuptool
pip install -r requirements.txt
python backuptool.py
