
from __future__ import annotations
import requests
import pandas as pd

from src.provenance import Provenance, SourcedValue

FAOSTAT_BASE_URL = "https://fenixservices.fao.org/faostat/api/v1/en/data/QCL"
KENYA_AREA_CODE = 114
YIELD_ELEMENT_CODE = 5419


class FaostatClient:
    def fetch_yield(self, crop_item_code: int, years: list[int]) -> pd.DataFrame:
        params = {
            "area": KENYA_AREA_CODE,
            "item": crop_item_code,
            "element": YIELD_ELEMENT_CODE,
            "year": ",".join(str(y) for y in years),
        }
        resp = requests.get(FAOSTAT_BASE_URL, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return pd.DataFrame(data)

    def sourced_yield(self, kg_per_ha: float, crop: str, year: int) -> SourcedValue:
        return SourcedValue(
            value=round(kg_per_ha / 2.47105, 1),  # convert hectare -> acre
            provenance=Provenance.OFFICIAL,
            citation=f"FAOSTAT QCL, Kenya, {year}",
            source_url="https://www.fao.org/faostat/en/#data/QCL",
            as_of=str(year),
            note=f"National average for {crop}, not Nakuru/smallholder-specific. "
                 f"Converted from kg/ha to kg/acre.",
        )


if __name__ == "__main__":
    client = FaostatClient()
    df = client.fetch_yield(crop_item_code=56, years=[2020, 2021, 2022])
    print(df.head())
