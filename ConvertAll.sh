#!/usr/bin/env bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONVERTERS_DIR="${ROOT_DIR}/Converters"
INPUT_DIR="${ROOT_DIR}/input"
OUTPUT_DIR="${ROOT_DIR}/output"

mkdir -p "${OUTPUT_DIR}"

if [[ ! -d "${CONVERTERS_DIR}" ]]; then
  echo "Missing Converters directory: ${CONVERTERS_DIR}" >&2
  exit 1
fi

if [[ ! -d "${INPUT_DIR}" ]]; then
  echo "Missing input directory: ${INPUT_DIR}" >&2
  exit 1
fi

find_script() {
  local folder="$1"
  local script

  script="$(find "${folder}" -maxdepth 1 -type f \( -name 'DS3toNR_*.py' -o -name 'ERtoNR_*.py' \) | sort | head -n 1 || true)"
  if [[ -z "${script}" ]]; then
    return 1
  fi
  printf '%s\n' "${script}"
}

find_template() {
  local folder="$1"
  local template

  template="$(find "${folder}" -maxdepth 1 -type f -name '*Template.csv' | sort | head -n 1 || true)"
  if [[ -z "${template}" ]]; then
    return 1
  fi
  printf '%s\n' "${template}"
}

run_converter() {
  local folder_path="$1"
  local folder_name
  local script_path
  local template_path
  local input_path
  local output_path

  folder_name="$(basename "${folder_path}")"

  script_path="$(find_script "${folder_path}")" || {
    echo "Skipping ${folder_name}: no converter script found." >&2
    return 0
  }

  template_path="$(find_template "${folder_path}")" || {
    echo "Skipping ${folder_name}: no template CSV found." >&2
    return 0
  }

  input_path="${INPUT_DIR}/${folder_name}.csv"
  output_path="${OUTPUT_DIR}/${folder_name}.csv"

  if [[ ! -f "${input_path}" ]]; then
    echo "Skipping ${folder_name}: missing input file ${input_path}" >&2
    return 0
  fi

  echo "==> ${folder_name}"
  echo "    script:   $(basename "${script_path}")"
  echo "    template: $(basename "${template_path}")"
  echo "    input:    $(basename "${input_path}")"
  echo "    output:   $(basename "${output_path}")"

  python "${script_path}" "${input_path}" "${output_path}" --template "${template_path}"
}

while IFS= read -r -d '' folder; do
  run_converter "${folder}"
done < <(find "${CONVERTERS_DIR}" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

echo "All params converted! Outputs are in the 'output' folder."