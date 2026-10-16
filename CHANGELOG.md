# Changelog

All notable changes to the Australian Builder's Brain. Versions follow the
plugin version in `.claude-plugin/plugin.json`.

## 0.6.1 (2026-10-17)

- Skills work when installed as a plugin: they find the brain at the plugin's folder, run from the user's own project folder, and never write into the plugin.
- A SessionStart hook builds a Python environment for the tools in the plugin's data folder, and rebuilds it only when `requirements.txt` changes.
- `LICENSE` is the standard MIT text, so GitHub recognises it; the scope note (MIT for code, CC BY 4.0 for everything else) is in the README.
- Plugin manifest: display name, version, homepage and licence.
- Added this changelog.

## 0.6.0 (2026-10-17)

- NCC 2022 loaded from the ABCB PDFs, with Amendments 1 and 2 merged as notices under the clauses they change; profiles and lookups take `--edition`.
- Trade and location profiles: 22 trades plus `builder`/`all`, 8 states and territories, each filtering the NCC, skills, takeoffs, materials and suppliers.
- Materials skill: takeoffs (deck, framing, electrical, plumbing, roofing and more), per-user price lists, an optional Bunnings API client with the user's own keys, and a rough order of magnitude estimate.
- Retired BEAM branding removed; templates documented as references for your own documents.

## 0.5.0 (2026-10-16)

- Ten document skills covering all templates: variations, claims, notices, handover, estimating, contracts, site, safety and financials, plus the ncc skill.
- NCC 2025 (v1.2) loaded from the ABCB XML.
- Template formula fixes: Setup references, final account retention, rain days, budget variance, quote acceptance fields, markup labels.
- CI: OKF lint plus example, profile, price list and takeoff tests on every push.

## 0.1.0 (2026-10-16)

- Scaffold: OKF v0.2 brain, lifecycle and phase pages, templates, fill tool, MIT and CC BY 4.0 licences.
