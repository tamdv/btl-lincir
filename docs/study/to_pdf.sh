#!/usr/bin/env bash
# [NHOM8] Export every docs/study/*.docx to PDF with Microsoft Word (macOS). Word's sandbox cannot write to this path
# (it contains "&"), so each PDF is written into Word's container and moved back here.
set -euo pipefail
cd "$(dirname "$0")"
C="$HOME/Library/Containers/com.microsoft.Word/Data/Documents"
for f in HuongDan_*.docx; do
  pdf="${f%.docx}.pdf"; rm -f "$pdf" "$C/$pdf"
  osascript <<OSA
with timeout of 300 seconds
tell application "Microsoft Word"
    repeat with d in (get documents)
        if name of d is "$f" then close d saving no
    end repeat
    open POSIX file "$PWD/$f"
    set theDoc to active document
    save as theDoc file name "$pdf" file format format PDF
    close theDoc saving no
end tell
end timeout
OSA
  mv "$C/$pdf" "$pdf"
  echo "$pdf: $(pdfinfo "$pdf" | grep Pages | awk '{print $2}') trang"
done
