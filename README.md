# ClosingQC

ClosingQC is a document QC (quality control) processor. It ingests closing/mortgage-style document files, extracts structured records, and flags each record for review status.

## Archetype

Backend document processing pipeline. The core is a pure function, `process_file(file_bytes: bytes) -> list[dict]`, that converts raw file bytes into a normalized list of records. It is designed to be driven by an external poller/worker that feeds files and consumes structured output.

## What the poller does

The poller watches an input source (queue, storage bucket, or directory) for new files and passes each file as raw bytes to `process_file`. It then persists or forwards the returned records.

## Poller input expectations

- Input is raw file bytes (`bytes`).
- Supported formats: PDF, Excel (`.xlsx`), CSV, and plain UTF-8 text.
- The poller must read the file fully into memory and pass it as `bytes` to `process_file`.
- Empty input (`b""`) is valid and returns an `Unreadable` record rather than raising.

## Output shape

`process_file` returns a `list[dict]`. Each record has exactly these top-level keys:

- `title` — the primary entity (borrower, supplier, vendor, etc.). Never the document type or category.
- `status` — one of the valid status values below.
- `details` — a dict of cleaned, non-empty field values for that record. `due_date` is never placed inside `details`.
- `due_date` — ISO date string (`YYYY-MM-DD`) or `null`. Always top-level.

### Valid statuses

Valid, Missing, Unsigned, Expired, Flagged, Needs Review, Mismatch, Late, Notary Invalid, Unreadable, Duplicate, Version Mismatch, Cleared.

## Files

- `processor.py`: provides `process_file(file_bytes)` for PDF, Excel, CSV, and plain text extraction.
- `run_demo.py`: hardcoded CSV demonstration; exits `0` on success.
- `run_tests.py`: unit tests covering top-level `due_date`, CSV fallback, `details` shape, status values, and unreadable input.

## Required Python packages

- openai
- requests
- pdfplumber
- openpyxl

## Running

- Demo: `python3 run_demo.py`
- Tests: `python3 run_tests.py`

Dashboard: https://closingqc.vokrix.co
Vercel: closingqc
Railway: closingqc
