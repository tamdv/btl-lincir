"""[NHOM8] Rewrite the speaker notes of the (hand-edited) deck in plain language. Slides themselves are untouched.
  python docs/study/update_notes.py [--deck slides/Slides_Nhom8_LinCIR.pptx]"""
import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

from pptx import Presentation

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plain_language import SLIDES  # noqa: E402

SPEAKER = {"1": "Tâm", "2": "Nou", "3": "Nou", "4": "Nou", "5": "Trung", "6": "Trung", "7": "Trung", "8": "Trung", "9": "Tâm",
           "10": "Tùng", "11": "Trung", "12": "Dũng", "13": "Tâm", "14": "Dũng", "15": "Dũng", "16": "Tùng", "17": "Cả nhóm"}

ap = argparse.ArgumentParser()
ap.add_argument("--deck", default=str(Path(__file__).resolve().parents[2] / "slides" / "Slides_Nhom8_LinCIR.pptx"))
a = ap.parse_args()
deck = Path(a.deck)
shutil.copy(deck, deck.with_name(f"{deck.stem}_truocKhiSuaGhiChu_{dt.datetime.now():%Y%m%d-%H%M}.pptx"))
prs = Presentation(deck)
for i, s in enumerate(prs.slides, start=1):
    k = str(i)
    if k in SLIDES:
        say, number = SLIDES[k]
        lines = [f"[{SPEAKER[k]}] {say}"]
        if number != "—":
            lines.append(f"Con số cần nêu: {number}.")
    else:
        lines = [f"[{SPEAKER.get(k, 'Cả nhóm')}] Cảm ơn cô và các bạn; mời đặt câu hỏi."]
    s.notes_slide.notes_text_frame.text = "\n".join(lines)
prs.save(deck)
print("đã cập nhật ghi chú", len(prs.slides), "slide")
