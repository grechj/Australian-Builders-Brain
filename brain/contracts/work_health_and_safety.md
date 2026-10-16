---
type: Contract Topic
title: Work health and safety on site
description: "The builder's core WHS duties on a residential site: high-risk construction work and SWMS, the site safety plan, inductions, toolbox talks, inspections, incidents and subcontractor compliance."
tags: [safety, whs, swms, induction, incidents]
status: draft
jurisdiction: [NSW, VIC, QLD, WA, SA, TAS, ACT, NT]
sources:
  - id: swa_hrcw
    resource: https://www.safeworkaustralia.gov.au/safety-topic/industry-and-business/construction
    title: Safe Work Australia, Construction
    author: org:safe_work_australia
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
stale_after: 2027-04-16T00:00:00Z
---

> **Draft, to verify.** Most states and territories use laws based on the
> model WHS Act and Regulations. Victoria has its own OHS Act and
> Regulations, with similar but not identical duties. Check the regulator's
> guidance for the job's state before relying on specifics.

The builder in control of the site has the primary duty to keep workers,
visitors and the public safe, so far as is reasonably practicable. It
can't be contracted away to the subbies, though they have duties too.

# High-risk construction work and SWMS

A Safe Work Method Statement is required before **high-risk construction
work** starts.[^swa_hrcw] The model WHS Regulations list the categories.
Common ones on houses:

- Risk of a person falling more than 2 m
- Demolition of load-bearing parts of a structure
- Disturbing or likely to disturb asbestos
- Structural alterations or repairs needing temporary support
- Trenches or shafts deeper than 1.5 m, and tunnels
- Work near energised electrical installations or services, or near gas mains and pipelines
- Work in or near confined spaces
- Work on or next to a road or railway, or where powered mobile plant is moving
- Tilt-up or precast concrete

The [SWMS template](/documents/swms.md) also offers "hot works" and
"crane/lifting operations". These are hazards that need controls, but they
aren't high-risk construction work in themselves unless they fall in a
listed category (for example powered mobile plant). The list above sets
when a SWMS is legally required.

A SWMS describes the work in steps, the hazards and risks of each step, and
the controls. Use the strongest practical controls first: eliminate, then
substitute or isolate, then engineering, then administrative controls, with
PPE last. Workers must read and sign on before starting, and it must be
followed and reviewed when the work or conditions change. Subcontractors
usually prepare the SWMS for their own work; the builder checks it.

# Site safety plan, induction and toolbox talks

- The [Site Safety Management Plan](/documents/site_safety_management_plan.md) records site rules, high-risk work, emergency arrangements, first aid and the nearest hospital.
- Every worker gets a site [induction](/documents/trade_induction_form.md) before starting, and must hold a general construction induction (White Card).
- [Toolbox talks](/documents/toolbox_talk_record.md) cover current risks (working at height, manual handling, weather, a recent near miss) and record who attended.
- Inspect the site regularly with the [site safety inspection](/playbooks/site_safety_inspection.md) playbook.

# Incidents

Record every incident and near miss in the
[Incident / Near Miss Report](/documents/incident_near_miss_report.md),
including the root cause and corrective actions.

**Notifiable incidents** (a death, a serious injury or illness, or a
dangerous incident such as a collapse, a fall of materials or contact with
an energised line) must be reported to the state WHS regulator immediately,
and the site must not be disturbed until the regulator allows it, except to
help an injured person or make the area safe. Call 000 first when someone
is hurt.

# Subcontractor compliance

Before a subbie starts, check:
- A current trade licence for the work
- Public liability insurance
- Workers compensation (for employees), or personal accident cover for sole traders, as required
- A SWMS for any high-risk work
- Inducted workers

Track expiry dates in the
[Subbie Insurance and Licence Tracker](/documents/subbie_insurance_licence_tracker.md),
with the status from the [expiry status](/computations/expiry_status.md)
computation.

[^swa_hrcw]: Safe Work Australia, Construction
