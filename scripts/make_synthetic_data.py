"""Generate the fictional data set for QPL-DEMO, reporting period 1 (Jan 2025 - Jun 2026).

Everything here is invented. The data deliberately contains the kinds of problems an audit
finds (listed in data/README.md), so that the checks in grantcheck can be seen working.

Run:  python scripts/make_synthetic_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
rng = np.random.default_rng(2026)
MONTHS = pd.period_range("2025-01", "2026-06", freq="M")

# ---- staff ---------------------------------------------------------------------------------
# annual personnel costs = gross salary + employer social contributions and taxes on pay (EUR);
# for a person hired during the year the figure is annualised (equivalent to pro-rating 215 days)
staff = pd.DataFrame([
    # id,  role,                                  contract,          2025,    2026,  exclusive, other EU days 2025, 2026
    ("S01", "Full professor (principal investigator)", "employee",        118000, 120400, False, 0, 0),
    ("S02", "Associate professor",                     "employee",         92000,  93800, False, 0, 0),
    ("S03", "Researcher (tenure track)",               "employee",         68000,  69400, False, 0, 0),
    ("S04", "Postdoctoral researcher",                 "direct contract",  31000,  31600, True,  0, 0),
    ("S05", "Postdoctoral researcher",                 "direct contract",  31000,  31600, True,  0, 0),
    ("S06", "Laboratory technician",                   "employee",         47000,  47900, False, 0, 0),
    ("S07", "Project manager",                         "employee",         44000,  44900, False, 0, 0),
    ("S08", "Research engineer (fixed term)",          "employee",         51000,  52000, False, 0, 0),
    ("S09", "Researcher",                              "employee",         66000,  67300, False, 70, 30),
    ("S10", "Postdoctoral researcher (from Jul 2025)", "direct contract",  31000,  31600, False, 0, 0),
], columns=["staff_id", "role", "contract", "annual_cost_2025", "annual_cost_2026", "exclusive",
            "other_eu_grant_days_2025", "other_eu_grant_days_2026"])

# ---- monthly time records -------------------------------------------------------------------
# days per month on each work package; exclusive staff file a monthly day-declaration,
# the others a timesheet; both must be signed by the person and the supervisor
plan = {
    "S01": {"WP1": 2.0, "WP2": 2.0, "WP3": 1.0},
    "S02": {"WP2": 2.0, "WP3": 2.0},
    "S03": {"WP2": 6.0, "WP3": 4.0},
    "S04": {"WP2": 10.0, "WP3": 7.5},
    "S05": {"WP2": 7.5, "WP3": 10.0},
    "S06": {"WP3": 8.0},
    "S07": {"WP1": 7.0, "WP4": 2.0},
    "S08": {"WP2": 9.5, "WP3": 10.0},          # 19.5 days a month in 2025: 234 days, above the cap
    "S09": {"WP2": 7.5, "WP3": 6.0},           # 162 days in 2025 + 70 days on another EU grant
    "S10": {"WP3": 10.0, "WP4": 5.0},
}
rows = []
for sid, wps in plan.items():
    exclusive = bool(staff.set_index("staff_id").loc[sid, "exclusive"])
    for m in MONTHS:
        if sid == "S10" and m < pd.Period("2025-07", "M"):
            continue                                            # not yet hired
        for wp, days in wps.items():
            d = days
            if sid == "S08" and m.year == 2026:
                d = days * 17 / 19.5                            # back to normal in 2026
            if sid == "S09" and m.year == 2026:
                d = days * 13 / 13.5
            d = round(d * 2) / 2
            signed_person = signed_supervisor = True
            if sid == "S05" and str(m) in ("2025-09", "2025-10"):
                signed_person = signed_supervisor = False       # monthly declarations never filed
            if sid == "S10" and str(m) in ("2026-03", "2026-04"):
                signed_supervisor = False                       # timesheets not countersigned
            rows.append((sid, str(m), wp, d, "monthly declaration" if exclusive else "timesheet",
                         signed_person, signed_supervisor))
time_records = pd.DataFrame(rows, columns=["staff_id", "month", "wp", "days", "record_type",
                                           "signed_by_person", "signed_by_supervisor"])

# ---- purchase costs, subcontracting and other charges ---------------------------------------
cols = ["expense_id", "date", "category", "description", "wp", "supplier", "invoice_ref",
        "net_eur", "vat_eur", "vat_recoverable", "declared_eur", "procurement",
        "purchase_price_eur", "useful_life_months", "available_from", "use_share",
        "flight_class", "economy_fare_eur", "subcontract_id", "other_eu_grant"]
exp = []


def add(**kw):
    rec = dict.fromkeys(cols)
    rec.update(kw)
    exp.append(rec)


# travel (C1): consortium meetings and conferences, economy class
meetings = [("Delft", 820), ("Grenoble", 690), ("Espoo", 1150), ("Munich", 640), ("Delft", 860),
            ("Grenoble", 720), ("Espoo", 1210)]
conferences = [("APS March Meeting, USA", 2650), ("Quantum technology conference, Rotterdam", 980),
               ("European Quantum Technologies Conference", 1040), ("Superconductivity workshop, Turin", 420)]
trip_dates = pd.date_range("2025-01-20", "2026-06-15", periods=18)
n = 0
for i, date in enumerate(trip_dates):
    if i % 3 == 2:
        place, base = conferences[(i // 3) % len(conferences)]
        what = f"Conference travel: {place}"
    else:
        place, base = meetings[i % len(meetings)]
        what = f"Consortium meeting, {place}"
    n += 1
    amount = round(base * rng.uniform(0.9, 1.15), 2)
    add(expense_id=f"T-{n:03d}", date=date.date().isoformat(), category="C1", description=what,
        wp="WP4" if "Conference" in what else "WP1", supplier="Travel agency (framework contract)",
        invoice_ref=f"TA-{25000 + n}", net_eur=amount, vat_eur=0.0, vat_recoverable=False,
        declared_eur=amount, procurement="framework", flight_class="economy")
# planted: business-class flight to the US conference
n += 1
add(expense_id=f"T-{n:03d}", date="2026-03-02", category="C1",
    description="Conference travel: APS March Meeting, USA", wp="WP4",
    supplier="Travel agency (framework contract)", invoice_ref=f"TA-{25000 + n}", net_eur=4150.0,
    vat_eur=0.0, vat_recoverable=False, declared_eur=4150.0, procurement="framework",
    flight_class="business", economy_fare_eur=1350.0)

# equipment (C2): declared as depreciation, except where planted
equipment = [
    # id,   description,                         price,  life, available,   share, declared (None = correct), procurement
    ("E-01", "Microwave signal generator",           48000, 60, "2025-03-01", 1.0, 48000.0, "negotiated"),
    ("E-02", "Cryogenic low-noise amplifiers (4)",   22000, 60, "2025-02-01", 1.0, None, "direct award"),
    ("E-03", "Arbitrary waveform generator",         35000, 60, "2025-05-01", 0.8, None, "direct award"),
    ("E-04", "Cryogenic probe station",             150000, 60, "2025-09-01", 1.0, None, "direct award"),
    ("E-05", "Lab data server",                      12000, 60, "2025-02-01", 0.5, None, "framework"),
    ("E-06", "Vector network analyser",              60000, 60, "2025-11-01", 0.7, 8000.0, "negotiated"),
]
for eid, desc, price, life, avail, share, declared, proc in equipment:
    months = (2026 - int(avail[:4])) * 12 + 6 - int(avail[5:7]) + 1
    correct = round(price / life * months * share, 2)
    add(expense_id=eid, date=avail, category="C2", description=desc, wp="WP3" if eid != "E-05" else "WP1",
        supplier=f"Supplier {eid}", invoice_ref=f"INV-{eid}", net_eur=float(price), vat_eur=0.0,
        vat_recoverable=False, declared_eur=declared if declared is not None else correct,
        procurement=proc, purchase_price_eur=float(price), useful_life_months=life,
        available_from=avail, use_share=share)

# other goods, works and services (C3)
c3 = []
for d in pd.date_range("2025-02-10", "2026-06-10", periods=12):
    c3.append(("Liquid helium delivery", "WP3", "Cryogenic gas supplier", rng.uniform(1200, 1800)))
for d in pd.date_range("2025-01-25", "2026-05-25", periods=10):
    c3.append(("Cleanroom consumables (wafers, resist)", "WP2", "Lab supplies distributor", rng.uniform(800, 2500)))
c3 += [("Chip packaging and wire-bonding service", "WP2", "Packaging service provider", 3000.0)] * 3
c3 += [("Open-access publication fee", "WP4", "Scientific publisher", v) for v in (2200.0, 2650.0, 2900.0)]
c3 += [("Conference registration fee", "WP4", "Conference organiser", v)
       for v in (450.0, 620.0, 750.0, 480.0, 690.0, 560.0)]
c3 += [("Printing of dissemination material", "WP4", "Print shop", 400.0)] * 2
c3_dates = pd.date_range("2025-01-28", "2026-06-20", periods=len(c3))
for k, ((desc, wp, sup, net), date) in enumerate(zip(c3, c3_dates), start=1):
    net = round(float(net), 2)
    vat = round(net * 0.22, 2)                     # Italian standard rate; not recoverable for this body
    add(expense_id=f"C-{k:03d}", date=date.date().isoformat(), category="C3", description=desc, wp=wp,
        supplier=sup, invoice_ref=f"FT-{26000 + k}", net_eur=net, vat_eur=vat, vat_recoverable=False,
        declared_eur=round(net + vat, 2), procurement="direct award")

# planted problems in C3
plant = exp[-len(c3):]
for rec in plant[4:7]:                             # VAT recoverable (commercial testing activity)
    rec["vat_recoverable"] = True
    rec["description"] += " (commercial testing activity)"
for rec in plant[10:12]:                           # invoice missing
    rec["invoice_ref"] = None
plant[15]["other_eu_grant"] = "ERC-DEMO"            # also charged to another EU grant
add(expense_id="C-900", date="2024-12-18", category="C3", description="Cleanroom consumables (delivered before the start)",
    wp="WP2", supplier="Lab supplies distributor", invoice_ref="FT-25999", net_eur=1598.36, vat_eur=351.64,
    vat_recoverable=False, declared_eur=1950.0, procurement="direct award")

# subcontracting (B)
add(expense_id="SC-01", date="2026-03-16", category="B", description="Independent validation of control firmware (task 3.4)",
    wp="WP3", supplier="Software validation firm", invoice_ref="SV-2026-014", net_eur=19672.13, vat_eur=4327.87,
    vat_recoverable=False, declared_eur=24000.0, procurement="negotiated", subcontract_id="SC-01")
add(expense_id="SC-02", date="2025-11-20", category="B", description="Set-up of a data-management platform",
    wp="WP1", supplier="IT services company", invoice_ref="IT-7781", net_eur=7786.89, vat_eur=1713.11,
    vat_recoverable=False, declared_eur=9500.0, procurement="direct award", subcontract_id="SC-02")

# financial charges booked to the project
add(expense_id="F-01", date="2025-02-05", category="bank_charges",
    description="Bank charge on the transfer of the EU pre-financing", wp="WP1", supplier="Bank",
    invoice_ref="BK-0205", net_eur=35.0, vat_eur=0.0, vat_recoverable=False, declared_eur=35.0)
add(expense_id="F-02", date="2026-01-12", category="interest",
    description="Late-payment interest paid to a supplier", wp="WP3", supplier="Cryogenic gas supplier",
    invoice_ref="INT-0112", net_eur=180.0, vat_eur=0.0, vat_recoverable=False, declared_eur=180.0)

expenses = pd.DataFrame(exp, columns=cols)

DATA.mkdir(exist_ok=True)
staff.to_csv(DATA / "staff.csv", index=False)
time_records.to_csv(DATA / "time_records.csv", index=False)
expenses.to_csv(DATA / "expenses.csv", index=False)
print(f"staff: {len(staff)} people · time records: {len(time_records)} rows · expenses: {len(expenses)} lines")
