# run_app.py
# Inicializador do Streamlit empacotado para Windows

import sys
import subprocess
import os

def main():

    # Garante que o diretório atual seja o da aplicação
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    comando = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.port=8501",
        "--server.headless=true"
    ]

    subprocess.run(comando)

if __name__ == "__main__":
    main()
