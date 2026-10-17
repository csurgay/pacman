@echo off
rem Starts a small local web server in this folder and opens the game.
rem Needed so the page can read pacman-speeds.yaml and ghost-fsm.yaml
rem (browsers do not let a page opened as a file read other files).
cd /d "%~dp0"
start "" cmd /c "timeout /t 2 >/dev/null & start http://localhost:8000/pacman.html"
where py >/dev/null 2>/dev/null && (py -m http.server 8000 & goto :eof)
where python >/dev/null 2>/dev/null && (python -m http.server 8000 & goto :eof)
echo Python was not found. Install Python, or serve this folder with any local web server.
pause
