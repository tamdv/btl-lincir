#!/usr/bin/env bash
# [NHOM8] Open the report in Microsoft Word (macOS), update TOC + lists of figures/tables, save, export PDF.
# Word's sandbox rejects "save as" to this path (it contains "&"), so the PDF is written into Word's container and moved here.
set -euo pipefail
cd "$(dirname "$0")"
D="$PWD/BaoCao_Nhom8_LinCIR.docx"; C="$HOME/Library/Containers/com.microsoft.Word/Data/Documents/BaoCao_Nhom8_LinCIR.pdf"
rm -f BaoCao_Nhom8_LinCIR.pdf "$C"
osascript <<OSA
with timeout of 600 seconds
tell application "Microsoft Word"
    repeat with d in (get documents)
        if name of d is "BaoCao_Nhom8_LinCIR.docx" then close d saving no
    end repeat
    open POSIX file "$D"
    set theDoc to active document
    repeat with f in (get fields of theDoc)
        update field f
    end repeat
    repeat with t in (get tables of contents of theDoc)
        update t
    end repeat
    repeat with t in (get tables of figures of theDoc)
        update t
    end repeat
    save theDoc
    save as theDoc file name "BaoCao_Nhom8_LinCIR.pdf" file format format PDF
    close theDoc saving no
end tell
end timeout
OSA
mv "$C" BaoCao_Nhom8_LinCIR.pdf
pdfinfo BaoCao_Nhom8_LinCIR.pdf | grep Pages
