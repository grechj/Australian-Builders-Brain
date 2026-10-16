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

## NCC 2022

Don't use the ABCB's NCC 2022 XML download. It's an older publishing export
("adopted from 1 September 2022") with one file per clause: clauses that
share a code and title across volumes overwrote each other, the map and
Part files are skeletons, and it predates Amendments 1 and 2. Use the
ABCB's NCC 2022 PDFs instead (`python3 tools/ncc_pdf_ingest.py --pdf-dir <folder>`); the run also merges
Amendments 1 and 2 from `tools/ncc2022_amendments.yaml`.

NCC 2022 attribution (required): "The National Construction Code 2022 was
provided by the Australian Building Codes Board under the CC BY 4.0
licence." Images, photographs, trade marks and third-party material are
excluded from the licence and aren't reproduced.
