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


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def should_preserve_template_value(col_name: str) -> bool:
    key = str(col_name).strip().lower()
    return key.startswith("pad") or "pad" in key or "reserve" in key or key.endswith("_old")


def build_column_map(source_columns: List[str], target_columns: List[str]) -> Tuple[Dict[str, str], List[str]]:
    target_by_norm = {normalize(col): col for col in target_columns}
    mapping: Dict[str, str] = {}
    unmapped: List[str] = []

    for src in source_columns:
        target = target_by_norm.get(normalize(src))
        if target:
            mapping[src] = target
        else:
            unmapped.append(src)

    return mapping, unmapped


def fix_signed_byte_fields(row: pd.Series) -> pd.Series:
    """
    Fix DS3 -> Nightreign fields that are stored differently.

    shootAngleXZ:
    - DS3 can export this as wrapped unsigned byte values like 241, 236, 231
    - Nightreign expects a signed byte range
    - Convert values > 127 into signed-byte equivalents by subtracting 256
    """
    field = "shootAngleXZ"

    if field in row:
        raw = str(row[field]).strip()
        if raw != "":
            try:
                value = int(raw)
                if value > 127:
                    fixed = value - 256
                    logging.debug("%s: %s -> %s", field, value, fixed)
                    row[field] = str(fixed)
            except ValueError:
                logging.warning("Could not parse %s value: %r", field, raw)

    return row


def convert(source_csv: Path, target_csv: Path, output_csv: Path) -> None:
    logging.info("Loading DS3 Bullet CSV: %s", source_csv)
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

        new_row = fix_signed_byte_fields(new_row)
        converted_rows.append(new_row)

    out_df = pd.DataFrame(converted_rows, columns=target_columns)

    unnamed_cols = [c for c in out_df.columns if str(c).startswith("Unnamed")]
    if unnamed_cols:
        out_df = out_df.drop(columns=unnamed_cols)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_csv, index=False, quoting=csv.QUOTE_MINIMAL)
    logging.info("Saved converted CSV to: %s", output_csv)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert DS3 Bullet CSV rows to Nightreign-compatible schema using a Nightreign target/template CSV."
    )
    parser.add_argument("--source", default="Bullet_midir.csv", help="Path to the DS3 source CSV")
    parser.add_argument("--target", default="Bullet_caligo.csv", help="Path to the Nightreign target/template CSV")
    parser.add_argument("--output", default="Bullet_midir_DS3toNR.csv", help="Path to write the converted CSV")
    parser.add_argument("--debug", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s - %(message)s",
    )

    convert(Path(args.source), Path(args.target), Path(args.output))


if __name__ == "__main__":
    main()
