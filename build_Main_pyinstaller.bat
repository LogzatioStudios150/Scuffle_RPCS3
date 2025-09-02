pyinstaller  --clean --windowed --noconfirm --icon=Data/icon.ico --add-data Data;Data --add-data Config;Config --name SCUFFLE_RPCS3 GUI_Main.py
rmdir /S /Q "./dist/SCUFFLE_RPCS3/Data/Scripts/Custom/"

cd ./dist
del /Q "SCUFFLE_RPCS3_%1.rar"
"C:\Program Files\WinRAR\winrar.exe" a -r -m5 -af ./SCUFFLE_RPCS3_%1.rar ./SCUFFLE_RPCS3
cd ..