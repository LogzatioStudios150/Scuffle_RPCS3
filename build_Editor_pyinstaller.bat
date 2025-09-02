pyinstaller  --clean --windowed --noconfirm --icon=Data/icon.ico --add-data Data;Data --add-data Config;Config --name SCUFFLE_Editor_RPCS3 GUI_MoveViewer.py
rmdir /S /Q "./dist/SCUFFLE_Editor_RPCS3/Data/Scripts/Custom/"

cd ./dist
del /Q "SCUFFLE_Editor_RPCS3_%1.rar"
"C:\Program Files\WinRAR\winrar.exe" a -r -m5 -af ./SCUFFLE_Editor_RPCS3_%1.rar ./SCUFFLE_Editor_RPCS3
cd ..