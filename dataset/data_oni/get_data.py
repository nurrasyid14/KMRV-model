from pathlib import Path
import pandas as pd
import requests

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

url_oni = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"

df_oni = pd.read_csv(url_oni, sep=r"\s+")
csv_path = OUTPUT_DIR / "oni.csv"
df_oni.to_csv(csv_path, index=False)
print(f"Dataframe tersimpan di: {csv_path}")

txt_path = OUTPUT_DIR / "oni.ascii.txt"
response = requests.get(url_oni)
response.raise_for_status()
txt_path.write_bytes(response.content)
print(f"File mentah tersimpan di: {txt_path}")
