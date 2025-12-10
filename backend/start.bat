@echo off
echo ========================================
echo   JerryTech Backend - Demarrage
echo ========================================
echo.

REM Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

REM Verifier si les dependances sont installees
echo Verification des dependances...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installation des dependances...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERREUR: Echec de l'installation des dependances
        pause
        exit /b 1
    )
)

REM Verifier si la base de donnees existe
if not exist jerrytech.db (
    echo Initialisation de la base de donnees...
    python init_db.py
    if errorlevel 1 (
        echo ERREUR: Echec de l'initialisation de la base de donnees
        pause
        exit /b 1
    )
)

echo.
echo Demarrage du serveur API...
echo API disponible sur: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.

python main.py

pause

