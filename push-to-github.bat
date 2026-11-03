@echo off
setlocal
cd /d "%~dp0"
echo ==================================================
echo   comfyui-molab  -  push to GitHub
echo ==================================================
echo.
echo [1/3] Opening https://github.com/new in your browser...
start "" https://github.com/new
echo.
echo   Repository name : comfyui-molab
echo   Visibility      : Public
echo   Do NOT check "Add a README file"
echo.
echo Create the repo first, then come back here.
pause

set /p GHUSER=Your GitHub username: 
if "%GHUSER%"=="" goto :nouser

set "REPOURL=https://github.com/%GHUSER%/comfyui-molab.git"
echo.
echo [2/3] Pushing to %REPOURL%
git remote remove origin >nul 2>&1
git remote add origin "%REPOURL%"
git push -u origin main
if errorlevel 1 goto :failed

echo.
echo [3/3] Done. Open the notebook in molab with:
echo.
echo   https://molab.marimo.io/github/%GHUSER%/comfyui-molab/blob/main/comfyui_molab.py
echo.
pause
exit /b 0

:nouser
echo.
echo Username is required. Nothing was changed.
pause
exit /b 1

:failed
echo.
echo Push failed.
echo   - Make sure the repo exists and is named exactly "comfyui-molab"
echo   - If a login window appeared, finish signing in to GitHub, then run this again
echo.
pause
exit /b 1
