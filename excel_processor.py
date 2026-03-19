# app/excel_processor.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from io import BytesIO
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import unicodedata

from holidays_co import HOLIDAYS_CO_2024_2026, holidays_set_and_map 


@dataclass
class ProcessorConfig:
    tz: str = "America/Bogota"          
    work_start: time = time(7, 0, 0)    # 07:00
    work_end: time = time(18, 0, 0)     # 18:00
    weekdays_only: bool = True          # L-V
    exclude_holidays: bool = True       # Festivos NO laborables

def _to_datetime(series: pd.Series | None) -> pd.Series:
    """Convierte serie a datetime, retornando Series vacía si es None."""
    if series is None:
        return pd.Series(dtype='datetime64[ns]')
    converted = pd.to_datetime(series, errors="coerce", utc=False)
    return converted

def _working_hours_between(start: pd.Timestamp, end: pd.Timestamp,
                           cfg: ProcessorConfig,
                           holiday_set: set) -> float:
    
    if pd.isna(start):
        return np.nan
    if pd.isna(end):
        end = pd.Timestamp(datetime.now(ZoneInfo(cfg.tz)))
    
    if end < start:
        return 0.0
    
    total = 0.0
    day = start.normalize()
    last = end.normalize()
    one_day = pd.Timedelta(days=1)

    while day <= last:
        d = day.date()

        is_weekday_ok = (day.dayofweek < 5) if cfg.weekdays_only else True
        is_holyday = (d in holiday_set) if cfg.exclude_holidays else False

        if is_weekday_ok and not is_holyday:
            ws = day + pd.Timedelta(hours=cfg.work_start.hour, minutes=cfg.work_start.minute)
            we = day + pd.Timedelta(hours=cfg.work_end.hour, minutes=cfg.work_end.minute)

            seg_start = max(start, ws)
            seg_end = min(end, we)

            if seg_end > seg_start:
                total += (seg_end - seg_start).total_seconds() / 3600.0
            
        day += one_day
    return round(total, 2)

def process_excel(file_bytes: bytes, cfg: ProcessorConfig | None = None) -> bytes:
    cfg = cfg or ProcessorConfig()
    tz = ZoneInfo(cfg.tz)


    # Leer Excel
    df = pd.read_excel(BytesIO(file_bytes), engine="openpyxl")

    # Normalizar nombres de columnas: quitar acentos, minúsculas, sólo letras y números
    def normalize(name: str) -> str:
        n = unicodedata.normalize('NFKD', name)
        n = ''.join(ch for ch in n if not unicodedata.combining(ch))
        n = n.lower()
        # mantener letras, números y espacios
        n = ''.join(ch if (ch.isalnum() or ch.isspace()) else ' ' for ch in n)
        # colapsar espacios
        n = ' '.join(n.split())
        return n

    df_cols_norm = {normalize(col): col for col in df.columns}

    # Variantes posibles para cada columna esperada
    col_open_variants = ["fecha de apertura", "fecha apertura", "fecha_inicio", "fecha apertura"]
    col_last_variants = ["ultima fecha actualizacion", "ultima fecha actualización", "fecha de actualizacion", "fecha actualizacion", "ultima actualizacion", "fecha actualizacion"]
    col_ans_variants = ["ans", "tiempo ans", "ans horas"]

    def find_col(variants: list[str]) -> str | None:
        for v in variants:
            key = normalize(v)
            if key in df_cols_norm:
                return df_cols_norm[key]
        return None

    col_open = find_col(col_open_variants)
    col_last = find_col(col_last_variants)
    col_ans = find_col(col_ans_variants)

    # Validar que las columnas existan
    if not col_open:
        raise ValueError(f"Columna buscada (variantes: {col_open_variants}) no encontrada. Columnas disponibles: {list(df.columns)}")
    if not col_last:
        raise ValueError(f"Columna buscada (variantes: {col_last_variants}) no encontrada. Columnas disponibles: {list(df.columns)}")

    # Convertir fechas asegurando tipos datetime
    start = pd.to_datetime(df[col_open], errors="coerce").fillna(pd.Timestamp(datetime.now(tz)))
    end = pd.to_datetime(df[col_last], errors="coerce").fillna(pd.Timestamp(datetime.now(tz)))

    # Guardar columnas convertidas en el dataframe
    df[col_open] = start
    df[col_last] = end

    # Festivos
    holiday_set, holiday_map = holidays_set_and_map()

    #Flags de festivo por fecha (solo por el dia calendario, no por hora)
    ap_date = start.dt.date
    ua_date = end.dt.date

    df["Es_Festivo_CO_Apertura"] = ap_date.apply(lambda d: "SI" if pd.notna(d) and d in holiday_set else "NO")
    df["Nombre_Festivo_Apertura"] = ap_date.apply(lambda d: holiday_map.get(d,"") if pd.notna(d) else "")

    df["Es_Festivo_CO_UltimaActualizacion"] = ua_date.apply(lambda d: "SI" if pd.notna(d) and d in holiday_set else "NO")
    df["Nombre_Festivo_UltimaActualizacion"] = ua_date.apply(lambda d: holiday_map.get(d,"") if pd.notna(d) else "")

    #Horas 24/7
    hours_247 = (end - start).dt.total_seconds() / 3600.0
    df["Horas_Transcurridas_24_7"] = hours_247.round(2)

    #Dias calendario
    df["Dias_Activos_Calendario"] = ((end - start).dt.total_seconds() / 86400).round(2)

    # helper: formatear días a texto (definido antes de su primer uso)
    def format_days(v):
        try:
            if v is None:
                return ""
            if isinstance(v, (str, bytes)):
                # intentar convertir a float
                v = float(str(v).replace(',', '.'))
            if np.isnan(v):
                return ""
        except Exception:
            return ""
        # redondear a 2 decimales
        val = round(float(v), 2)
        # decidir singular/plural (usar singular solo si es exactamente 1.0)
        is_int = abs(val - round(val)) < 1e-9
        if is_int:
            n = int(round(val))
            word = "día" if n == 1 else "días"
            return f"{n} {word}"
        # formato con coma decimal
        s = f"{val:.2f}".replace('.', ',')
        word = "día" if abs(val - 1.0) < 1e-9 else "días"
        return f"{s} {word}"

    def format_days_hours_from_hours(hours: float, per_day_hours: float) -> str:
        """Convierte una cantidad de horas a 'X días Y h' usando per_day_hours como horas por día."""
        try:
            if hours is None:
                return ""
            if isinstance(hours, (str, bytes)):
                hours = float(str(hours).replace(',', '.'))
            if np.isnan(hours):
                return ""
        except Exception:
            return ""
        if per_day_hours <= 0:
            per_day_hours = 24.0
        total_hours = float(hours)
        days = int(total_hours // per_day_hours)
        rem_hours = int(round(total_hours - days * per_day_hours))
        parts = []
        if days > 0:
            parts.append(f"{days} día" if days == 1 else f"{days} días")
        if rem_hours > 0 or (days == 0 and rem_hours == 0):
            parts.append(f"{rem_hours} h")
        return ' '.join(parts)

    # Columna de texto para Dias_Activos_Calendario
    df["Dias_Activos_Calendario_Texto"] = [format_days(x) for x in df["Dias_Activos_Calendario"]]

    #Estado ANS (ANS 24/7)
    # Si la columna ANS existe, usarla; si no, usar NaN
    if col_ans:
        ans = pd.to_numeric(df.get(col_ans), errors="coerce")
    else:
        ans = pd.Series([np.nan] * len(df))
    
    df["Estado_ANS_24_7"] = np.where(
        (~ans.isna()) & (~hours_247.isna()) & (hours_247 > ans),
        "VENCIDO",
        np.where((~ans.isna()) & (~hours_247.isna()), "EN TIEMPO", "")
    )
    # Horas laborales (7-18, L-V)) EXCLUYENDO FESTIVOS
    labor = [
        _working_hours_between(s, e, cfg, holiday_set)
        for s, e in zip(start, end)
    ]
    df["Horas_Laborales_7a18_LV_sin_Festivos"] = np.round(np.array(labor, dtype="float"),2)

    # Horas no laborales (24/7 - laborales)
    nonlabor = np.maximum(0, hours_247.values  - np.array(labor, dtype="float"))
    df["Horas_No_Laborales_24_7_menos_7a18_LV_sin_Festivos"] = np.round(nonlabor,2)
    # Columna adicional: convertir horas no laborales a días (horas / 24)
    df["Dias_No_Laborales_24_7_menos_7a18_LV_sin_Festivos"] = np.round(nonlabor / 24.0, 2)
    df["Dias_No_Laborales_24_7_menos_7a18_LV_sin_Festivos_Texto"] = [format_days_hours_from_hours(x, 24.0) if pd.notna(x) else "" for x in df["Horas_No_Laborales_24_7_menos_7a18_LV_sin_Festivos"]]
    # Columnas de texto para otras horas -> días+horas
    # Horas transcurridas -> usar base 24h
    df["Dias_Transcurridas_24_7_Texto"] = [format_days_hours_from_hours(x, 24.0) if pd.notna(x) else "" for x in df["Horas_Transcurridas_24_7"]]
    # Horas laborales -> usar jornada laboral (cfg.work_end - cfg.work_start)
    work_minutes = (cfg.work_end.hour * 60 + cfg.work_end.minute) - (cfg.work_start.hour * 60 + cfg.work_start.minute)
    work_day_hours = work_minutes / 60.0 if work_minutes > 0 else 24.0
    df["Dias_Laborales_7a18_LV_sin_Festivos_Texto"] = [format_days_hours_from_hours(x, work_day_hours) if pd.notna(x) else "" for x in df["Horas_Laborales_7a18_LV_sin_Festivos"]]

    # Calcular días no laborales contando festivos (por día calendario)
    def count_non_labor_days(s: pd.Timestamp, e: pd.Timestamp, cfg: ProcessorConfig, holiday_set: set) -> int:
        try:
            if pd.isna(s) or pd.isna(e):
                return 0
        except Exception:
            return 0
        day = s.normalize()
        last = e.normalize()
        cnt = 0
        one_day = pd.Timedelta(days=1)
        while day <= last:
            d = day.date()
            is_weekday_ok = (day.dayofweek < 5) if cfg.weekdays_only else True
            is_holyday = (d in holiday_set)
            # considerar no laborable si es fin de semana (si weekdays_only) o si es festivo
            if (not is_weekday_ok) or is_holyday:
                cnt += 1
            day += one_day
        return cnt

    dias_no_lab_cnt = [count_non_labor_days(s, e, cfg, holiday_set) for s, e in zip(start, end)]
    df["Dias_No_Laborales_Contando_Festivos"] = dias_no_lab_cnt
    df["Dias_No_Laborales_Contando_Festivos_Texto"] = [f"{n} día" if n==1 else f"{n} días" for n in dias_no_lab_cnt]

    #Hoja de festivos
    fest_df = pd.DataFrame(HOLIDAYS_CO_2024_2026, columns=["Fecha", "Festivo"])
    fest_df["Fecha"] = pd.to_datetime(fest_df["Fecha"])

    # Exportar a bytes (Excel)
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Detalle")
        fest_df.to_excel(writer, index=False, sheet_name="Festivos_CO_2024_2026")
    
    out.seek(0)
    return out.read()