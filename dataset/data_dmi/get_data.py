from pathlib import Path

import numpy as np
import pandas as pd
import requests

URL_DMI = "https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data"
OUTPUT_DIR = Path(__file__).resolve().parent
RAW_PATH = OUTPUT_DIR / "dmi.had.long.data"
CSV_PATH = OUTPUT_DIR / "dmi.csv"
MISSING_VALUE = -9999.0


def download_raw(url: str, dest: Path) -> None:
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    dest.write_bytes(response.content)


def parse_dmi(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=1, sep=r"\s+", header=None, dtype=str)
    df = df[df[0].str.match(r"^\d{4}$", na=False)].copy()
    df.columns = ["Year", *range(1, 13)]
    df = df.apply(pd.to_numeric, errors="coerce")

    return (
        df.melt(id_vars="Year", var_name="Month", value_name="DMI")
        .replace({"DMI": {MISSING_VALUE: np.nan}})
        .dropna(subset=["DMI"])
        .astype({"Year": int, "Month": int})
        .sort_values(["Year", "Month"])
        .reset_index(drop=True)
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    download_raw(URL_DMI, RAW_PATH)
    df_dmi = parse_dmi(RAW_PATH)
    df_dmi.to_csv(CSV_PATH, index=False)

    print(f"DMI berhasil disimpan di: {CSV_PATH} ({len(df_dmi)} baris)")


if __name__ == "__main__":
    main()
