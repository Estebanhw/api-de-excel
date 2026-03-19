#!/usr/bin/env python
"""
Levanta el proyecto completo: backend (uvicorn) + frontend (http.server)
y abre automáticamente el navegador.
"""
import subprocess
import time
import webbrowser
import sys
import os

def run():
    cwd = os.path.dirname(os.path.abspath(__file__))
    venv_scripts = os.path.join(cwd, ".venv", "Scripts")
    python_exe = os.path.join(venv_scripts, "python.exe")
    
    if not os.path.exists(python_exe):
        print("ERROR: entorno virtual no encontrado en", venv_scripts)
        sys.exit(1)
    
    print("=" * 60)
    print("Iniciando servidor backend (uvicorn)...")
    print("=" * 60)
    
    # Levantar backend en background
    backend_proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)
    print("✓ Backend levantado en http://127.0.0.1:8000")
    
    print("=" * 60)
    print("Iniciando servidor frontend (http.server)...")
    print("=" * 60)
    
    # Levantar frontend en background
    frontend_dir = os.path.join(cwd, "frontend")
    frontend_proc = subprocess.Popen(
        [python_exe, "-m", "http.server", "8080", "-d", frontend_dir],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(1)
    print("✓ Frontend levantado en http://127.0.0.1:8080")
    
    print("=" * 60)
    print("Abriendo navegador...")
    print("=" * 60)
    
    # Abrir navegador
    webbrowser.open("http://127.0.0.1:8080")
    print("✓ Navegador abierto en http://127.0.0.1:8080")
    print()
    print("=" * 60)
    print("PROYECTO INICIADO")
    print("=" * 60)
    print("Backend:  http://127.0.0.1:8000 (documentación en /docs)")
    print("Frontend: http://127.0.0.1:8080")
    print()
    print("Presiona Ctrl+C para detener ambos servidores...")
    print("=" * 60)
    
    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\n\nDeteniendo...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("✓ Servidores detenidos.")

if __name__ == "__main__":
    run()
