#!/usr/bin/env python
import sys
import os
sys.path.insert(0, r'c:/Users/julian.soler/Music/Appi de ans/APP')

from excel_processor import process_excel, ProcessorConfig
from pathlib import Path

input_file = Path("c:/Users/julian.soler/Music/Appi de ans/APP/sample_input.xlsx")
output_file = Path("c:/Users/julian.soler/Music/Appi de ans/APP/test_output.xlsx")

if not input_file.exists():
    print("ERROR: archivo no existe", input_file)
    sys.exit(1)

print("Procesando", input_file.name, "...")
try:
    with open(input_file, "rb") as f:
        content = f.read()
    
    cfg = ProcessorConfig(
        tz="America/Mexico_City",
        weekdays_only=True,
        exclude_holidays=True
    )
    
    result = process_excel(content, cfg)
    
    with open(output_file, "wb") as f:
        f.write(result)
    
    print(f"✓ Procesado correctamente. Archivo de salida: {output_file.name}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
