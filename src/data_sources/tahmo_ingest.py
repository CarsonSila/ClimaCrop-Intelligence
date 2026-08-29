from __future__ import annotations
import os
import requests
import pandas as pd
from datetime import date

from src.provenance import Provenance, SourcedValue

TAHMO_BASE_URL = "https://datahub.tahmo.org/api/v1"


class CredentialsNotConfigured(RuntimeError):
    pass


class TahmoClient:
    def __init__(self, api_key: str | None = None, api_secret: str | None = None):
        self.api_key = api_key or os.environ.get("TAHMO_API_KEY")
        self.api_secret = api_secret or os.environ.get("TAHMO_API_SECRET")

    def _require_credentials(self):
        if not self.api_key or not self.api_secret:
            raise CredentialsNotConfigured(
                "No TAHMO API credentials found. TAHMO does not offer public "
                "self-serve signup — request access at https://tahmo.org, then "
                "set TAHMO_API_KEY and TAHMO_API_SECRET as environment variables. "
                "Refusing to proceed rather than silently generating synthetic data."
            )

    def list_stations(self, country: str = "KE") -> pd.DataFrame:
        """Fetch real station metadata (id, name, lat, lon, elevation)."""
        self._require_credentials()
        resp = requests.get(
            f"{TAHMO_BASE_URL}/services/assets/v2/stations",
            auth=(self.api_key, self.api_secret),
            params={"countrycode": country},
            timeout=30,
        )
        resp.raise_for_status()
        stations = resp.json().get("data", [])
        return pd.DataFrame(stations)

    def fetch_station_series(self, station_id: str, start: date, end: date, variable: str = "pr") -> pd.DataFrame:
        """Fetch real measured time series for one station/variable.
        `variable` uses TAHMO's short codes, e.g. 'pr' for precipitation,
        'te' for temperature — confirm exact codes against current TAHMO
        API docs when credentials are issued, as these are subject to
        change without notice from a third-party API.
        """
        self._require_credentials()
        resp = requests.get(
            f"{TAHMO_BASE_URL}/services/measurements/v2/stations/{station_id}/measurements/controlled",
            auth=(self.api_key, self.api_secret),
            params={"start": start.isoformat(), "end": end.isoformat(), "variable": variable},
            timeout=60,
        )
        resp.raise_for_status()
        df = pd.DataFrame(resp.json().get("results", [{}])[0].get("series", [{}])[0].get("values", []))
        return df

    def sourced(self, value, note: str = "") -> SourcedValue:
        """Wrap a value pulled from this client as MEASURED provenance."""
        return SourcedValue(
            value=value,
            provenance=Provenance.MEASURED,
            citation="TAHMO station network",
            source_url="https://tahmo.org",
            note=note,
        )


if __name__ == "__main__":
    client = TahmoClient()
    try:
        stations = client.list_stations()
        print(f"Fetched {len(stations)} real station records.")
    except CredentialsNotConfigured as e:
        print(f"[Expected until credentials are set up] {e}")
