# GreenRoots — Tree Plantation & Monitoring Application

A beginner-friendly Environmental Studies project using:
- HTML for page structure
- CSS for styling
- Python + Flask for the backend
- SQLite for saving tree records
- A little JavaScript for small browser conveniences

## Features
- Overall number of trees recorded
- Healthy trees, trees needing attention, and distinct plantation sites
- Add tree records with tree name, species, planter/person/team, location, planting date, height, health, and notes
- Contributor leaderboard calculated from recorded planter names
- Species summary and tree health percentages
- Search/filter tree records
- Update a tree's health status or delete a record
- Export all records to a CSV spreadsheet
- Data persists in `trees.db` between app restarts

## Requirements
- Python 3.10 or newer recommended
- Visual Studio Code
- VS Code's integrated terminal
- Internet only for the initial Flask installation

## Setup in VS Code (Windows)

1. Extract this project ZIP to a folder, for example `tree_plantation_flask_project`.
2. Open VS Code.
3. Choose **File → Open Folder...** and select the extracted folder.
4. Open **Terminal → New Terminal**.
5. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

6. Activate it in PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt as the terminal and run:

   ```bat
   .venv\Scripts\activate.bat
   ```

7. Install Flask:

   ```powershell
   py -m pip install -r requirements.txt
   ```

8. Start the website:

   ```powershell
   py app.py
   ```

9. Open this address in Chrome or Edge:

   http://127.0.0.1:5000

Keep the terminal running while you use the website. To stop the server, press `Ctrl+C` in the terminal.

## Where is the database?
The application creates `trees.db` in the project folder automatically the first time it runs. It contains the records you add. Keep a backup of this file if the data matters.

## Notes
- No sample trees are inserted automatically. The totals start at zero, so your dashboard reflects the records you enter.
- This is a local starter application for a college project, not a secured public website. Before deploying publicly, add authentication, CSRF protection, stronger validation, and a production server.
- Change `app.secret_key` in `app.py` before sharing/deploying.
