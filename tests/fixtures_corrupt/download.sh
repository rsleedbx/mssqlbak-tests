#!/usr/bin/env bash
# Download SQLskills corrupt-database BAK files from Paul Randal's demo page.
# Source: https://www.sqlskills.com/sql-server-resources/sql-server-demos/
# Blog:   https://www.sqlskills.com/blogs/paul/corruption-demo-databases-and-scripts/
#
# Usage: bash download.sh
# Requires: curl, unzip
set -euo pipefail

DEST="$(cd "$(dirname "$0")" && pwd)"

declare -A ZIPS=(
  ["2005corruptdatabasesbackups.zip"]="https://www.sqlskills.com/resources/conferences/2005corruptdatabasesbackups.zip"
  ["2008fatalcorruptionbackups.zip"]="https://www.sqlskills.com/resources/conferences/2008fatalcorruptionbackups.zip"
  ["2008r2fatalcorruptionbackups.zip"]="https://www.sqlskills.com/resources/conferences/2008r2fatalcorruptionbackups.zip"
  ["democorruptmetadata2008r2.zip"]="https://www.sqlskills.com/resources/conferences/democorruptmetadata2008r2.zip"
  ["ie0_corruptdbs.zip"]="https://www.sqlskills.com/resources/conferences/ie0_corruptdbs.zip"
)

cd "${DEST}"

for fname in "${!ZIPS[@]}"; do
  url="${ZIPS[$fname]}"
  if [[ -f "${fname}" ]]; then
    echo "==> ${fname} already present, skipping download"
  else
    echo "==> Downloading ${fname} from ${url}"
    curl -fL -o "${fname}" "${url}"
  fi
  echo "==> Extracting ${fname}"
  unzip -qo "${fname}"
done

echo
echo "Done. BAK files:"
ls -lh ./*.bak 2>/dev/null | awk '{print "  " $5 "  " $9}'
