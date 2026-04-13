import argparse
import csv
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import pandas as pd
except ImportError as exc:
    raise SystemExit("This script requires pandas. Install it with: pip install pandas") from exc

# Explicit mappings for known DS3 -> Nightreign AtkParam_Npc field name differences.
# Anything not listed here falls back to normalization-based matching.
EXPLICIT_ALIASES: Dict[str, str] = {
    "spEffect0": "spEffectId0",
    "spEffect1": "spEffectId1",
    "spEffect2": "spEffectId2",
    "spEffect3": "spEffectId3",
    "spEffect4": "spEffectId4",
    "AtkPhys": "atkPhys",
    "AtkMag": "atkMag",
    "AtkFire": "atkFire",
    "AtkThun": "atkThun",
    "AtkStam": "atkStam",
    "AtkThrowEscape": "atkThrowEscape",
    "AtkObj": "atkObj",
    "AtkAttribute": "atkAttribute",
    "GuardAtkRate": "guardAtkRate",
    "GuardBreakRate": "guardBreakRate",
    "GuardRate": "guardRate",
    "GuardCutCancelRate": "guardCutCancelRate",
    "GuardStaminaCutRate": "guardStaminaCutRate",
    "ThrowTypeID": "throwTypeId",
    "damageLevel": "dmgLevel",
    "DefMaterial": "defSeMaterial1",
    # DS3 has one shared field; NR splits it. Put the same value into both later.
    "atkPowForSfxSe": "atkPow_forSfx",
    "atkDirForSfxSe": "atkDir_forSfx",
    # DS3 name -> NR name
    "atkElementCorrectId": "overwriteAttackElementCorrectId",
}

# Nightreign-only defaults/overrides copied from the ER->NR converter pattern
# and kept conservative. Values already present from template remain unless listed here.
FORCED_DEFAULTS: Dict[str, str] = {
    "pad4": "0",
    "pad7_old": "[0|0|0|0]",
    # Sound defaults used by the sample ER->NR script.
    "AppearAiSoundId": "2100",
    "HitAiSoundId": "2010",
}


def normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def load_csv(path: Path) -> pd.DataFrame:
    # Keep everything as strings so IDs/pads are preserved exactly.
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def build_column_map(source_columns: List[str], target_columns: List[str]) -> Tuple[Dict[str, str], List[str]]:
    target_by_norm = {normalize(col): col for col in target_columns}
    mapping: Dict[str, str] = {}
    unmapped: List[str] = []

    for src in source_columns:
        if src in EXPLICIT_ALIASES and EXPLICIT_ALIASES[src] in target_columns:
            mapping[src] = EXPLICIT_ALIASES[src]
            continue

        norm = normalize(src)
        target = target_by_norm.get(norm)
        if target:
            mapping[src] = target
        else:
            unmapped.append(src)

    return mapping, unmapped


def apply_special_cases(src_row: pd.Series, out_row: pd.Series) -> pd.Series:
    # DS3 has one combined atkPowForSfxSe; Nightreign has separate atkPow_forSfx / atkPow_forSe.
    if "atkPowForSfxSe" in src_row.index:
        value = src_row["atkPowForSfxSe"]
        if "atkPow_forSfx" in out_row.index and value != "":
            out_row["atkPow_forSfx"] = value
        if "atkPow_forSe" in out_row.index and value != "":
            out_row["atkPow_forSe"] = value

    # Some DS3 exports use sameAttackJudgmentId where NR uses atkBehaviorId_2 semantics poorly.
    # Do not force this automatically.

    # A few DS3 rows export pad arrays with more bytes than NR's pad7_old. Keep template default.
    return out_row


def convert(ds3_csv: Path, template_csv: Path, output_csv: Path) -> None:
    logging.info("Loading DS3 ATK CSV: %s", ds3_csv)
    src_df = load_csv(ds3_csv)
    logging.info("Loading NR template CSV: %s", template_csv)
    template_df = load_csv(template_csv)

    if template_df.empty:
        raise ValueError("Template CSV has no rows. It should contain at least the default row.")

    template_row = template_df.iloc[0].copy()
    out_columns = list(template_df.columns)
    col_map, unmapped = build_column_map(list(src_df.columns), out_columns)

    logging.info("Mapped %d DS3 columns into NR columns.", len(col_map))
    if unmapped:
        logging.info("%d DS3 columns were not mapped and will be ignored.", len(unmapped))
        for col in unmapped:
            logging.debug("Unmapped source column: %s", col)

    out_rows = []
    for _, src_row in src_df.iterrows():
        new_row = template_row.copy()

        for src_col, dst_col in col_map.items():
            src_val = src_row.get(src_col, "")
            if src_val != "":
                new_row[dst_col] = src_val

        new_row = apply_special_cases(src_row, new_row)

        for col, value in FORCED_DEFAULTS.items():
            if col in new_row.index:
                new_row[col] = value

        out_rows.append(new_row)
        logging.info("Processed DS3 ATK ID: %s", src_row.get("ID", "(no ID)"))

    out_df = pd.DataFrame(out_rows, columns=out_columns)

    unnamed_cols = [col for col in out_df.columns if str(col).startswith("Unnamed")]
    if unnamed_cols:
        out_df = out_df.drop(columns=unnamed_cols)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_csv, index=False, quoting=csv.QUOTE_MINIMAL)
    logging.info("Saved converted CSV to: %s", output_csv)



def find_template(explicit_template: Optional[str]) -> Path:
    if explicit_template:
        path = Path(explicit_template)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {path}")
        return path

    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / "template" / "ATKTemplate.csv",
        script_dir / "ATKTemplate.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Could not find ATKTemplate.csv. Put it next to this script or in a template/ folder, "
        "or pass --template explicitly."
    )



def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Dark Souls 3 AtkParam_Npc CSV rows into a Nightreign-shaped CSV using an NR template."
    )
    parser.add_argument("input", help="Path to DS3 AtkParam_Npc CSV")
    parser.add_argument("output", nargs="?", help="Path to write converted Nightreign CSV")
    parser.add_argument("--template", help="Path to Nightreign ATKTemplate.csv")
    parser.add_argument("--debug", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    template_path = find_template(args.template)
    output_path = Path(args.output) if args.output else input_path.with_name(input_path.stem + "_DS3toNR.csv")

    convert(input_path, template_path, output_path)


if __name__ == "__main__":
    main()
