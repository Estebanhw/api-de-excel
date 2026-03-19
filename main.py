#app/main.pu
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO

from excel_processor import process_excel, ProcessorConfig

app = FastAPI(title="Procesador de Excel", version="1.0") #numero de version

# Habilitar CORS para facilitar desarrollo del frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/process")
async def process(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel .xlsx/.xls")
    
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # Limite de 10MB
        raise HTTPException(status_code=413, detail="Archivo demasiado grande. El límite es de 10MB.")
    
    cfg = ProcessorConfig(
        tz="America/Mexico_City",
        weekdays_only=True,
        exclude_holidays=True, # Festivos son NO laborables para las horas laborales
    )

    try:
        out_bytes = process_excel(contents, cfg)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"No pude procesar el archivo: {e}")
    
    output_name = file.filename.rsplit(".", 1)[0] + "_procesado.xlsx"
    return StreamingResponse(
        BytesIO(out_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={output_name}"}
    )
