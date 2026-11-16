"""ETL do Observatório Macro-Financeiro do Brasil.
Fonte: API pública do Sistema Gerenciador de Séries Temporais (SGS/BCB).
"""
from pathlib import Path
from datetime import datetime
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

SERIES = {
    "selic_meta": 432,
    "ipca_mensal": 433,
    "ipca_12m": 13522,
    "dolar_ptax": 1,
    "ibc_br": 24364,
}

START_DATE = "01/01/2020"
END_DATE = "31/12/2023"


def fetch_sgs_series(code: int, start_date: str = START_DATE,
                     end_date: str = END_DATE) -> pd.DataFrame:
    """Extrai uma série do SGS; datas no formato dd/mm/aaaa."""
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
    params = {"formato": "json", "dataInicial": start_date, "dataFinal": end_date}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if not payload:
        return pd.DataFrame(columns=["date", "value"])
    df = pd.DataFrame(payload)
    df["date"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    df["value"] = pd.to_numeric(
        df["valor"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )
    df = df[["date", "value"]].dropna(subset=["date", "value"])
    return df.drop_duplicates(subset=["date"]).sort_values("date")


def extract_all(start_date: str = START_DATE, end_date: str = END_DATE) -> dict:
    """Extrai todas as séries oficiais e grava cópias brutas."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    data = {}
    for name, code in SERIES.items():
        df = fetch_sgs_series(code, start_date, end_date)
        df.to_csv(RAW_DIR / f"{name}.csv", index=False, encoding="utf-8")
        data[name] = df
    return data


def transform_series(data: dict) -> pd.DataFrame:
    """Padroniza datas, remove duplicidades e combina as séries por mês."""
    monthly = []
    for name, df in data.items():
        if df.empty:
            continue
        clean = df.copy()
        clean["date"] = pd.to_datetime(clean["date"], errors="coerce")
        clean["value"] = pd.to_numeric(clean["value"], errors="coerce")
        clean = clean.dropna(subset=["date", "value"]).drop_duplicates("date")
        clean = clean.sort_values("date").set_index("date")
        # Média mensal para séries diárias; valor mensal para séries mensais.
        clean = clean.resample("MS").mean(numeric_only=True).rename(
            columns={"value": name}
        )
        monthly.append(clean)
    if not monthly:
        return pd.DataFrame(columns=["date", *SERIES.keys()])
    result = pd.concat(monthly, axis=1).reset_index()
    result = result.rename(columns={"index": "date"})
    result["juro_real_ex_post"] = (
        ((1 + result["selic_meta"] / 100) /
         (1 + result["ipca_12m"] / 100)) - 1
    ) * 100
    result = result.sort_values("date").drop_duplicates("date")
    return result


def validate_data(df: pd.DataFrame) -> dict:
    """Retorna diagnóstico simples de qualidade da base."""
    return {
        "linhas": int(len(df)),
        "duplicados": int(df.duplicated().sum()) if not df.empty else 0,
        "nulos_por_coluna": df.isna().sum().to_dict() if not df.empty else {},
        "data_inicial": str(df["date"].min().date()) if not df.empty else None,
        "data_final": str(df["date"].max().date()) if not df.empty else None,
    }


def run_etl(start_date: str = START_DATE, end_date: str = END_DATE) -> pd.DataFrame:
    data = extract_all(start_date, end_date)
    result = transform_series(data)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(PROCESSED_DIR / "indicadores_macro.csv", index=False, encoding="utf-8")
    return result


if __name__ == "__main__":
    final = run_etl()
    print("ETL concluído:", validate_data(final))
