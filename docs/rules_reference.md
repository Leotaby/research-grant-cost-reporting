# Rules reference

The rules the tool applies, with their sources. The grant agreement signed for a project, and the
conditions of its call, always prevail over this summary.

Main source: European Commission, *EU Grants: AGA – Annotated Grant Agreement*, version 2.0,
1 April 2025. The AGA annotates the corporate model grant agreement (MGA) used by Horizon Europe
and the other EU programmes of 2021-2027; article numbers below are those of the MGA.

## 1. When is a cost eligible? (MGA Art. 6.1)

An actual cost is eligible only if it meets all seven general conditions:

1. it is actually incurred by the beneficiary;
2. it is incurred in the period set out in Article 4 (the action duration);
3. it is declared under one of the budget categories in Article 6.2 and Annex 2;
4. it is incurred in connection with the action described in Annex 1 and is necessary for it;
5. it is identifiable and verifiable;
6. it complies with the applicable national law on taxes, labour and social security;
7. it is reasonable, justified and complies with the principle of sound financial management.

Checks R01 (period) and R05 (supporting documents) apply conditions 2 and 5 directly.

## 2. Personnel costs (MGA Art. 6.2.A)

- Cost = daily rate × day-equivalents worked on the action, rounded to the nearest half-day.
- Daily rate = annual personnel costs for the person / 215.
- The total day-equivalents declared in EU grants for a person and a year cannot exceed 215
  (check R02). The tool adds the days the person declared on other EU grants.
- If the financial year is not closed when the report is prepared, the daily rate of the last
  closed financial year is used. In the demo, days worked in 2026 are costed at the 2025 rate.
- Time worked must be supported by reliable time records (MGA Art. 20): monthly timesheets, or
  monthly day-declarations for people working only on the action, signed by the person and the
  supervisor (check R03).

## 3. Purchase costs and subcontracting (MGA Art. 6.2.B and 6.2.C)

- **Travel and subsistence (C.1):** eligible in line with the beneficiary's usual travel practices.
  Business class where the rules allow economy is flagged for a decision (W01), because costs
  beyond usual practice can be rejected as excessive (Art. 6.3).
- **Equipment (C.2):** by default only depreciation is eligible: the depreciable amount is spread
  over the useful life, starting when the asset is available for use; only the share of actual
  use for the action counts; the total charged can never exceed the purchase price (check R04).
  Some calls allow the full cost instead; the Data Sheet says which option applies.
- **Other goods, works and services (C.3):** consumables, publication fees, conference fees,
  services bought from third parties.
- **Subcontracting (B):** action tasks carried out by a third party must be set out in Annex 1.
  Subcontracts not foreseen there need an amendment or approval under the simplified procedure
  (check W02; MGA Art. 5.5 and 6.2.B).
- **Purchasing rules:** purchases must give best value for money and avoid conflicts of interest.
  Beneficiaries that are contracting authorities, such as Italian universities, must also follow
  national public procurement law (section 6).

## 4. Indirect costs (MGA Art. 6.2.E)

Indirect costs (overheads) are a flat rate of the eligible direct costs; no supporting documents
are needed for them.

| Scheme | Flat rate | Base |
| --- | --- | --- |
| Horizon Europe | 25% | Eligible direct costs (A-D) excluding subcontracting, financial support to third parties and exempted categories |
| Corporate MGA, standard option | 7% | Eligible direct costs (A-D) excluding volunteers' costs and exempted categories |

Every ineligible direct cost in the base therefore also removes 25% (or 7%) on top. Run the tool
with `--programme STANDARD` to see the same data under the 7% rule.

## 5. Ineligible costs (MGA Art. 6.3)

Never eligible, among others: return on capital and dividends; debt and debt service charges;
provisions for future losses or debts; interest owed (check R09); currency exchange losses;
bank costs charged for transfers from the granting authority (check R08); excessive or reckless
expenditure; deductible or refundable VAT (check R06); costs incurred during a suspension of the
grant agreement; in-kind contributions by third parties, by default; and costs declared under
another EU grant (check R07).

## 6. Italian law that applies alongside the grant agreement

- **Public procurement:** D.Lgs. 31 marzo 2023, n. 36 (*Codice dei contratti pubblici*),
  Art. 50(1): supplies and services below EUR 140 000 can be awarded directly (letter b); from
  EUR 140 000 up to the EU thresholds a negotiated procedure with at least five operators is
  required (letter e). Check W03 flags direct awards at or above EUR 140 000. (Text as amended by
  D.Lgs. 209/2024.)
- **Projects co-funded by EU cohesion funds** (ERDF, ESF+, managed by national or regional
  authorities, for example national research programmes): the eligibility rules are those of
  Regulation (EU) 2021/1060 and of DPR 10 marzo 2025, n. 66, in force since 23 May 2025 (it replaced
  DPR 22/2018, which still applies to 2014-2020 programmes). Two differences from the grant
  agreement rules above:
  - staff costs at an hourly rate = latest documented annual gross employment costs / 1 720 hours
    (pro rata for part-time; Reg. 2021/1060, Art. 55(2)(a)), instead of a daily rate on 215 days;
  - VAT is eligible only where it is not recoverable by the beneficiary; fines, penalties,
    late-payment interest and exchange losses are not eligible.

## 7. Certificate and record keeping

- **Certificate on the financial statements (CFS):** in Horizon Europe it is required with the
  final report when the requested EU contribution (actual costs) reaches EUR 430 000
  (EUR 725 000 for beneficiaries with a systems and process audit). Other programmes set the
  threshold in the Data Sheet.
- **Records:** keep supporting documents for 5 years after the payment of the balance (3 years for
  grants of up to EUR 60 000), as set in the Data Sheet (MGA Art. 20).

## Sources

- European Commission, *EU Grants: AGA – Annotated Grant Agreement*, version 2.0, 1 April 2025,
  EU Funding & Tenders Portal:
  https://ec.europa.eu/info/funding-tenders/opportunities/docs/2021-2027/common/guidance/aga_en.pdf
- European Commission, *How to prepare a successful proposal in Horizon Europe: the rules of the
  game, the Model Grant Agreement* (presentation, 24 March 2021): daily rate on 215 days,
  depreciation by default, 25% indirect costs, CFS threshold.
- Regulation (EU) 2021/1060 (Common Provisions Regulation), Art. 55; Commission Notice C/2024/7467
  on simplified cost options, section 2.3.2: https://eur-lex.europa.eu/eli/C/2024/7467/oj
- DPR 10 marzo 2025, n. 66, GU n. 105 of 8 May 2025:
  https://www.normattiva.it/eli/id/2025/05/08/25G00073/ORIGINAL
- D.Lgs. 31 marzo 2023, n. 36, Art. 50: https://www.brocardi.it/nuovo-codice-appalti/art50.html
