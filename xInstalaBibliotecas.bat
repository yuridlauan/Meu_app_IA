@echo off
cd /d %~dp0

echo.
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo.
set /p LIB="Digite o nome da biblioteca que deseja instalar: "
echo.
echo Instalando %LIB% no ambiente virtual...
echo ----------------------------------------
pip install %LIB%
echo ----------------------------------------

echo.
pause
