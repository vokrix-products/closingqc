import csv
import datetime
import io
import re

import pdfplumber
import openpyxl

VALID_STATUSES = {
    "Valid",
    "Missing",
    "Unsigned",
    "Expired",
    "Flagged",
    "Needs Review",
    "Mismatch",
    "Late",
    "Notary Invalid",
    "Unreadable",
    "Duplicate",
    "Version Mismatch",
    "Cleared",
}


def _normalize_key(value):
    return re.sub(r"[^0-9a-z]+", "_", str(value).strip().lower()).strip("_")


def _safe_cell(value):
    if value is None:
        return ""
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    return str(value).strip()


def _parse_date(value):
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()

    text = str(value).strip()
    if not text:
        return None

    if re.match(r"^\d{4}-\d{2}-\d{2}", text):
        return text[:10]

    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.datetime.strptime(text, fmt).date().isoformat()
        except Exception:
            pass

    return None


def _infer_title(mapping, row_num):
    # Primary entity only. Never document_type or document category.
    priority = [
        "borrower_name",
        "co_borrower_name",
        "supplier",
        "vendor_name",
        "employee_name",
        "patient_name",
        "contract_party",
        "name",
    ]

    for key in priority:
        for original_key, value in mapping.items():
            if _normalize_key(original_key) == key and str(value).strip():
                return str(value).strip()

    for original_key, value in mapping.items():
        if str(value).strip():
            return str(value).strip()

    return f"Record {row_num}"


def _infer_due_date(mapping):
    for key, value in mapping.items():
        if _normalize_key(key) == "due_date":
            parsed = _parse_date(value)
            if parsed:
                return parsed

    for key, value in mapping.items():
        norm = _normalize_key(key)
        if norm in {"closing_date", "disbursement_date", "settlement_date", "date"}:
            parsed = _parse_date(value)
            if parsed:
                return parsed

    for key, value in mapping.items():
        norm = _normalize_key(key)
        if "date" in norm or "due" in norm or "deadline" in norm:
            parsed = _parse_date(value)
            if parsed:
                return parsed

    return None


def _record_from_mapping(mapping, row_num):
    details = {}

    for key, value in mapping.items():
        # due_date must remain top-level only.
        if _normalize_key(key) == "due_date":
            continue

        cell = _safe_cell(value)
        if cell:
            details[str(key)] = cell

    title = _infer_title(mapping, row_num)
    due_date = _infer_due_date(mapping)

    if not details:
        status = "Missing"
    else:
        status = "Needs Review"

    return {
        "title": title,
        "status": status,
        "details": details,
        "due_date": due_date,
    }


def _parse_csv_text(text):
    try:
        reader = csv.reader(io.StringIO(text.strip()))
        rows = list(reader)
    except Exception:
        return []

    if not rows:
        return []

    header = [_safe_cell(value) for value in rows[0]]

    if len(header) <= 1:
        return [
            {"text": _safe_cell(row[0])}
            for row in rows
            if any(str(cell).strip() for cell in row)
        ]

    records = []
    for row in rows[1:]:
        if not any(str(cell).strip() for cell in row):
            continue

        padded = list(row) + [""] * (len(header) - len(row))
        padded = padded[: len(header)]
        records.append(dict(zip(header, padded)))

    return records


def process_file(file_bytes: bytes) -> list[dict]:
    if not isinstance(file_bytes, bytes):
        raise TypeError("file_bytes must be bytes")

    if len(file_bytes) == 0:
        return [
            {
                "title": "Unreadable file",
                "status": "Unreadable",
                "details": {"reason": "Empty file"},
                "due_date": None,
            }
        ]

    # Try PDF first.
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        if text.strip():
            records = _parse_csv_text(text)

            if records:
                return [
                    _record_from_mapping(record, index + 1)
                    for index, record in enumerate(records)
                ]

            first_line = next(
                (line.strip() for line in text.splitlines() if line.strip()),
                "Extracted PDF text",
            )
            return [
                {
                    "title": first_line[:120],
                    "status": "Needs Review",
                    "details": {"text": text.strip()[:2000]},
                    "due_date": None,
                }
            ]
    except Exception:
        pass

    # Try Excel next.
    try:
        workbook = openpyxl.load_workbook(
            io.BytesIO(file_bytes),
            data_only=True,
            read_only=True,
        )
        records = []

        try:
            for sheet in workbook.worksheets:
                rows_iter = sheet.iter_rows(values_only=True)
                first = next(rows_iter, None)

                if first is None:
                    continue

                header = [_safe_cell(value) for value in first]

                for row in rows_iter:
                    if not any(str(cell).strip() for cell in row):
                        continue

                    mapping = dict(zip(header, row))
                    records.append(mapping)
        finally:
            workbook.close()

        if records:
            return [
                _record_from_mapping(record, index + 1)
                for index, record in enumerate(records)
            ]
    except Exception:
        pass

    # Fallback to UTF-8 text or CSV.
    try:
        text = file_bytes.decode("utf-8", errors="ignore").strip()
    except Exception:
        text = ""

    if not text:
        return [
            {
                "title": "Unreadable file",
                "status": "Unreadable",
                "details": {"reason": "No extractable data"},
                "due_date": None,
            }
        ]

    records = _parse_csv_text(text)
    if records:
        return [
            _record_from_mapping(record, index + 1)
            for index, record in enumerate(records)
        ]

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return [
            {
                "title": "Unreadable file",
                "status": "Unreadable",
                "details": {"reason": "No extractable data"},
                "due_date": None,
            }
        ]

    return [
        {
            "title": lines[0][:120],
            "status": "Needs Review",
            "details": {"text": text[:2000]},
            "due_date": None,
        }
    ]
