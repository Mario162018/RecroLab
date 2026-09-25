#!/usr/bin/env bash
# Genera un ejecutable de RecreoLab a partir de app.py, sin ventana
# de terminal. Necesita Python instalado en esta computadora y
# conexión a Internet SOLO la primera vez (para bajar dependencias).
set -e

echo "=========================================="
echo "  RecreoLab - generar ejecutable (Linux/Mac)"
echo "=========================================="
echo

python3 -m pip install --upgrade pip
python3 -m pip install customtkinter pyinstaller pillow

CARPETA="$(cd "$(dirname "$0")" && pwd)"
SISTEMA="$(uname)"

echo
echo "Generando el ejecutable, un momento..."
echo

if [ "$SISTEMA" = "Darwin" ]; then
    pyinstaller --noconfirm --onefile --windowed --name RecreoLab \
        --icon=RecreoLab.ico --collect-all customtkinter app.py

    if [ ! -f "dist/recreolab_datos.json" ] && [ -f "recreolab_datos.json" ]; then
        cp recreolab_datos.json dist/
    fi

    echo
    echo "=========================================="
    echo "Listo. Quedó dist/RecreoLab.app — se abre"
    echo "con doble clic, o arrastrándolo a Aplicaciones."
    echo "=========================================="
else
    pyinstaller --noconfirm --onefile --windowed --name RecreoLab \
        --collect-all customtkinter app.py

    if [ ! -f "dist/recreolab_datos.json" ] && [ -f "recreolab_datos.json" ]; then
        cp recreolab_datos.json dist/
    fi
    cp RecreoLab.ico dist/RecreoLab.ico

    LANZADOR="$HOME/.local/share/applications/recreolab.desktop"
    mkdir -p "$HOME/.local/share/applications"
    cat > "$LANZADOR" << LANZADOR_EOF
[Desktop Entry]
Type=Application
Name=RecreoLab
Comment=Kiosco escolar simulado
Exec=$CARPETA/dist/RecreoLab
Icon=$CARPETA/dist/RecreoLab.ico
Terminal=false
Categories=Education;
LANZADOR_EOF
    chmod +x "$LANZADOR"
    if [ -d "$HOME/Desktop" ]; then
        cp "$LANZADOR" "$HOME/Desktop/recreolab.desktop"
        chmod +x "$HOME/Desktop/recreolab.desktop"
    fi

    echo
    echo "=========================================="
    echo "Listo. RecreoLab ya aparece en el menú de"
    echo "aplicaciones (y en el Escritorio, si existe)."
    echo "=========================================="
fi
