@echo off
echo Creating migrations for challenges...
"D:/Django jemit/venv/Scripts/python.exe" manage.py makemigrations challenges

echo Running migrations...
"D:/Django jemit/venv/Scripts/python.exe" manage.py migrate

echo Creating initial challenge data...
"D:/Django jemit/venv/Scripts/python.exe" manage.py create_challenges

echo Done! You can now access:
echo - Challenges: http://127.0.0.1:8000/challenges/
echo - Dashboard with challenges: http://127.0.0.1:8000/dashboard/

pause