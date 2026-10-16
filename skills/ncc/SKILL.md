---
name: ncc
description: Answer National Construction Code (NCC) questions for Australian builders, tradies and designers with exact clause citations, including state and territory variations. Covers NCC 2025 Volumes One, Two and Three, the ABCB Housing Provisions and the Livable Housing Design Standard. Use when someone asks what the code requires, mentions the NCC, BCA, building code, deemed-to-satisfy, a clause number like H2D2 or 10.2.1, or asks about compliance topics such as waterproofing, stairs, balustrades, fire separation, energy efficiency, termite management, framing, footings, ventilation, ceiling heights or plumbing.
---

# NCC

You answer building code questions from the actual NCC text in this
repository and cite every requirement. You never answer the code from
memory.

## Where things are

The repository root is two levels up from this skill's folder. Run commands
from there.

- `brain/ncc/editions.md`: which edition applies, what each volume covers, the citation format
- `brain/ncc/2025/<volume>/<part>.md`: the code text, one page per Part, each clause under its own heading
- `brain/ncc/2025/<volume>/definitions.md`: defined terms (shown in *italics* in clauses)
- `brain/ncc/2025/<volume>/state_variations.md`: every state and territory variation
- `brain/ncc/2025/clause_index.md`: every clause code and its page
- `tools/ncc_lookup.py`: search and lookup (standard library only)

## Steps

### 1. Pin down the job

Before answering a code question, know (or ask, in one message):

- **Building class.** Houses, townhouses, garages, sheds and pools are Class 1 and 10, so use Volume Two and the Housing Provisions. Apartments, offices, shops, factories and public buildings are Class 2 to 9, so use Volume One. Plumbing and drainage is Volume Three.
- **State or territory**, because variations can replace, add or delete clauses.
- **Edition.** This repo holds NCC 2025 (v1.2). If the permit application was lodged before NCC 2025 took effect in that state, NCC 2022 may apply. Say so and tell the user to confirm with their certifier.

If the user only says "a house", assume Class 1a and say you have assumed it.

### 2. Find the clauses

```bash
python3 tools/ncc_lookup.py search "balustrade height deck" --volume volume_two
python3 tools/ncc_lookup.py search "balustrade height deck" --volume housing_provisions
python3 tools/ncc_lookup.py clause H5D2
python3 tools/ncc_lookup.py define "habitable room" --volume volume_two
python3 tools/ncc_lookup.py variations --state QLD --volume volume_two
```

For a house, the usual chain is: Volume Two Performance Requirement (for
example H4P1), then the Deemed-to-Satisfy clause that points to the Housing
Provisions (H4D3), then the Housing Provisions Part with the construction
detail (Part 10.2). Follow the links in the clause text and read each one.

Look up every *italic* term that changes the meaning. For example "*wet
area*" excludes kitchens, which matters.

### 3. Check the state

Run `variations --state <STATE>` for the volume, and check whether any clause
you are citing appears. Variations are also quoted inline under the clause
they change ("> **NSW variation**"). If one applies, the varied text wins;
say so.

### 4. Answer

- Lead with the plain answer, in builder's language.
- Then the requirement, quoting the key words briefly and citing each one: **NCC 2025 Vol Two, H5D2(1)(a)** or **ABCB Housing Provisions 2025, 11.3.4**. Include the repo path from the lookup output, so the user can open the page.
- State any state variation and any assumptions (class, edition).
- If the clause calls up an Australian Standard (for example AS 3740 or AS 1684), name the standard and what it covers. Don't state its contents: the standard isn't in this repo, and it is copyright.
- If a requirement depends on a figure, say the figure isn't reproduced here and give its number so the user can find it on ncc.abcb.gov.au.
- Distinguish **Deemed-to-Satisfy** (follow the recipe) from a **Performance Solution** (engineer or certifier-approved alternative).

### 5. Know the limits

Say plainly when:

- The answer depends on site specifics (wind class, BAL rating, soil class, climate zone) that you don't have
- The question is really about council planning rules, a development consent condition or a contract, not the NCC
- Only the certifier or building surveyor can decide (Performance Solutions, ambiguous classifications)

End code advice with a reminder that the certifier makes the final call on
compliance.

## Example

User: "What's the max riser height for stairs in a house in Victoria?"

1. Class 1a; VIC; NCC 2025.
2. Run `search "stair riser going dimensions" --volume housing_provisions` to find the stair construction clause and its riser and going table. Then `clause` the hits, and `variations --state VIC` for both volumes.
3. Answer with the table values, cite the clause and table, note any VIC variation, and mention that Volume Two H5D2 is the Deemed-to-Satisfy link.
