# Data: fictional project QPL-DEMO

Everything in this folder is invented: the project, the department, the people (identified only by
role) and the amounts. `scripts/make_synthetic_data.py` regenerates it.

QPL-DEMO is a 48-month research and innovation action (January 2025 to December 2028) on a pilot
line for superconducting quantum devices, set up like a Chips JU action: Horizon Europe cost rules,
an EU contribution of 50% of the eligible costs, the rest from national co-funding or own
resources. The files describe one partner, a university physics department, in reporting period 1
(January 2025 to June 2026).

## Files

| File | Content |
| --- | --- |
| `project.json` | Duration, reporting periods, budget by cost category, work packages with planned person-months, subcontracts listed in Annex 1, travel rule, national direct-award threshold |
| `staff.csv` | One row per person: role, contract and, for each calendar year, the personnel costs of the months that fall in the reporting period (gross pay plus employer contributions and taxes on pay), the number of those months the person was employed, and the days declared on other EU grants. Pay did not change in the first half of 2026 |
| `time_records.csv` | Days worked per person, month and work package; record type (monthly declaration of days, or timesheet from the time-recording system); signed by the person and by the supervisor |
| `deliverables.csv` | Deliverables and milestones from Annex 1: id, title, work package, due month, date submitted. Their status is measured on the day the periodic report is due, 60 days after the period ends |
| `expenses.csv` | Ledger of purchase costs, subcontracting and charges booked to the project: date, category, supplier, invoice, net amount, VAT and whether it is recoverable, amount declared, procurement procedure; equipment price, useful life, date available and share of use; flight class and economy fare; subcontract id; other EU grant charged |

Budget categories follow the EU grant agreement: A personnel, B subcontracting, C.1 travel and
subsistence, C.2 equipment, C.3 other goods, works and services, D other cost categories,
E indirect costs.

## Problems planted on purpose

The data contains 18 problems of the kinds an audit finds. `tests/test_statement_and_data.py` checks
that the tool finds every one of them, and nothing else.

| Line | Problem | Check |
| --- | --- | --- |
| S05, 2025 | Monthly day-declarations for September and October never signed | R03 |
| S10, 2026 | March and April timesheets not countersigned by the supervisor | R03 |
| S08, 2025 | 234 days declared in the year, above the 215 cap | R02 |
| S09, 2025 | 162 days on this action plus 70 on another EU grant | R02 |
| E-01 | Signal generator declared at the full price instead of depreciation | R04 |
| E-06 | Network analyser depreciated at 100% use instead of 70% | R04 |
| C-005 to C-007 | VAT included although the department can recover it | R06 |
| C-011, C-012 | No invoice reference | R05 |
| C-016 | Also charged to another EU grant | R07 |
| C-900 | Consumables delivered before the action started | R01 |
| F-01 | Bank charge on the transfer of the EU pre-financing | R08 |
| F-02 | Late-payment interest paid to a supplier | R09 |
| T-019 | Business-class flight; the travel rule allows economy | W01 (at risk) |
| SC-02 | Subcontract not listed in Annex 1 | W02 (at risk) |
| E-04 | EUR 150 000 probe station bought by direct award | W03 (at risk) |
