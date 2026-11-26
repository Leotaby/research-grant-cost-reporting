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
- Daily rate = actual personnel costs during the months within the reporting period ÷ maximum
  declarable day-equivalents. The maximum is 215 ÷ 12 × the number of months within the reporting
  period × the working-time factor, rounded to the nearest half-day (AGA, annotations to
  Art. 6.2.A.1). For a full year of full-time work the rate comes to annual personnel costs ÷ 215.
- The rate is calculated per person for the reporting period. It may be calculated separately for
  each calendar year within the period if that is done consistently, which is what the tool does.
- Two ceilings apply (check R02). A person cannot declare more day-equivalents than the maximum for
  the period, because no more than 100% of the personnel costs can be declared. And the total
  declared in EU grants for a person and a calendar year cannot exceed 215; the tool adds the days
  the person declared on other EU grants.
- Time worked must be supported by declarations signed monthly by the person and the supervisor,
  unless a reliable time-recording system is in place (MGA Art. 20; check R03).
- The rate of the "last closed financial year" belongs to a different option, average personnel
  costs declared as unit costs. It does not apply to actual costs.

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

### Co-funded actions

The EU funding rate is not always 100%. Most Chips JU calls are co-funded by the Joint Undertaking
and the participating states: the EU contribution covers a share of the eligible costs and national
authorities can fund part of the rest under their own rules, so the same costs are reported twice,
once under each set of rules. The demo uses an EU funding rate of 50%.

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

## 7. Reporting deadlines, payments, audit certificate and records

These are the standard time limits; the Data Sheet of each grant agreement sets the ones that apply.

- **Continuous reporting (MGA Art. 21; Data Sheet 4.1):** deliverables, milestones and critical
  risks are reported in the Funding & Tenders Portal throughout the action.
- **Periodic report (Art. 21; Data Sheet 4.2):** due within 60 days after the end of each
  reporting period, with a technical part and a financial part. Each beneficiary fills in and
  signs its own financial statement in the Portal; the coordinator assembles the report and
  submits it.
- **Payments (Art. 22):** the granting authority pays within 90 days of receiving the report. The
  deadline is suspended while it waits for missing information.
- **Final report:** submitted with the last periodic report, within 60 days after the end of the
  action; the payment of the balance follows.
- **Certificate on the financial statements (CFS; Art. 24; Data Sheet 4.3):** in Horizon Europe
  it is required when the EU contribution a beneficiary requests reaches EUR 430 000 over the
  whole action (EUR 725 000 for beneficiaries with an approved systems and process audit). The
  whole requested contribution counts: unit costs, flat rates such as the 25% for indirect costs,
  and lump sums are not examined in the certificate, but they are included in the threshold
  calculation. It is submitted only with the final report, or when a beneficiary's participation
  ends, and it is issued by a qualified external auditor or, for public bodies, by a competent and
  independent public officer. Other programmes set the threshold in the Data Sheet.
- **Records (Art. 20):** keep supporting documents for 5 years after the payment of the balance
  (3 years for grants of up to EUR 60 000).
- **Audits (Art. 25):** the granting authority can start checks, reviews and audits during the
  action and up to 2 years after the payment of the balance.
- **National co-funding:** where a national authority funds part of the costs, its grant decree
  sets its own reporting deadlines and certification requirements.

`grantcheck/deadlines.py` turns these time limits into a calendar for the project and checks the
beneficiary's position against the CFS threshold.

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
- European Commission, project officer's presentation at the kick-off of a Horizon Europe project
  (OSCARS, 14 March 2024): report due 60 days after the period ends, payment within 90 days, CFS
  only at final reporting, audits up to 2 years after the balance:
  https://indico.in2p3.fr/event/32021/sessions/20402/attachments/83288/123981/20240314-KoM-EC-Officer-OSCARS-EnricoPellizzari.pdf
- European Commission, Common Audit Service (DG Research and Innovation), presentation on the
  certificate on the financial statements in Horizon Europe, 26 June 2024: the threshold is
  calculated on the total EU contribution requested, flat rates included:
  https://www.gov.si/assets/ministrstva/MVZI/Znanost/Obzorje-Evropa/Pravna-in-financna-vprasanja/CFS-HE_2024.pdf
- FFG, Austrian national contact point, "Certificate on the Financial Statements (CFS) in Horizon
  Europe": https://ffg.at/en/europe/heu/legal-financial/cfs
- Chips Joint Undertaking, *Annual activity report 2024*, "Chips for Europe Initiative calls":
  https://aar2024.chips-ju.europa.eu/annual-report/chips-for-europe-initiative-calls
