import pandas as pd
from datetime import datetime, timedelta

now = datetime.now()
rows = [
    {"Fecha de apertura": now - timedelta(days=3), "ultima Fecha Actualización": now - timedelta(days=1), "Ans": 48},
    {"Fecha de apertura": now - timedelta(days=10), "ultima Fecha Actualización": now - timedelta(days=2), "Ans": 72},
]

df = pd.DataFrame(rows)
df.to_excel("sample_input.xlsx", index=False)
print("WROTE sample_input.xlsx")
