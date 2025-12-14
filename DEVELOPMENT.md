# SanctionDefenderApp Development Guide

## Quick Start

### 1. Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Run Tests

```powershell
.\venv\Scripts\python.exe test_local.py
```

### 3. Common Commands

| Command                                     | Purpose                     |
| ------------------------------------------- | --------------------------- |
| `python -m pytest`                          | Run all tests               |
| `pip install -r functions/requirements.txt` | Install/update dependencies |
| `firebase deploy`                           | Deploy to Firebase          |
| `firebase deploy --only functions`          | Deploy only cloud functions |

## Project Structure

```
SanctionDefenderApp/
├── functions/
│   ├── main.py              # Cloud function code
│   ├── requirements.txt      # Python dependencies
│   └── lib/                  # Installed packages (auto-generated)
├── public/                   # Frontend (HTML/CSS/JS)
├── firebase.json             # Firebase configuration
├── firestore.rules           # Firestore security rules
├── storage.rules             # Cloud Storage rules
└── venv/                     # Python virtual environment
```

## Function Overview

### download_sanctions_lists()

- **Purpose**: Downloads sanctions lists from EU, UK, and US sources
- **Schedule**: Runs every 24 hours (via Cloud Scheduler)
- **Downloads**:
  - EU sanctions list (~24 MB)
  - UK sanctions list (~19 MB)
  - US SDN list (~3.5 MB)
  - US Non-SDN list (~104 MB)

**Next Steps**: Parse XML and store in Firestore

## Environment Info

- **Python**: 3.14.0
- **Firebase CLI**: 14.27.0
- **Node.js**: v24.11.1
