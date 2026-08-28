@echo off
set GIT="C:\Program Files\Git\cmd\git.exe"
set DIR="C:\Users\Admin\OneDrive\Desktop\ECOSORT_AI"

echo === Git Status ===
%GIT% -C %DIR% status

echo.
echo === Staging all files ===
%GIT% -C %DIR% add .

echo.
echo === Committing ===
%GIT% -C %DIR% commit -m "Initial commit: EcoSort AI project"

echo.
echo === Setting branch to main ===
%GIT% -C %DIR% branch -M main

echo.
echo === Pushing to GitHub ===
%GIT% -C %DIR% push -u origin main

echo.
echo === Done ===
pause
