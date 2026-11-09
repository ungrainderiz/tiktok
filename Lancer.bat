@echo off
REM Double-clic : ouvre la fenetre. Glisser une video sur ce fichier : la decoupe directement.
cd /d "%~dp0"
python decoupeur.py %*
if errorlevel 1 pause
