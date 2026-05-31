@echo off

echo Stopping PostgreSQL...
net stop postgresql-x64-17

echo.
echo Starting PostgreSQL...
net start postgresql-x64-17

echo.
pause