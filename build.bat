@echo off
pyinstaller --clean --noconfirm --onedir --windowed --icon "./appicon.ico" --add-data "./theme;theme/" --add-data "./resources;resources/"  "./app.py"