pyinstaller --clean --noconfirm --onedir --windowed --icon "./appicon.ico" --add-data "./theme;theme/" --add-data "./resources;resources/" --add-data "./configs;configs/"  "./app.py"