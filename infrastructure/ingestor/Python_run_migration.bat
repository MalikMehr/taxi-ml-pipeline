@echo off
echo --- Starting Quarterly Data Migration ---
:: Enter the specific folder where the YAML and Python files live
cd /d "C:\Users\Mehr Khan\Desktop\University\IU Studies\Semester 3 (1 left 3 done)\Data Engineering project\Development\Project\infrastructure\ingestor"

:: Use your specific filename: Pythonmover.yml
docker-compose -f Pythonmover.yml up --build --force-recreate
echo --- Migration Complete ---
pause