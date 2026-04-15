#!/usr/bin/env python3
import argparse
import csv
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import pandas as pd
except ImportError as exc:
    raise SystemExit("This script requires pandas. Install it with: pip install pandas") from exc


def normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def restore_blank_headers(columns: List[str]) -> List[str]:
    restored = []
    for col in columns:
        text = str(col)
        if text.startswith("Unnamed:"):
            restored.append("")
        else:
            restored.append(text)
    return restored


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df.columns = restore_blank_headers(list(df.columns))
    return df


def should_preserve_template_value(col_name: str) -> bool:
    key = str(col_name).strip().lower()
    return key.startswith("pad") or "pad" in key or "reserve" in key or key.endswith("_old")


def build_column_map(source_columns: List[str], target_columns: List[str]) -> Tuple[Dict[str, str], List[str]]:
    target_by_norm = {}
    for col in target_columns:
        if col == "":
            continue
        target_by_norm[normalize(col)] = col

    mapping: Dict[str, str] = {}
    unmapped: List[str] = []

    for src in source_columns:
        if src == "":
            continue
        target = target_by_norm.get(normalize(src))
        if target:
            mapping[src] = target
        else:
            unmapped.append(src)

    return mapping, unmapped


def fix_wrapped_byte_fields(row: pd.Series) -> pd.Series:
    # DS3 s8 -> NR/ER u8
    if "categoryPriority" in row.index:
        raw = str(row["categoryPriority"]).strip()
        if raw:
            try:
                value = int(raw)
                if value < 0:
                    row["categoryPriority"] = str(value + 256)
            except ValueError:
                logging.warning("Could not parse categoryPriority: %r", raw)

    # NR/ER-only u8 field; -1 is invalid here
    if "deleteCriteriaDamage" in row.index:
        raw = str(row["deleteCriteriaDamage"]).strip()
        if raw:
            try:
                value = int(raw)
                if value == -1:
                    row["deleteCriteriaDamage"] = "0"
            except ValueError:
                logging.warning("Could not parse deleteCriteriaDamage: %r", raw)

    return row


def write_csv_exact(df: pd.DataFrame, output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    headers = list(df.columns)
    has_blank_trailing_header = bool(headers) and headers[-1] == ""

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)

        for row in df.itertuples(index=False, name=None):
            values = list(row)

            if has_blank_trailing_header and values and values[-1] == "":
                values = values[:-1]

            writer.writerow(values)


def convert(source_csv: Path, target_csv: Path, output_csv: Path) -> None:
    logging.info("Loading DS3 SpEffect CSV: %s", source_csv)
    source_df = load_csv(source_csv)

    logging.info("Loading NR template CSV: %s", target_csv)
    target_df = load_csv(target_csv)

    if target_df.empty:
        raise ValueError("Target/template CSV is empty.")

    template_row = target_df.iloc[0].copy()
    target_columns = list(target_df.columns)
    col_map, unmapped = build_column_map(list(source_df.columns), target_columns)

    logging.info("Mapped %d DS3 columns into NR columns.", len(col_map))
    if unmapped:
        logging.info("%d DS3 columns were not mapped and will be ignored.", len(unmapped))

    converted_rows = []
    for _, srow in source_df.iterrows():
        new_row = template_row.copy()

        for src_col, dst_col in col_map.items():
            if should_preserve_template_value(dst_col):
                continue

            src_val = srow.get(src_col, "")
            if src_val != "":
                new_row[dst_col] = src_val

        new_row = fix_wrapped_byte_fields(new_row)
        converted_rows.append(new_row)

    out_df = pd.DataFrame(converted_rows, columns=target_columns)

    logging.info("Template columns: %d", len(target_columns))
    logging.info("Output columns: %d", len(out_df.columns))
    logging.info("Last template header: %r", target_columns[-1])

    write_csv_exact(out_df, output_csv)
    logging.info("Saved converted CSV to: %s", output_csv)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert DS3 SpEffectParam CSV rows to Nightreign-compatible schema using a Nightreign target/template CSV."
    )
    parser.add_argument("--source", default="SpEffectParam.csv", help="Path to the DS3 source CSV")
    parser.add_argument("--target", default="SpEffectTemplate.csv", help="Path to the Nightreign target/template CSV")
    parser.add_argument("--output", default="SpEffectParam_fixed.csv", help="Path to write the converted CSV")
    parser.add_argument("--debug", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s - %(message)s",
    )

    convert(Path(args.source), Path(args.target), Path(args.output))


if __name__ == "__main__":
    main()
