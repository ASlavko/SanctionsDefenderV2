@echo off
echo ===================================================
echo SanctionDefenderV2 Automated Git Backup
echo ===================================================
echo.

:: Get current date and time for the commit message
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set mydate=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%
set mytime=%datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2%

set commit_msg=Automated backup on %mydate% at %mytime%

echo Adding all changes to Git...
git add .
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to add files to Git.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Committing changes with message: "%commit_msg%"...
git commit -m "%commit_msg%"
if %ERRORLEVEL% neq 0 (
    echo [INFO] No changes to commit or commit failed.
) else (
    echo [SUCCESS] Changes committed locally.
    
    echo.
    echo Pushing to GitHub...
    git push origin main
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to push to GitHub. Check your connection or permissions.
    ) else (
        echo [SUCCESS] Backup pushed to GitHub successfully!
    )
)

echo.
echo Backup process complete.
pause
