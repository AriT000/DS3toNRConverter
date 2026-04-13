#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def build_column_lookup(columns):
    lookup = {}
    for col in columns:
        key = str(col).strip().lower()
        if key not in lookup:
            lookup[key] = col
    return lookup


def should_preserve_template_value(col_name: str) -> bool:
    key = str(col_name).strip().lower()
    return (
        key.startswith("pad")
        or "pad" in key
        or "reserve" in key
        or key.endswith("_old")
    )


def convert(source_csv: Path, target_csv: Path, output_csv: Path) -> None:
    source_df = normalize_columns(pd.read_csv(source_csv, dtype=str, keep_default_na=False))
    target_df = normalize_columns(pd.read_csv(target_csv, dtype=str, keep_default_na=False))

    if target_df.empty:
        raise ValueError('Target/template CSV is empty.')

    template_row = target_df.iloc[0].copy()
    target_columns = list(target_df.columns)
    source_lookup = build_column_lookup(source_df.columns)

    converted_rows = []
    for _, srow in source_df.iterrows():
        new_row = template_row.copy()

        for tcol in target_columns:
            if should_preserve_template_value(tcol):
                continue

            source_col = source_lookup.get(str(tcol).strip().lower())
            if source_col is not None:
                new_row[tcol] = srow[source_col]

        converted_rows.append(new_row)

    out_df = pd.DataFrame(converted_rows, columns=target_columns)

    # unnamed_cols = [c for c in out_df.columns if str(c).startswith('Unnamed')]
    # if unnamed_cols:
    #     out_df = out_df.drop(columns=unnamed_cols)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_csv, index=False)


def main():
    parser = argparse.ArgumentParser(
        description='Convert DS3 SpEffectParam CSV rows to Nightreign-compatible schema using a Nightreign target/template CSV.'
    )
    parser.add_argument(
        '--source',
        default='SpEffectParam_midir.csv',
        help='Path to the DS3 source CSV (default: SpEffectParam_midir.csv)',
    )
    parser.add_argument(
        '--target',
        default='SpEffectParam_caligo.csv',
        help='Path to the Nightreign target/template CSV (default: SpEffectParam_caligo.csv)',
    )
    parser.add_argument(
        '--output',
        default='SpEffectParam_midir_DS3toNR.csv',
        help='Path to write the converted CSV (default: SpEffectParam_midir_DS3toNR.csv)',
    )
    args = parser.parse_args()

    convert(Path(args.source), Path(args.target), Path(args.output))
    print(f'Converted CSV written to: {args.output}')


if __name__ == '__main__':
    main()
