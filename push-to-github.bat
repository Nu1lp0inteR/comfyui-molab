@echo off
setlocal
cd /d "%~dp0"
echo ==================================================
echo   comfyui-molab  -  publish and push
echo ==================================================
echo.
echo Step 1: make sure the repo is PUBLIC
echo   Opening https://github.com/NullPointeR/comfyui-molab/settings ...
echo.
start "" "https://github.com/NullPointeR/comfyui-molab/settings"
echo   Scroll to the bottom, find "Danger Zone":
echo     Change repository visibility  -^>  Make public
echo   If it is already public, just skip this step.
echo.
echo   (molab cannot read private repos, so public is required.)
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
echo   repository not found  -^> check the repo name at github.com/NullPointeR?tab=repositories
echo   Authentication failed -^> finish the GitHub login window, then run this again
echo.
echo If the login window never appears, run this once in the same folder:
echo   git credential-manager github login
echo.
pause
exit /b 1
