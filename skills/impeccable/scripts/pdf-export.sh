#!/usr/bin/env bash
# Export a web page to PDF with headless Chrome/Chromium.
# Usage: pdf-export.sh <url-or-html-file> [output.pdf]
# Env: CHROME_BIN (override), CHROME_NO_SANDBOX=1 (containers only), PDF_WAIT_MS (default 5000)
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <url-or-html-file> [output.pdf]" >&2
  exit 2
fi

input=$1
output=${2:-}

chrome=${CHROME_BIN:-}
if [[ -z "$chrome" ]]; then
  for candidate in google-chrome google-chrome-stable chromium chromium-browser; do
    if command -v "$candidate" >/dev/null 2>&1; then
      chrome=$(command -v "$candidate")
      break
    fi
  done
fi
if [[ -z "$chrome" ]]; then
  echo "pdf-export: Chrome/Chromium not found; set CHROME_BIN" >&2
  exit 127
fi

if [[ "$input" != http://* && "$input" != https://* && "$input" != file://* ]]; then
  if [[ ! -f "$input" ]]; then
    echo "pdf-export: not a file or URL: $input" >&2
    exit 1
  fi
  input="file://$(realpath "$input")"
fi

if [[ -z "$output" ]]; then
  output="$(basename "${input%%\?*}")"
  output="${output%.*}.pdf"
fi
output=$(realpath -m "$output")

profile=$(mktemp -d)
trap 'rm -rf "$profile"' EXIT

args=(
  --headless=new
  --disable-gpu
  --no-pdf-header-footer
  --virtual-time-budget="${PDF_WAIT_MS:-5000}"
  --user-data-dir="$profile"
  --print-to-pdf="$output"
)
if [[ "${CHROME_NO_SANDBOX:-0}" == "1" ]]; then
  args+=(--no-sandbox)
fi

"$chrome" "${args[@]}" "$input" >/dev/null 2>&1 || {
  echo "pdf-export: Chrome failed; retry with CHROME_NO_SANDBOX=1 in a container" >&2
  exit 1
}

if [[ ! -s "$output" ]]; then
  echo "pdf-export: no PDF written (blank page, auth, or script error)" >&2
  exit 1
fi

echo "$output"
if command -v pdfinfo >/dev/null 2>&1; then
  pdfinfo "$output" | grep -E '^(Pages|Page size|File size):' || true
fi
