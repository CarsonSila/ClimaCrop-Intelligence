from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Provenance(Enum):
    MEASURED = "measured"
    OFFICIAL = "official"
    ESTIMATED = "estimated"
    MODELED = "modeled"
    ASSUMED = "assumed"

    @property
    def confidence_weight(self) -> float:
        return {
            Provenance.MEASURED: 1.0,
            Provenance.OFFICIAL: 0.9,
            Provenance.ESTIMATED: 0.65,
            Provenance.MODELED: 0.5,
            Provenance.ASSUMED: 0.2,
        }[self]

    @property
    def label(self) -> str:
        return {
            Provenance.MEASURED: "Measured",
            Provenance.OFFICIAL: "Official source",
            Provenance.ESTIMATED: "Estimated (documented method)",
            Provenance.MODELED: "Model output",
            Provenance.ASSUMED: "Unverified placeholder",
        }[self]

    @property
    def badge_color(self) -> str:
        return {
            Provenance.MEASURED: "#1e8e3e",
            Provenance.OFFICIAL: "#1a73e8",
            Provenance.ESTIMATED: "#f9ab00",
            Provenance.MODELED: "#e8710a",
            Provenance.ASSUMED: "#d93025",
        }[self]


@dataclass
class SourcedValue:
    value: Any
    provenance: Provenance
    citation: str = ""
    source_url: str = ""
    as_of: str = ""
    note: str = ""

    def __repr__(self):
        return f"{self.value} [{self.provenance.label}]"

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "provenance": self.provenance.value,
            "provenance_label": self.provenance.label,
            "citation": self.citation,
            "source_url": self.source_url,
            "as_of": self.as_of,
            "note": self.note,
        }


@dataclass
class ProvenanceReport:
    fields: dict = field(default_factory=dict)

    def add(self, name: str, sourced_value: SourcedValue):
        self.fields[name] = sourced_value
        return self

    @property
    def overall_confidence(self) -> float:
        if not self.fields:
            return 0.0
        weights = [sv.provenance.confidence_weight for sv in self.fields.values()]
        return round(sum(weights) / len(weights), 3)

    @property
    def weakest_link(self) -> Optional[SourcedValue]:
        if not self.fields:
            return None
        return min(self.fields.values(), key=lambda sv: sv.provenance.confidence_weight)

    def summary_label(self) -> str:
        c = self.overall_confidence
        if c >= 0.85:
            return "High confidence — built on measured/official data"
        elif c >= 0.6:
            return "Moderate confidence — includes estimated figures"
        elif c >= 0.35:
            return "Low confidence — relies on modeled or placeholder data"
        else:
            return "Unverified — mostly placeholder data, not for real decisions"

    def to_dict(self) -> dict:
        return {
            "overall_confidence": self.overall_confidence,
            "summary": self.summary_label(),
            "weakest_link": self.weakest_link.to_dict() if self.weakest_link else None,
            "fields": {k: v.to_dict() for k, v in self.fields.items()},
        }
