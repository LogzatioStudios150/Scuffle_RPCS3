del /Q ."./dist/SCUFFLE_Editor_RPCS3_%1.rar"
rmdir /S /Q "./dist/SCUFFLE_Editor_RPCS3" 
uv run nuitka --standalone --enable-plugin=tk-inter ./GUI_MoveViewer.py --output-dir=./dist --output-filename=SCUFFLE_Editor_RPCS3 --remove-output --windows-console-mode=disable --windows-icon-from-ico=.\Data\icon.ico --product-name=SCUFFLE_Editor_RPCS3 --file-version=%1 --product-version=%1 --include-data-dir=./Config=Config --include-data-dir=./Data=Data 
move "./dist/GUI_MoveViewer.dist" "./dist/SCUFFLE_Editor_RPCS3"
rmdir /S /Q "./dist/SCUFFLE_Editor_RPCS3/Data/Scripts/Custom/"

cd ./dist
"C:\Program Files\WinRAR\winrar.exe" a -r -af ./SCUFFLE_Editor_RPCS3_%1.rar ./SCUFFLE_Editor_RPCS3/
cd ..