# SCUFFLE
A version of [SCUFFLE](https://github.com/FottenSC/Scuffle/releases/) compatible with Soul Calibur 4 and Soul Calibur 5 through RPCS3 -- based on the useful parts of the popular Tekken Bot Prime, it shows you frame data while you're playing the game so you don't have to alt-tab to a wiki or a google doc or a paste bin or yell at your twitch chat or <character> discord. Some of the frame data is even correct.


# Usage

Download the latest release from https://github.com/LogzatioStudios150/Scuffle_RPCS3/releases/. Run the .exe at the same as Soul Calibur 6 (PC version only) and it will read the memory to display internal frame data. The frame data overlay should display at the top of the screen, works only in windowed or windowed borderless mode (NO FULLSCREEN).

# Technical

SCUFFLE uses python 3.9 and strives to use only Standard Library modules so it should run with any 64-bit python 3.9. 32-bit Python (the default if you use the installer) probably won't work.

To build the project, make sure you have python 3.5 and pyinstaller and run the the project_build.bat file.

# I want to know more!

Check out https://www.youtube.com/watch?v=GjB-MRonAFc or read [How the Movelist is Parsed](__HowTheMovelistBytesWork.md)
  

# Credits
Rougelite is the gigachad who originally made scuffle and thanks to Unicorn_cz for all the help :)
  
(https://www.youtube.com/user/Roguelike)
