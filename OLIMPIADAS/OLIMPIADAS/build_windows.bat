@echo off
REM Genera RecreoLab.exe a partir de app.py. Necesita Python instalado
REM en esta PC y conexion a Internet SOLO la primera vez (para bajar
REM las dependencias). Despues de generado, el .exe funciona sin
REM Python ni Internet, con icono propio y sin ventana de consola.

echo ==========================================
echo   RecreoLab - generar ejecutable (Windows)
echo ==========================================
echo.

REM En algunas instalaciones de Windows el comando que funciona es
REM "python" y en otras es el lanzador "py". Probamos los dos y
REM usamos el que funcione, sin que haga falta tocar nada a mano.
set PY_CMD=
where python >nul 2>nul
if %errorlevel%==0 set PY_CMD=python
if not defined PY_CMD (
    where py >nul 2>nul
    if %errorlevel%==0 set PY_CMD=py
)

if not defined PY_CMD (
    echo No se encontro Python instalado en esta PC.
    echo Instalalo desde https://www.python.org/downloads/
    echo IMPORTANTE: en el instalador, tildar la casilla
    echo "Add python.exe to PATH" antes de instalar.
    echo Despues, cerrar esta ventana, abrir una nueva y
    echo volver a correr este script.
    pause
    exit /b 1
)

echo Usando el comando: %PY_CMD%
echo.

%PY_CMD% -m pip install --upgrade pip
%PY_CMD% -m pip install customtkinter pyinstaller pillow

echo.
echo Generando el ejecutable, un momento...
echo.

REM Usamos "-m PyInstaller" (como modulo) en vez del comando
REM "pyinstaller" suelto: asi funciona aunque su carpeta Scripts
REM tampoco este en el PATH.
%PY_CMD% -m PyInstaller --noconfirm --onefile --windowed --name RecreoLab ^
    --icon=RecreoLab.ico --collect-all customtkinter app.py

echo.
echo Copiando el icono y los datos junto al ejecutable...
if exist RecreoLab.ico copy /y RecreoLab.ico dist\RecreoLab.ico >nul
if not exist dist\recreolab_datos.json if exist recreolab_datos.json copy recreolab_datos.json dist\ >nul

echo.
echo Creando el acceso directo en el Escritorio...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0crear_acceso_directo.ps1"

echo.
echo ==========================================
echo Listo. Quedo un acceso directo "RecreoLab"
echo en el Escritorio, con su propio icono y sin
echo ventana negra de consola al abrirlo.
echo (El .exe real esta en dist\RecreoLab.exe,
echo  por si prefieren moverlo a otro lado.)
echo ==========================================
pause
