---
type: Playbook
title: Checking ABNs, licences and insurance
description: How to check an ABN on ABN Lookup, a licence on each state's public register, and insurance from a certificate of currency, for the user's own business and for subbies and suppliers.
tags: [playbooks, compliance, abn, licensing, insurance, subcontractors]
status: draft
jurisdiction: [NSW, VIC, QLD, WA, SA, TAS, ACT, NT]
sources:
  - id: access_canberra_tradesperson
    resource: https://www.accesscanberra.act.gov.au/consumer-rights/choosing-a-tradesperson
    title: Choosing a tradesperson (Access Canberra)
  - id: act_construction_licences
    resource: https://www.planning.act.gov.au/professionals/regulation-and-responsibilities/construction-licences
    title: Construction licences (ACT Government)
  - id: act_residential_insurance
    resource: https://www.planning.act.gov.au/community/build-or-renovate/before-you-start/building-contracts/residential-building-work-insurance
    title: Residential building work insurance (ACT Government)
  - id: nsw_licence_check
    resource: https://www.service.nsw.gov.au/transaction/check-builder-or-tradespersons-licence
    title: Check a builder or tradesperson licence (Service NSW)
  - id: qbcc_find
    resource: https://www.qbcc.qld.gov.au/uk/node/7086
    title: Find a licensed contractor (QBCC)
  - id: bpc_find
    resource: https://www.bpc.vic.gov.au/tools/find-practitioner
    title: Find a practitioner (Building and Plumbing Commission)
  - id: wa_licence_search
    resource: https://www.wa.gov.au/organisation/building-and-energy/building-and-energy-licence-and-registration-search
    title: Building and Energy licence and registration search (WA)
  - id: sa_find_licence
    resource: https://www.cbs.sa.gov.au/find-a-licence-holder
    title: Find a licence holder (Consumer and Business Services SA)
  - id: tas_find
    resource: https://cbos.tas.gov.au/find-a-licensed-tradesperson
    title: Find a licensed tradesperson (Tasmania)
  - id: nt_bpb
    resource: https://ntlis.nt.gov.au/building-practitioners/
    title: Building Practitioners Board registration check (NT)
generated: { by: claude/opus-5.5, at: 2026-10-21T00:00:00Z }
stale_after: 2027-04-21T00:00:00Z
---

> **Draft, to verify.** Register addresses change when regulators are renamed
> or move to new systems. If a link below doesn't work, search the
> regulator's site for "licence search" or "public register" and update this
> page.

Three checks, in this order, whenever the brain takes on a business's
details: the user's own at setup, and a subbie's or supplier's when they're
engaged or their first invoice arrives.

1. **ABN**: is it real, active, whose is it, and is it registered for GST?
2. **Licence**: is it current, the right class for the work, and in the right name?
3. **Insurance**: is the cover current, for enough, and in the right name?

Claude does the lookups on the public pages with its web tools, only when the
user asks or agrees, and records what it saw (`tools/start.py check` for the
user's own; the Subbie Insurance and Licence Tracker for subbies). Nothing is
looked up in the background. If a page can't be read (some registers are
search forms that need a browser), give the user the link and ask them to
read out what it shows, or use the browser if the session has one.

# 1. ABN

Use [ABN Lookup](https://abr.business.gov.au), the Australian Business
Register's public search. A single ABN's page is
`https://abr.business.gov.au/ABN/View?abn=<11 digits, no spaces>`.

Record:

- **Entity name** and any business or trading names
- **ABN status**: active, or cancelled from a date
- **GST**: registered from a date, or not registered
- **Main business location** (state and postcode)

What it means:

- **Checksum first.** `tools/start.py` and the inbox already reject an ABN that fails the ATO's check digit. That catches typos, not cancelled ABNs.
- **Cancelled, or not found:** don't pay a supplier or subbie against it until it's sorted. Paying an enterprise that doesn't quote an ABN can mean withholding 47% (see [accounts and tax](/contracts/accounts_and_tax.md)).
- **Not registered for GST:** they must not charge GST, and you can't claim a GST credit for any they do charge. For the user's own business, check the profile's `gst_registered` agrees.
- **Name differs from the business name:** fine if it's a registered trading name, but a tax invoice has to identify the supplier, so make sure the invoice name and ABN belong together.

The ABR also has a free web services API (it needs a registered key). The
brain doesn't use it: the public page is enough, and it keeps the brain free
of keys.

# 2. Licence

Each state and territory runs its own register.[^access_canberra_tradesperson][^nsw_licence_check][^qbcc_find][^bpc_find][^wa_licence_search][^sa_find_licence][^tas_find][^nt_bpb]

| State | Register | What it covers | Notes |
|---|---|---|---|
| ACT | [Access Canberra public registers](https://services.accesscanberra.act.gov.au/s/public-registers): [builders](https://services.accesscanberra.act.gov.au/s/public-registers/construction-licences?registerid=licensed-builders), [electricians](https://services.accesscanberra.act.gov.au/s/public-registers/construction-licences?registerid=electricians-public-register), [plumbers](https://services.accesscanberra.act.gov.au/s/public-registers/construction-licences?registerid=plumbers), [gasfitters](https://services.accesscanberra.act.gov.au/s/public-registers/construction-licences?registerid=gasfitters), [drainers](https://services.accesscanberra.act.gov.au/s/public-registers/construction-licences?registerid=drainers) | Construction occupation licences | Shows status, including expired, suspended and cancelled, and disciplinary action on the Details tab. Asbestos licences are on WorkSafe ACT's register. |
| NSW | [Check a builder or tradesperson licence](https://www.service.nsw.gov.au/transaction/check-builder-or-tradespersons-licence) (Service NSW, for NSW Fair Trading) | Building and trade licences | Search by name, licence number, ABN, ACN or location. |
| VIC | [Find a practitioner](https://www.bpc.vic.gov.au/tools/find-practitioner) (Building and Plumbing Commission) | Building practitioners and plumbers | Shows status, the work they can do, and conditions. Electricians are licensed separately (Energy Safe Victoria). |
| QLD | [QBCC licensee register](https://my.qbcc.qld.gov.au/myQBCC/s/qbcc-licensee-register) | QBCC licences | Search by name or licence number; shows the licence history. Electricians are licensed separately (Electrical Safety Office). |
| WA | [Online Licence Search](https://ols.demirs.wa.gov.au/search) (Building and Energy) | Builders, building surveyors, plumbers, electricians, painters | Registered practitioners and contractors can share a number: match the name, number and licence type. |
| SA | [Find a licence holder](https://secure.cbs.sa.gov.au/OccLicPubReg/LicenceSearch.php) (Consumer and Business Services) | Builders, plumbers, electricians, gas fitters and other occupations | |
| TAS | [Find a licensed tradesperson](https://cbos.tas.gov.au/find-a-licensed-tradesperson) | Licensed building and trade occupations | The page now redirects to Consumer Affairs Tasmania; check the address. |
| NT | [Building Practitioners Board registration check](https://ntlis.nt.gov.au/building-practitioners/) | Registered building practitioners | Electricians and plumbers have their own boards. |

Record: licence number, holder's name, **class or type** (and any
endorsements or conditions), **status**, and **expiry**. Then check:

- **Status is current**, not suspended, cancelled or expired.
- **The class covers the work.** For example, ACT builder licences run from Class A (unlimited) to Class D (non-structural basic building work), and specialist work such as demolition and pool installation needs an endorsement.[^act_construction_licences]
- **The name matches** the business you're dealing with. A company or partnership may need its own licence, not just a licensed director or nominee.

**Not every trade needs a licence.** In the ACT, carpenters and bricklayers
don't currently need one: builders, electricians, plumbers, drainers and
gasfitters do.[^act_construction_licences] Other states license more trades,
often above a dollar value. Don't assume: check the state's licensing page
for the trade, and if no licence is needed record that (`--result
not_required`) so the brain stops asking.

# 3. Insurance

Ask for a **certificate of currency** for each policy and record the
insurer, policy number, cover and expiry. Check the insured's name matches,
the cover is enough (subcontract agreements commonly ask for $10M or $20M of
public liability), and the expiry is after the work finishes.

- **Public liability:** almost always required by head contractors and clients.
- **Workers compensation:** compulsory for employers, through each state's scheme. A sole trader with no employees may not have it; check what the contract asks.
- **Home warranty (residential building insurance):** required in most states for residential building work above a threshold, issued per job, and must be in place before the work starts. In the ACT it covers houses and apartment buildings of three storeys or fewer; from 1 January 2025 the minimum cover is $200,000, and a fidelity certificate from an approved fidelity fund can be used instead of a policy. The builder must have it before applying for a commencement notice and give the owner evidence of it.[^act_residential_insurance]
- **Contract works and professional indemnity:** often asked for on larger or design-and-construct jobs.

The brain keeps the user's own policies in `profile.yaml` (`tools/start.py
insurance`) and warns 30 days before any expires, using the
[expiry status](/computations/expiry_status.md) computation. Subbies' policies
go in the [Subbie Insurance and Licence Tracker](/documents/subbie_insurance_licence_tracker.md).

[^access_canberra_tradesperson]: Access Canberra, Choosing a tradesperson.
[^act_construction_licences]: ACT Government, Construction licences.
[^act_residential_insurance]: ACT Government, Residential building work insurance.
[^nsw_licence_check]: Service NSW, Check a builder or tradesperson licence.
[^qbcc_find]: QBCC, Find a licensed contractor.
[^bpc_find]: Building and Plumbing Commission, Find a practitioner.
[^wa_licence_search]: WA Building and Energy, licence and registration search.
[^sa_find_licence]: Consumer and Business Services SA, Find a licence holder.
[^tas_find]: Tasmania, Find a licensed tradesperson.
[^nt_bpb]: NT Building Practitioners Board, registration check.
