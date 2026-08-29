from __future__ import annotations
import os
import pandas as pd
from src.provenance import Provenance, SourcedValue

REQUIRED_COLUMNS = ["crop", "market", "price_kes_per_kg", "collection_date", "source"]


class SnapshotNotFound(FileNotFoundError):
    pass


def load_price_snapshot(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise SnapshotNotFound(
            f"No price snapshot found at {path}. Real market prices for Kenyan "
            f"crops aren't available via a public API (AMIS is a web portal, not "
            f"an API) — populate this file from an AMIS bulletin, a KACE/RATIN "
            f"data partnership, or another cited source before running the "
            f"pipeline. Refusing to synthesize placeholder prices silently."
        )
    df = pd.read_csv(path)
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Price snapshot is missing required columns: {missing}")
    return df


def to_sourced_prices(df: pd.DataFrame) -> list[SourcedValue]:
    out = []
    for _, row in df.iterrows():
        out.append(SourcedValue(
            value=row["price_kes_per_kg"],
            provenance=Provenance.OFFICIAL,
            citation=row["source"],
            as_of=row["collection_date"],
            note=f"{row['crop']} @ {row['market']}",
        ))
    return out


if __name__ == "__main__":
    example_path = "data/market_price_snapshots/latest.csv"
    try:
        df = load_price_snapshot(example_path)
        print(f"Loaded {len(df)} sourced price rows.")
    except SnapshotNotFound as e:
        print(f"[Expected until a snapshot is curated] {e}")
