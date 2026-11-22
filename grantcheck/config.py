"""Programme presets and the catalogue of checks.

Only the parameters that differ between EU grant schemes live here. Sources: European Commission,
"EU Grants: AGA - Annotated Grant Agreement", version 2.0 of 1 April 2025, and the Horizon Europe
Model Grant Agreement (see docs/rules_reference.md).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Programme:
    name: str
    indirect_rate: float                    # flat rate for indirect costs (AGA Art. 6.2.E)
    indirect_base_excludes: tuple           # direct cost categories left out of the flat-rate base
    day_cap: int = 215                      # day-equivalents per person per year across EU grants
    cfs_threshold_eur: float | None = None  # requested EU contribution that requires a CFS


PROGRAMMES = {
    # Horizon Europe: 25% of eligible direct costs, excluding subcontracting and financial support
    # to third parties; certificate on the financial statements from EUR 430 000 requested
    "HORIZON": Programme("Horizon Europe", 0.25, ("B",), 215, 430_000),
    # standard option of the corporate model grant agreement: 7% of eligible direct costs
    # (categories A-D); the CFS threshold is set call by call in the Data Sheet
    "STANDARD": Programme("Corporate MGA, standard option", 0.07, (), 215, None),
}

CATEGORIES = ["A", "B", "C1", "C2", "C3", "D"]
CATEGORY_NAMES = {
    "A": "A. Personnel costs",
    "B": "B. Subcontracting costs",
    "C1": "C.1 Travel and subsistence",
    "C2": "C.2 Equipment",
    "C3": "C.3 Other goods, works and services",
    "D": "D. Other cost categories",
    "E": "E. Indirect costs",
}

# id: (what the check finds, reference, what to do about it)
RULES = {
    "R01": ("Cost incurred outside the action duration", "AGA Art. 6.1(a)(ii)",
            "Remove from the claim and charge it to the department's own funds."),
    "R02": ("Days above the yearly cap of 215 day-equivalents across EU grants", "AGA Art. 6.2.A",
            "Declare at most the remaining days; check the days declared on the person's other EU grants."),
    "R03": ("Time not supported by signed monthly time records", "AGA Art. 6.1(a)(v); MGA Art. 20",
            "Collect the signed records; if they cannot be produced, remove the cost."),
    "R04": ("Equipment declared above the depreciation for the period", "AGA Art. 6.2.C.2",
            "Declare only the depreciation for the months of use, times the share of use for the action."),
    "R05": ("No invoice or other supporting document", "AGA Art. 6.1(a)(v)",
            "File the invoice and the proof of payment, or remove the cost."),
    "R06": ("Deductible or refundable VAT", "AGA Art. 6.3(a)",
            "Declare the cost net of VAT."),
    "R07": ("Cost already declared under another EU grant", "AGA Art. 6.3(b)",
            "Keep the cost in one grant only."),
    "R08": ("Bank charges on transfers from the granting authority", "AGA Art. 6.3(a)",
            "Remove from direct costs."),
    "R09": ("Interest owed", "AGA Art. 6.3(a)",
            "Remove: interest is never eligible."),
    "W01": ("Travel above the beneficiary's usual travel rules", "AGA Art. 6.2.C.1; Art. 6.3(a)",
            "Justify it under the travel rules, or declare only the economy fare."),
    "W02": ("Subcontract not set out in Annex 1", "AGA Art. 6.2.B",
            "Ask the granting authority to approve it (amendment, or approval in the periodic report)."),
    "W03": ("Direct award at or above the national threshold for supplies and services",
            "D.Lgs. 36/2023, Art. 50(1)(b) and (e)",
            "Check the procurement file: from EUR 140 000 a negotiated procedure with at least five "
            "operators is required."),
}
