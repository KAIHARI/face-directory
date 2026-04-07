@echo off
REM ============================================================
REM Face Directory — Deploy
REM ============================================================
REM Double-click this file to publish the current index.html
REM and face files to GitHub Pages.
REM
REM This runs: python run.py deploy
REM Which runs: git add -A && git commit && git push
REM ============================================================

REM Switch to the directory containing this script
cd /d "%~dp0"

REM Run the deploy subcommand
python run.py deploy

REM Pause so the window stays open and you can read the result
echo.
echo Press any key to close this window...
pause >nul
