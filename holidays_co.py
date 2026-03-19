# app/holidays_co.py
from datetime import date

# Festivos oficiales CO (2024-2026) basados en listados publicados por festivos.com.co [3](https://www.calendariodecolombia.com/calendario-2024.html)[1](https://festivos-colombia.com.co/calendario-2025/)[2](https://colombiafestivos.com.co/calendario-2026-colombia-festivos.html)
HOLIDAYS_CO_2024_2026 = [
    # 2024
    (date(2024, 1, 1), "Año Nuevo"),
    (date(2024, 1, 8), "Reyes Magos"),
    (date(2024, 3, 25), "Día de San José"),
    (date(2024, 3, 28), "Jueves Santo"),
    (date(2024, 3, 29), "Viernes Santo"),
    (date(2024, 5, 1), "Día del trabajo"),
    (date(2024, 5, 13), "Ascensión de Jesús"),
    (date(2024, 6, 3), "Corpus Christi"),
    (date(2024, 6, 10), "Sagrado Corazón de Jesús"),
    (date(2024, 7, 1), "San Pedro y San Pablo"),
    (date(2024, 7, 20), "Día de la independencia"),
    (date(2024, 8, 7), "Batalla de Boyacá"),
    (date(2024, 8, 19), "Asunción de la Virgen"),
    (date(2024, 10, 14), "Día de la raza"),
    (date(2024, 11, 4), "Todos los Santos"),
    (date(2024, 11, 11), "Independencia de Cartagena"),
    (date(2024, 12, 8), "Inmaculada Concepción"),
    (date(2024, 12, 25), "Navidad"),

    # 2025 [1](https://festivos-colombia.com.co/calendario-2025/)
    (date(2025, 1, 1), "Año Nuevo"),
    (date(2025, 1, 6), "Reyes Magos"),
    (date(2025, 3, 24), "Día de San José"),
    (date(2025, 4, 17), "Jueves Santo"),
    (date(2025, 4, 18), "Viernes Santo"),
    (date(2025, 5, 1), "Día del trabajo"),
    (date(2025, 6, 2), "Ascensión de Jesús"),
    (date(2025, 6, 23), "Corpus Christi"),
    (date(2025, 6, 30), "Sagrado Corazón de Jesús"),
    (date(2025, 6, 30), "San Pedro y San Pablo"),
    (date(2025, 7, 20), "Día de la independencia"),
    (date(2025, 8, 7), "Batalla de Boyacá"),
    (date(2025, 8, 18), "Asunción de la Virgen"),
    (date(2025, 10, 13), "Día de la raza"),
    (date(2025, 11, 3), "Todos los Santos"),
    (date(2025, 11, 17), "Independencia de Cartagena"),
    (date(2025, 12, 8), "Inmaculada Concepción"),
    (date(2025, 12, 25), "Navidad"),

    # 2026 [2](https://colombiafestivos.com.co/calendario-2026-colombia-festivos.html)
    (date(2026, 1, 1), "Año Nuevo"),
    (date(2026, 1, 12), "Reyes Magos"),
    (date(2026, 3, 23), "Día de San José"),
    (date(2026, 4, 2), "Jueves Santo"),
    (date(2026, 4, 3), "Viernes Santo"),
    (date(2026, 5, 1), "Día del trabajo"),
    (date(2026, 5, 18), "Ascensión de Jesús"),
    (date(2026, 6, 8), "Corpus Christi"),
    (date(2026, 6, 15), "Sagrado Corazón de Jesús"),
    (date(2026, 6, 29), "San Pedro y San Pablo"),
    (date(2026, 7, 20), "Día de la independencia"),
    (date(2026, 8, 7), "Batalla de Boyacá"),
    (date(2026, 8, 17), "Asunción de la Virgen"),
    (date(2026, 10, 12), "Día de la raza"),
    (date(2026, 11, 2), "Todos los Santos"),
    (date(2026, 11, 16), "Independencia de Cartagena"),
    (date(2026, 12, 8), "Inmaculada Concepción"),
    (date(2026, 12, 25), "Navidad"),
]

def holidays_set_and_map():
    """
    Retorna:
    - set de fechas festivas (date)
    - dict {date: nombre_festivo}
    """
    s = {d for d, _ in HOLIDAYS_CO_2024_2026}
    m = {d: name for d, name in HOLIDAYS_CO_2024_2026}
    return s, m