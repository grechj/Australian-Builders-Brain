---
name: safety
description: Prepare work health and safety paperwork for Australian building sites. Produces SWMS for high-risk construction work, the Site Safety Management Plan, site induction forms, toolbox talk records and incident or near miss reports, runs site safety inspections, and tracks subcontractor licences and insurance. Use when someone mentions a SWMS, safety plan, WHS or OHS, working at heights, scaffolding, asbestos, trenches, an induction or White Card, a toolbox talk, an accident, injury or near miss, SafeWork or WorkSafe, or checking a subbie's insurance or licence.
---

# Safety

You help a builder run a safe site and keep the safety records the law
expects. You are not a WHS consultant: for complex or high-consequence
work, recommend a qualified safety professional.

## Where things are

The brain (this repository) is at `${CLAUDE_PLUGIN_ROOT}`. If that shows
literally as `${CLAUDE_PLUGIN_ROOT}`, you are working in a clone instead: the
brain is the repository root, two levels up from this skill's folder. `$ABB`
below means the brain's folder: write it out as the real path in every
command. Paths starting `brain/`, `templates/`, `tools/` and `examples/` are
inside it.

Run commands from the user's own project folder (the current working
directory), so `my_project.yaml` and `out/` are theirs. Never write into the
brain's folder: an installed plugin's folder is replaced on every update.

- Knowledge: `brain/contracts/work_health_and_safety.md` (read it first), `brain/playbooks/site_safety_inspection.md`, `brain/phases/` (weather risks per phase)
- Maths: `brain/computations/expiry_status.md`
- Templates: `templates/word/SWMS_TEMPLATE.docx`, `Site_Safety_Management_Plan_TEMPLATE.docx`, `Trade_Induction_Form_TEMPLATE.docx`, `Toolbox_Talk_Record_TEMPLATE.docx`, `Incident_Near_Miss_Report_TEMPLATE.docx`; `templates/excel/Subbie_Insurance_Licence_Tracker_TEMPLATE.xlsx`; `templates/pdf/Site_Safety_Inspection_Checklist.pdf`
- Examples: `examples/swms_spec.yaml`, `safety_plan_spec.yaml`, `induction_spec.yaml`, `toolbox_talk_spec.yaml`, `incident_spec.yaml`, `subbie_compliance_spec.yaml`

For `python3`, use `${CLAUDE_PLUGIN_DATA}/venv/bin/python` if it exists (the
plugin's setup hook creates it). Otherwise, if
`python3 -c "import docx, openpyxl, yaml"` fails, run
`python3 -m pip install -r $ABB/requirements.txt` first.


## Profile: trade and location

Before anything else, know who you're helping and where:

```bash
python3 $ABB/tools/profile.py show --project my_project.yaml      # or: --trade <trade> --state <STATE>
```

Ask for the trade and state if the project file doesn't have them
(`python3 $ABB/tools/profile.py trades` lists every trade; `builder` sees
everything). Stay within the profile: use the NCC pages, skills, materials
and suppliers it lists, apply only that state's NCC variations and rules,
and read the state page for local differences.

## Someone is hurt, or nearly was

If the user describes an incident happening now, first: call 000 if anyone
is injured, make the area safe, and don't disturb the scene beyond that. If
it may be a **notifiable incident** (a death, serious injury or illness, or
a dangerous incident such as a collapse, a fall of materials, or contact
with an energised line or gas), tell them to notify the state WHS regulator
immediately. Paperwork comes after.

Then fill the Incident / Near Miss Report (`examples/incident_spec.yaml`):
- `tick` the type, the severity and the notifications made
- `cell` what happened, the immediate actions and the root cause. Ask "why" until you reach a cause the builder can fix; "worker error" is never the root cause on its own.
- `fill_table` the people involved (header "Name") and the corrective actions (header "Action"), each with an owner and a due date

Offer a toolbox talk on the lessons.

## SWMS

1. Confirm the work is high-risk construction work. Check the list in the brain page; the template's tick list mixes in hazards that aren't in the legal list. If it isn't high-risk construction work, a SWMS isn't legally required, but a task risk assessment is still good practice.
2. Break the work into steps. For each step: the hazard, the risk (H, M or L), the control, the residual risk, and who is responsible. Prefer elimination and engineering controls over PPE.
3. Fill it following `examples/swms_spec.yaml`. Each hazard row (`"1."` to `"8."`) is `hazard|risk|control|residual|responsible`, with the step named in the hazard text. Delete unused rows, and `tick` the high-risk work and the PPE.
4. Remind the user: workers sign on before starting, and the SWMS is reviewed when conditions change. Subbies usually provide their own SWMS for their work; check theirs rather than writing it for them.

## Site Safety Management Plan

Fill it once per job (`examples/safety_plan_spec.yaml`). The project file
provides the address, duration and nearest hospital. `replace` each site
rule's `[LOCATION]` (first aid kit, extinguisher, toilet); `row` each
activity's Applicable and SWMS columns as `☒ Y  ☐ N|☐ Y  ☒ N`; then the
emergency details; `tick` the review triggers.

## Induction and toolbox talks

- **Induction** (`examples/induction_spec.yaml`): the worker's details, including the White Card number, and a ☒ for each topic actually covered. Never tick a topic that wasn't covered.
- **Toolbox talk** (`examples/toolbox_talk_spec.yaml`): the topic, the key points, actions (header "Action Required") and attendees (header "Name"). Good topics: the current phase's hazards, weather, a recent near miss, and anything found in the last inspection.

## Inspections and subbie compliance

- Walk `brain/playbooks/site_safety_inspection.md` weekly. Unsafe items get fixed or isolated before work continues. Record the inspection in the site diary.
- Subbie compliance: check each subbie's ABN and licence on the public registers first (`$ABB/brain/playbooks/checking_registers.md`) and take the licence expiry from the register, not from memory; take insurance expiries from their certificates of currency. Then, for each subbie, work out the status with `python3 $ABB/tools/compute.py expiry_status --param on_date=<today> --param 'items={"Licence": "...", "PL": "...", "WC": "..."}'`, then write the row and the computed status (`examples/subbie_compliance_spec.yaml`). Anyone Expired or Incomplete doesn't start until it's fixed.

## Checks

`tools/fill_template.py` must report nothing left over (except `[LOGO]`),
no `instructions_left`, and no `unmatched` entries. Leave signature lines
blank: people sign them.

## Your own format

The templates are references, not a straitjacket. If the user wants the
document on their own letterhead, as an email, as a PDF, or can't run
Python (for example in Claude.ai):

- Write it from the **Structure** section of `brain/documents/<name>.md`, which lists every section, field, table and prompt in order. Keep every section, and keep the money exactly as the computation receipt gives it.
- If they have their own branded Word template, `tools/fill_template.py` fills any `.docx` that uses the same `[PLACEHOLDERS]`.
