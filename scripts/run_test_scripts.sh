#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
list_file=".test-files.txt"
find tests -maxdepth 1 -name 'test_*.py' | sort > "$list_file"
while IFS= read -r test_file; do
  echo "RUN $test_file"
  PYTHONPATH=. /mnt/c/Users/Ali_m/OneDrive/Desktop/DocuAgent/.venv/bin/python "$test_file"
done < "$list_file"
rm -f "$list_file"
