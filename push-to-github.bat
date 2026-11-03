@echo off
setlocal
cd /d "%~dp0"
echo ==================================================
echo   comfyui-molab  -  push to GitHub
echo ==================================================
echo.
echo Repo: https://github.com/Nu1lp0inteR/comfyui-molab
echo.
echo A browser window will pop up asking you to sign in to GitHub.
echo Make sure you sign in as  Nu1lp0inteR  (digit 1 and zero, not letters).
echo.
pause

echo.
echo Pushing...
echo.
git -c credential.helper=manager push -u origin main
if errorlevel 1 goto :failed

echo.
echo Done. Open the notebook in molab with:
echo.
echo   https://molab.marimo.io/github/Nu1lp0inteR/comfyui-molab/blob/main/comfyui_molab.py
echo.
pause
exit /b 0

:failed
echo.
echo Push failed. What to do:
echo   1. If the login window never appeared, run this once in this folder:
echo        git credential-manager github login
echo   2. Then run this script again.
echo   3. If it says "Authentication failed" but you did log in, open
echo      Windows Credential Manager and delete any entry named
echo      "git:https://github.com", then run this script again.
echo.
pause
exit /b 1
