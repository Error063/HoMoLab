@echo off
pyinstaller --clean --noconfirm --onedir --windowed --icon "./homo/appicon.ico" --add-data "./theme;theme/" --add-data "./homo/resources;resources/" -n "app" "./homo/homolab/__main__.py"