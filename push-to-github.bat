@echo off
setlocal
cd /d "%~dp0"
echo ==================================================
echo   comfyui-molab  -  push to GitHub
echo ==================================================
echo.
echo Step 1: create the repo on GitHub
echo   Opening https://github.com/new?name=comfyui-molab ...
echo.
start "" "https://github.com/new?name=comfyui-molab"
echo   Check these three things on the page:
echo     - Repository name : comfyui-molab
echo     - Visibility      : Public
echo     - "Add a README file" must stay UNCHECKED
echo.
echo   Click "Create repository", then come back here.
echo.
pause

echo.
echo Step 2: pushing (a browser window will pop up for GitHub login)
echo.
git -c credential.helper=manager push -u origin main
if errorlevel 1 goto :failed

echo.
echo Step 3: done. Open the notebook in molab:
echo.
echo   https://molab.marimo.io/github/NullPointeR/comfyui-molab/blob/main/comfyui_molab.py
echo.
echo Copy that link into your browser.
echo.
pause
exit /b 0

:failed
echo.
echo Push failed.
echo   404 / repository not found  -^> the repo was not created yet, or the name differs
echo   Authentication failed       -^> finish the GitHub login window, then run this again
echo.
echo If the login window never appears, run this once in the same folder:
echo   git credential-manager github login
echo.
pause
exit /b 1
