# NCC source data

The ABCB publishes the National Construction Code as structured XML under a
Creative Commons Attribution 4.0 licence:

- NCC 2022: https://data.gov.au/data/dataset/national-construction-code-ncc-2022
- NCC 2025 (v1.2): https://data.gov.au/data/dataset/national-construction-code-2025-version-1-2

Unzip each zip into its own folder here, named after the zip:

    raw/ncc/ncc-2025-volume-two-v1.2/contents.xml
    raw/ncc/ncc-2025-housing-provisions-v1.2/contents.xml
    ...

then convert them to brain pages:

    python3 tools/ncc_ingest.py --edition 2025

The XML and the figures (about 75 MB) are git-ignored. The converted pages
in `brain/ncc/2025/` are committed.

Attribution, required by the licence:
© Commonwealth of Australia and the States and Territories of Australia,
published by the Australian Building Codes Board, licensed under CC BY 4.0.
