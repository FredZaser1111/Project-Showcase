"""Mock regional banking regulations for compliance investigator."""

from __future__ import annotations

REGULATIONS: dict[str, list[str]] = {
    "northeast": [
        "NYDFS Part 500: document enhanced due diligence when DTI > 0.45 or credit < 620.",
        "MA 209 CMR 18.00: disclose adverse action factors within 30 days for borderline denials.",
    ],
    "southeast": [
        "FL OFR guidance: escalate applications with ≥3 prior delinquencies to senior underwriter.",
        "GA Fair Lending Act: justify rate exceptions with documented risk mitigants.",
    ],
    "midwest": [
        "IL Predatory Loan Prevention Act: cap fees; require ability-to-repay attestation.",
        "OH Residential Mortgage Lending Act: retain underwriting rationale for 36 months.",
    ],
    "west": [
        "CA DFPI: gray-zone credit decisions require second-level review before funding.",
        "WA Consumer Loan Act: document compensating factors when credit < 640.",
    ],
}


def lookup_regulations(region: str) -> list[str]:
    return REGULATIONS.get(region.lower(), [
        "Federal ECOA / Reg B: provide specific adverse action reasons; avoid prohibited bases.",
        "FDIC safety-and-soundness: maintain documented credit policy exceptions.",
    ])
