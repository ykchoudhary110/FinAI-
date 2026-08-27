from dataclasses import dataclass
from typing import List


@dataclass
class LegalDocumentChunk:
    doc_id: str
    statute_name: str
    section_no: str
    effective_date: str
    title: str
    content: str
    topic_tags: List[str]


SEED_LEGAL_CORPUS: List[LegalDocumentChunk] = [
    # ---------------- DIRECT TAXATION: INCOME TAX ACT, 1961 ----------------
    LegalDocumentChunk(
        doc_id="IT_ACT_SEC_87A",
        statute_name="Income Tax Act, 1961",
        section_no="Section 87A",
        effective_date="2025-04-01",
        title="Rebate in Respect of Income-Tax for Individual Taxpayers",
        content=(
            "Under Section 87A of the Income Tax Act 1961 (as amended for Assessment Year 2026-27 / FY 2025-26 under the New Tax Regime), "
            "an individual resident taxpayer whose total income does not exceed ₹12,00,000 is eligible for a tax rebate equal to 100% of income-tax payable, "
            "up to a maximum rebate of ₹60,000. Marginal relief is provided for taxpayers whose net taxable income marginally exceeds ₹12.00 Lakhs."
        ),
        topic_tags=["Income Tax", "Tax Rebate", "Section 87A", "New Tax Regime", "12 lakhs", "60000 rebate"],
    ),
    LegalDocumentChunk(
        doc_id="IT_ACT_SEC_115BAC",
        statute_name="Income Tax Act, 1961",
        section_no="Section 115BAC",
        effective_date="2025-04-01",
        title="Tax Rates Under Default New Tax Regime (FY 2025-26)",
        content=(
            "Section 115BAC specifies the default tax regime rates: Income up to ₹4,00,000 is exempt (0%). "
            "₹4,00,001 to ₹8,00,000 is taxed at 5%. ₹8,00,001 to ₹12,00,000 is taxed at 10%. ₹12,00,001 to ₹16,00,000 is taxed at 15%. "
            "₹16,00,001 to ₹20,00,000 is taxed at 20%. ₹20,00,001 to ₹24,00,000 is taxed at 25%. Income above ₹24,00,000 is taxed at 30%. "
            "A standard deduction of ₹75,000 is allowed for salaried employees under Section 16(ia)."
        ),
        topic_tags=["Income Tax", "Tax Slabs", "Section 115BAC", "Standard Deduction", "75000", "New Tax Regime"],
    ),
    LegalDocumentChunk(
        doc_id="IT_ACT_SEC_80C",
        statute_name="Income Tax Act, 1961",
        section_no="Section 80C",
        effective_date="2024-04-01",
        title="Deductions in Respect of Life Insurance Premia, PF, PPF, ELSS",
        content=(
            "Section 80C allows a deduction from total gross income up to a maximum aggregate ceiling of ₹1,50,000 for investments in "
            "Public Provident Fund (PPF), Employee Provident Fund (EPF), Equity Linked Savings Schemes (ELSS), National Savings Certificates (NSC), "
            "principal repayment of housing loan, and tuition fees for children. Available under Old Tax Regime."
        ),
        topic_tags=["Income Tax", "Section 80C", "PPF", "ELSS", "Deductions", "150000"],
    ),
    LegalDocumentChunk(
        doc_id="IT_ACT_SEC_80D",
        statute_name="Income Tax Act, 1961",
        section_no="Section 80D",
        effective_date="2024-04-01",
        title="Deduction in Respect of Health Insurance Premia",
        content=(
            "Section 80D allows deduction up to ₹25,000 for health insurance premiums paid for self, spouse, and dependent children. "
            "An additional deduction of ₹25,000 is available for parents' insurance, which is enhanced to ₹50,000 if parents are senior citizens (aged 60+). "
            "Preventive health check-up is covered up to ₹5,000 within the overall limit."
        ),
        topic_tags=["Income Tax", "Section 80D", "Health Insurance", "Senior Citizen", "Medical"],
    ),
    LegalDocumentChunk(
        doc_id="IT_ACT_SEC_24B",
        statute_name="Income Tax Act, 1961",
        section_no="Section 24(b)",
        effective_date="2024-04-01",
        title="Deductions from Income from House Property (Interest on Borrowed Capital)",
        content=(
            "Under Section 24(b), interest payable on capital borrowed for the acquisition, construction, repair, or reconstruction of a property "
            "is deductible up to a maximum limit of ₹2,00,000 per financial year for a self-occupied residential property. For let-out properties, actual interest paid is allowed subject to loss set-off limits."
        ),
        topic_tags=["Income Tax", "Section 24(b)", "Home Loan Interest", "House Property", "200000"],
    ),
    LegalDocumentChunk(
        doc_id="IT_ACT_SEC_10_13A",
        statute_name="Income Tax Act, 1961",
        section_no="Section 10(13A)",
        effective_date="2024-04-01",
        title="House Rent Allowance (HRA) Exemption Rules",
        content=(
            "Under Section 10(13A) read with Rule 2A, HRA received by an employee is exempt up to the least of: "
            "(a) Actual HRA received, (b) Rent paid in excess of 10% of salary, or (c) 50% of salary for metro cities "
            "(Mumbai, Delhi, Kolkata, Chennai) and 40% for non-metro cities. Applicable only under the Old Tax Regime."
        ),
        topic_tags=["Income Tax", "HRA", "Section 10(13A)", "Rent Exemption"],
    ),
    LegalDocumentChunk(
        doc_id="IT_ACT_SEC_44ADA",
        statute_name="Income Tax Act, 1961",
        section_no="Section 44ADA",
        effective_date="2024-04-01",
        title="Presumptive Taxation for Professionals (Freelancers, Doctors, CAs, Tech Consultants)",
        content=(
            "Section 44ADA applies to resident professionals. Where gross receipts do not exceed ₹75 Lakhs (if digital receipts >= 95%), "
            "a sum equal to 50% of gross receipts is deemed to be taxable profit. Eliminates requirement to maintain detailed books of account or tax audit under Section 44AB."
        ),
        topic_tags=["Income Tax", "Presumptive Tax", "Section 44ADA", "Freelancer Tax"],
    ),
    LegalDocumentChunk(
        doc_id="IT_ACT_SEC_44AD",
        statute_name="Income Tax Act, 1961",
        section_no="Section 44AD",
        effective_date="2024-04-01",
        title="Presumptive Taxation for Small Businesses and MSMEs",
        content=(
            "Section 44AD allows resident individuals, HUFs, and firms with turnover up to ₹3 Crores (if cash <= 5%) to declare presumptive profits: "
            "6% of digital/banking turnover and 8% on cash turnover. No books of account or Section 44AB audit required."
        ),
        topic_tags=["Income Tax", "Presumptive Tax", "Section 44AD", "MSME Business"],
    ),
    LegalDocumentChunk(
        doc_id="IT_ACT_SEC_111A",
        statute_name="Income Tax Act, 1961",
        section_no="Section 111A",
        effective_date="2024-07-23",
        title="Tax on Short-Term Capital Gains in Equity Shares / Mutual Funds",
        content=(
            "As amended by Finance (No. 2) Act 2024, short-term capital gains arising from the transfer of listed equity shares or units of equity oriented funds "
            "subject to STT are taxed at a flat rate of 20% (increased from the previous 15% rate)."
        ),
        topic_tags=["Income Tax", "Capital Gains", "STCG", "Section 111A", "Budget 2024"],
    ),
    LegalDocumentChunk(
        doc_id="IT_ACT_SEC_112A",
        statute_name="Income Tax Act, 1961",
        section_no="Section 112A",
        effective_date="2024-07-23",
        title="Tax on Long-Term Capital Gains in Listed Equity Shares and Units",
        content=(
            "Under Section 112A, long-term capital gains on listed equity shares or equity mutual funds held for more than 12 months "
            "are taxed at 12.5% on gains exceeding the enhanced annual exemption limit of ₹1,25,00,000 (increased from ₹1,00,000 @ 10% by Budget 2024)."
        ),
        topic_tags=["Income Tax", "Capital Gains", "LTCG", "Section 112A", "Budget 2024"],
    ),
    LegalDocumentChunk(
        doc_id="CBDT_CIRCULAR_04_2024",
        statute_name="CBDT Circular No. 04/2024",
        section_no="Circular 04/2024",
        effective_date="2024-04-15",
        title="Deduction of Tax at Source from Salaries under Section 192",
        content=(
            "Clarifies that employers must seek intimation from employees regarding their chosen tax regime (Old vs Default New Regime). "
            "If no choice is communicated, TDS must be deducted using the default New Regime rates under Section 115BAC with ₹75,000 standard deduction."
        ),
        topic_tags=["Income Tax", "TDS", "CBDT Circular", "Salary TDS", "Section 192", "Circular 04/2024"],
    ),

    # ---------------- INDIRECT TAXATION: CGST ACT, 2017 & GST RULES ----------------
    LegalDocumentChunk(
        doc_id="CGST_ACT_SEC_16",
        statute_name="Central Goods and Services Tax Act, 2017",
        section_no="Section 16",
        effective_date="2024-10-01",
        title="Eligibility and Conditions for Taking Input Tax Credit (ITC)",
        content=(
            "Section 16(2) provides that registered persons can claim ITC only if: (a) in possession of tax invoice/debit note, "
            "(b) details are communicated by supplier in GSTR-1 and reflected in GSTR-2B, (c) goods/services are received, "
            "(d) tax charged has been actually paid to Government, and (e) valid return under Section 39 is furnished. "
            "Payment must be made to the supplier within 180 days from invoice date, else ITC must be reversed with Section 50 interest."
        ),
        topic_tags=["GST", "Input Tax Credit", "Section 16", "ITC Conditions", "GSTR-2B", "tax invoice possession", "GSTR-3B"],
    ),
    LegalDocumentChunk(
        doc_id="CGST_ACT_SEC_17_5",
        statute_name="Central Goods and Services Tax Act, 2017",
        section_no="Section 17(5)",
        effective_date="2024-04-01",
        title="Blocked Credits — Ineligible Input Tax Credit Categories",
        content=(
            "Section 17(5) explicitly disallows ITC on: (a) Motor vehicles for transport of persons with seating capacity <= 13 (except when used for taxable supply of vehicles or passenger transport), "
            "(b) Food, beverages, outdoor catering, beauty treatment, health services, and club memberships, (c) Works contract services for construction of immovable property (except plant & machinery), "
            "(d) Goods/services used for personal consumption, and (e) Goods lost, stolen, destroyed, written off, or disposed of by way of gift or free samples."
        ),
        topic_tags=["GST", "Blocked Credit", "Section 17(5)", "Ineligible ITC", "motor vehicles", "club memberships"],
    ),
    LegalDocumentChunk(
        doc_id="CGST_ACT_SEC_31",
        statute_name="Central Goods and Services Tax Act, 2017",
        section_no="Section 31",
        effective_date="2024-01-01",
        title="Tax Invoice Provisions and Mandatory Particulars under Rule 46",
        content=(
            "Section 31 read with Rule 46 requires every registered supplier to issue a Tax Invoice containing: "
            "(a) Supplier name, address, GSTIN; (b) Consecutive serial number <= 16 characters; (c) Date of issue; "
            "(d) Recipient GSTIN/UIN; (e) HSN/SAC code; (f) Description and quantity of goods/services; (g) Total value & taxable value; "
            "(h) Rate & amount of CGST, SGST, IGST; (i) Place of supply; and (j) Digital signature / signature."
        ),
        topic_tags=["GST", "Tax Invoice", "Section 31", "Rule 46", "B2B Invoice", "Mandatory Details"],
    ),
    LegalDocumentChunk(
        doc_id="CGST_RULE_86B",
        statute_name="CGST Rules, 2017",
        section_no="Rule 86B",
        effective_date="2024-04-01",
        title="Restrictions on Use of Amount Available in Electronic Credit Ledger",
        content=(
            "Rule 86B mandates that a registered person whose taxable supply value in a month exceeds ₹50 Lakhs (excluding exempt/zero-rated supplies) "
            "cannot use Electronic Credit Ledger (ITC) to discharge more than 99% of total output tax liability. At least 1% must be discharged through Electronic Cash Ledger."
        ),
        topic_tags=["GST", "Rule 86B", "Credit Ledger", "Cash Payment Mandate"],
    ),
    LegalDocumentChunk(
        doc_id="CGST_ACT_SEC_54",
        statute_name="Central Goods and Services Tax Act, 2017",
        section_no="Section 54",
        effective_date="2024-04-01",
        title="Refund of Tax and Unutilized Input Tax Credit",
        content=(
            "Section 54 permits refund claims within 2 years from relevant date for: (a) Zero-rated export supplies, (b) Inverted duty structure (inputs tax rate higher than output tax rate), "
            "(c) Excess cash balance in electronic cash ledger. Application is filed in FORM GST RFD-01. Provisional refund of 90% is granted within 7 days in RFD-04 for exports, and final order passed within 60 days in RFD-06."
        ),
        topic_tags=["GST", "Refund", "Section 54", "Inverted Duty Structure", "RFD-01", "Exports"],
    ),
    LegalDocumentChunk(
        doc_id="CBIC_CIRCULAR_186",
        statute_name="CBIC Circular No. 186/18/2022-GST",
        section_no="Circular 186/2022",
        effective_date="2022-12-27",
        title="Clarification on E-Invoicing, IRN Generation and Dynamic QR Codes",
        content=(
            "Mandates Invoice Reference Number (IRN) generation via Invoice Registration Portal (IRP) for B2B supplies where aggregate turnover exceeds notified thresholds. "
            "Failure to generate IRN renders the invoice invalid under Rule 48(5), disentitling the buyer from claiming ITC."
        ),
        topic_tags=["GST", "E-Invoicing", "IRN", "Circular 186", "QR Code", "Rule 48(5)"],
    ),

    # ---------------- LANDMARK SUPREME COURT RULINGS ----------------
    LegalDocumentChunk(
        doc_id="SC_RULING_SAFARI_RETREATS",
        statute_name="Supreme Court of India Ruling",
        section_no="Civil Appeal No. 2948/2023",
        effective_date="2024-10-03",
        title="Chief Commissioner of Central Goods & Service Tax v. M/s Safari Retreats Pvt. Ltd.",
        content=(
            "The Supreme Court affirmed that Section 17(5)(d) cannot be interpreted universally to deny ITC on shopping malls and commercial buildings constructed for leasing. "
            "Applied the 'functionality test' to determine if the building qualifies as 'plant' for the business of renting commercial spaces."
        ),
        topic_tags=["Supreme Court", "Safari Retreats", "Section 17(5)(d)", "Commercial Building ITC", "Mall ITC"],
    ),
    LegalDocumentChunk(
        doc_id="SC_RULING_BHARTI_AIRTEL",
        statute_name="Supreme Court of India Ruling",
        section_no="Civil Appeal No. 6520/2021",
        effective_date="2021-10-28",
        title="Union of India v. Bharti Airtel Ltd. & Anr.",
        content=(
            "The Supreme Court held that taxpayers cannot unilaterally rectify FORM GSTR-3B returns of past tax periods based on subsequent reconciliation with FORM GSTR-2A. "
            "Reaffirmed that ITC eligibility is an entitlement subject to strict statutory verification mechanisms."
        ),
        topic_tags=["Supreme Court", "Bharti Airtel", "GSTR-3B Rectification", "GSTR-2A", "ITC Reconciliation"],
    ),

    # ---------------- GST BOOK CHAPTERS (CONCEPTS & PRACTICES 2024) ----------------
    LegalDocumentChunk(
        doc_id="GST_BOOK_CH1_SLABS",
        statute_name="GST Concepts & Practices (2024) / CGST Act 2017",
        section_no="Chapter 1.17",
        effective_date="2024-01-01",
        title="Four-Tier GST Rate Slabs & Structure in India",
        content=(
            "GST operates on a 4-tier rate structure: (1) Zero Rate (0%): Essential food items, fresh milk, eggs, unbranded paneer, curd, educational & health services; "
            "(2) Lower Rate (5%): Sugar, tea, edible oils, domestic LPG, cashew nuts, spices, footwear <= ₹500, GTA transport; "
            "(3) Standard Rate (12% & 18%): Processed food, butter, computers, monitors (18%), IT services (18%), commercial rent (18%); "
            "(4) Higher Rate (28%): Luxury goods, air conditioners, automobiles, cement, with Compensation Cess on demerit goods."
        ),
        topic_tags=["GST", "GST Rates", "Slabs", "0%", "5%", "12%", "18%", "28%"],
    ),
    LegalDocumentChunk(
        doc_id="GST_BOOK_CH2_COMPOSITE_MIXED",
        statute_name="GST Concepts & Practices (2024) / CGST Act 2017",
        section_no="Section 2(30) & Section 2(74)",
        effective_date="2024-01-01",
        title="Composite Supply vs. Mixed Supply & Tax Liability",
        content=(
            "Composite Supply (Sec 2(30)): Two or more taxable supplies naturally bundled and supplied together where one is principal supply (e.g. laptop with charger, hotel stay with breakfast). "
            "Taxed at the rate of the Principal Supply. Mixed Supply (Sec 2(74)): Two or more individual supplies bundled for a single price not naturally bundled (e.g. gift hamper with chocolates, dry fruits and aerated drinks). "
            "Taxed at the Highest Rate of tax among the bundled items."
        ),
        topic_tags=["GST", "Composite Supply", "Mixed Supply", "Principal Supply", "Section 2(30)", "Section 2(74)"],
    ),
    LegalDocumentChunk(
        doc_id="GST_BOOK_CH2_COMPOSITION",
        statute_name="GST Concepts & Practices (2024) / CGST Act 2017",
        section_no="Section 10",
        effective_date="2024-01-01",
        title="Composition Scheme Eligibility, Turnover Limits & Tax Rates",
        content=(
            "Section 10 Composition Scheme is an optional simplified tax scheme for small taxpayers with aggregate turnover up to ₹1.5 Crores (₹1 Crore for Special Category States). "
            "Tax rates: Manufacturers pay 1% (0.5% CGST + 0.5% SGST), Restaurant/Catering pays 5% (2.5% + 2.5%), Other traders pay 1%. "
            "Composition dealers cannot make inter-state outward supplies, cannot collect GST on invoices, cannot issue tax invoices (must issue Bill of Supply), and cannot claim Input Tax Credit (ITC)."
        ),
        topic_tags=["GST", "Composition Scheme", "Section 10", "Bill of Supply", "Small Business"],
    ),
    LegalDocumentChunk(
        doc_id="GST_BOOK_CH3_TIME_OF_SUPPLY",
        statute_name="GST Concepts & Practices (2024) / CGST Act 2017",
        section_no="Sections 12, 13 & 14",
        effective_date="2024-01-01",
        title="Time of Supply (TOS) for Goods and Services",
        content=(
            "Time of Supply determines when GST liability arises. For Goods (Sec 12): Earlier of date of issue of invoice (or last date required to issue invoice under Sec 31) or date of payment entry. "
            "For Services (Sec 13): If invoice issued within 30 days of service completion, TOS is earlier of invoice date or payment date; if invoice not issued within 30 days, TOS is date of service completion. "
            "Under RCM, TOS is earlier of date of receipt of goods, date of payment, or 30 days (goods) / 60 days (services) from invoice date."
        ),
        topic_tags=["GST", "Time of Supply", "Section 12", "Section 13", "Invoice Due Date", "RCM"],
    ),
    LegalDocumentChunk(
        doc_id="GST_BOOK_CH3_PLACE_OF_SUPPLY",
        statute_name="GST Concepts & Practices (2024) / IGST Act 2017",
        section_no="Sections 10, 11, 12, 13, 14",
        effective_date="2024-01-01",
        title="Place of Supply (POS) and Determination of CGST+SGST vs. IGST",
        content=(
            "Place of Supply determines tax jurisdiction: Intra-state supply (same state) attracts CGST+SGST; Inter-state supply attracts IGST. "
            "Goods with movement (Sec 10(1)(a)): Location of goods when movement terminates for delivery. Immovable property services (Sec 12(3)): Location of the property. "
            "Restaurant & catering (Sec 12(4)): Location where service is actually performed. Telecommunications (Sec 12(11)): Location of fixed line or billing address. Online OIDAR services (Sec 14): Location of non-taxable recipient."
        ),
        topic_tags=["GST", "Place of Supply", "IGST", "CGST", "SGST", "Interstate", "Intrastate"],
    ),
    LegalDocumentChunk(
        doc_id="GST_BOOK_CH3_VALUE_OF_SUPPLY",
        statute_name="GST Concepts & Practices (2024) / CGST Act 2017",
        section_no="Section 15 & Rules 27-31",
        effective_date="2024-01-01",
        title="Value of Taxable Supply & Transaction Value Rules",
        content=(
            "Section 15(1) establishes that GST is payable on Transaction Value. Inclusions (Sec 15(2)): Non-GST taxes, duties, packing charges, freight, commission, and delayed payment interest/late fees. "
            "Exclusions (Sec 15(3)): In-bill discounts recorded on invoice, and post-supply discounts agreed before supply where recipient reverses attributable ITC. "
            "For related party or non-monetary supplies, Valuation Rules 27 to 31 apply (Open Market Value, Like Kind & Quality, Cost + 10% markup, or Residual method)."
        ),
        topic_tags=["GST", "Valuation", "Transaction Value", "Section 15", "Discounts", "Rules 27-31"],
    ),
    LegalDocumentChunk(
        doc_id="GST_BOOK_CH3_ISD",
        statute_name="GST Concepts & Practices (2024) / CGST Act 2017",
        section_no="Section 2(61) & Section 20",
        effective_date="2024-01-01",
        title="Input Service Distributor (ISD) Mechanism and Credit Distribution",
        content=(
            "Input Service Distributor (ISD) is a corporate/head office that receives tax invoices for common input services and distributes CGST, SGST, and IGST credit to manufacturing/operational units sharing the same PAN. "
            "Credit is distributed pro-rata based on the turnover of each recipient unit during the relevant period. Mandatory separate ISD registration is required."
        ),
        topic_tags=["GST", "Input Service Distributor", "ISD", "Section 20", "Credit Distribution"],
    ),
    LegalDocumentChunk(
        doc_id="GST_BOOK_CH4_ELECTRONIC_LEDGERS",
        statute_name="GST Concepts & Practices (2024) / CGST Act 2017",
        section_no="Section 49 & Rules 85-87",
        effective_date="2024-01-01",
        title="Three Electronic Ledgers: Cash (PMT-05), Credit (PMT-02), and Liability (PMT-01)",
        content=(
            "Under Section 49, three electronic registers are maintained on the GST portal: "
            "(1) Electronic Cash Ledger (FORM GST PMT-05): Displays cash deposits made via challan PMT-06 (valid 15 days); used to pay tax, interest, late fees, and penalties. "
            "(2) Electronic Credit Ledger (FORM GST PMT-02): Self-assessed ITC from GSTR-3B; can ONLY be utilized for paying output tax. "
            "(3) Electronic Liability Register (FORM GST PMT-01): Records all tax demands and return liabilities."
        ),
        topic_tags=["GST", "Electronic Ledgers", "Cash Ledger", "Credit Ledger", "Section 49", "PMT-05", "PMT-02"],
    ),
    LegalDocumentChunk(
        doc_id="GST_BOOK_CH7_GST_COUNCIL_NAA",
        statute_name="GST Concepts & Practices (2024) / CGST Act 2017",
        section_no="Article 279A & Section 171",
        effective_date="2024-01-01",
        title="GST Council Voting Structure & National Anti-Profiteering Authority (NAA)",
        content=(
            "GST Council (Article 279A): Decisions require a 75% weighted majority. Central Government holds 1/3rd (33.3%) weightage, and State Governments together hold 2/3rd (66.7%) weightage. "
            "Anti-Profiteering (Section 171): Mandates that any reduction in GST rates or benefit of Input Tax Credit must be passed on to consumers via commensurate reduction in prices. Violations attract penalties and prosecution."
        ),
        topic_tags=["GST", "GST Council", "Article 279A", "Anti-Profiteering", "Section 171", "NAA"],
    ),
    LegalDocumentChunk(
        doc_id="PWC_RESIDENTIAL_STATUS",
        statute_name="PwC Worldwide Tax Summaries / Income Tax Act 1961",
        section_no="Section 6 (Residence in India)",
        effective_date="2026-05-12",
        title="Residential Status (ROR, RNOR, NR) and Scope of Total Income",
        content=(
            "Taxation of individuals in India depends on residential status: (1) Resident and Ordinarily Resident (ROR) - taxed on worldwide income wherever received; "
            "(2) Resident but Not Ordinarily Resident (RNOR) - taxed only on Indian income, deemed Indian income, or income from business controlled in India; "
            "(3) Non-Resident (NR) - taxed strictly on income earned or received in India. Foreign income of RNOR and NR is exempt from Indian tax."
        ),
        topic_tags=["Income Tax", "PwC Summary", "Residential Status", "ROR", "NR", "Foreign Income"],
    ),
    LegalDocumentChunk(
        doc_id="PWC_SURCHARGE_CESS_RULES",
        statute_name="PwC Worldwide Tax Summaries / Finance Act",
        section_no="Surcharge & Health Cess",
        effective_date="2025-04-01",
        title="Surcharge Slabs, Marginal Relief and 4% Health & Education Cess",
        content=(
            "Surcharge on individual income: Above ₹50 Lakh to ₹1 Crore: 10%; Above ₹1 Crore to ₹2 Crore: 15%; Above ₹2 Crore to ₹5 Crore: 25%; "
            "Above ₹5 Crore: 25% under New Regime (capped) and 37% under Old Regime. Surcharge on Long-Term Capital Gains (LTCG) is capped at 15%. "
            "Health and Education Cess of 4% is levied on total tax plus surcharge."
        ),
        topic_tags=["Income Tax", "Surcharge", "Cess", "PwC", "High Net Worth"],
    ),
]
