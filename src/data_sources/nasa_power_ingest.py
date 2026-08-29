from __future__ import annotations
import requests
import pandas as pd
from datetime import date

from src.provenance import Provenance, SourcedValue

POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


COUNTY_CENTROIDS = {
    "Nakuru": (-0.3031, 36.0800),
    "Uasin Gishu": (0.5143, 35.2698),
    "Kiambu": (-1.0333, 36.8667),
    "Nairobi": (-1.2864, 36.8172),
    "Makueni": (-1.8039, 37.6202),
    "Kitui": (-1.3667, 38.0167),
    "Bungoma": (0.5695, 34.5590),
    "Kisumu": (-0.0917, 34.7679),
    "Kwale": (-4.1743, 39.4522),
    "Mombasa": (-4.0435, 39.6682),
}


class NasaPowerClient:
    def fetch_daily(self, latitude: float, longitude: float, start: date, end: date) -> pd.DataFrame:
        """Fetch real daily temperature + precipitation for a point.
        No credentials required."""
        params = {
            "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR",
            "community": "AG",
            "longitude": longitude,
            "latitude": latitude,
            "start": start.strftime("%Y%m%d"),
            "end": end.strftime("%Y%m%d"),
            "format": "JSON",
        }
        resp = requests.get(POWER_BASE_URL, params=params, timeout=60)
        resp.raise_for_status()
        payload = resp.json()

        params_block = payload["properties"]["parameter"]
        df = pd.DataFrame({
            "date": pd.to_datetime(list(params_block["T2M"].keys()), format="%Y%m%d"),
            "temp_mean_c": list(params_block["T2M"].values()),
            "temp_max_c": list(params_block["T2M_MAX"].values()),
            "temp_min_c": list(params_block["T2M_MIN"].values()),
            "precip_mm": list(params_block["PRECTOTCORR"].values()),
        })
        
        df = df.replace(-999, pd.NA)
        return df

    def fetch_county_daily(self, county: str, start: date, end: date) -> pd.DataFrame:
        if county not in COUNTY_CENTROIDS:
            raise ValueError(f"No centroid configured for '{county}'. Add it to COUNTY_CENTROIDS "
                              f"(or better: use the cooperative's actual farm GPS point).")
        lat, lon = COUNTY_CENTROIDS[county]
        df = self.fetch_daily(lat, lon, start, end)
        df["county"] = county
        return df

    def sourced(self, value, note: str = "") -> SourcedValue:
        return SourcedValue(
            value=value,
            provenance=Provenance.MEASURED,
            citation="NASA POWER (satellite/reanalysis, AG community)",
            source_url="https://power.larc.nasa.gov/",
            note=note or "~0.5° grid resolution — regional signal, not a ground-station reading.",
        )


if __name__ == "__main__":
    client = NasaPowerClient()
    df = client.fetch_county_daily("Nakuru", date(2024, 3, 1), date(2024, 5, 31))
    print(df.head())
    print(f"\n{len(df)} real daily records fetched for Nakuru, MAM 2024.")
