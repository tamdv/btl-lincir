"""[NHOM8] Insert two slides after the cover of the hand-edited deck: paper summary (slide 2) and roadmap (slide 3).
Existing slides are kept as they are; only footer numbers are shifted. A timestamped backup is written first.

  python slides/add_overview_slides.py [--deck slides/Slides_Nhom8_LinCIR.pptx]
"""
import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_slides import (BLUE, BLUE_DARK, MORPH_XML, MUTED, NAVY, NS_P, TINT, WHITE, bullets, card,  # noqa: E402
                          shape, text)


def frame(prs, title, orb, dot):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = WHITE
    shape(s, MSO_SHAPE.OVAL, *orb, orb[2], TINT, name="!!orb")
    shape(s, MSO_SHAPE.OVAL, *dot, dot[2], BLUE, name="!!dot")
    text(s, 0.6, 0.38, 11.4, 1.25, title, size=32, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, name="!!title")
    text(s, 11.9, 6.82, 1.0, 0.5, "0", size=20, color=MUTED, align=PP_ALIGN.RIGHT, name="!!num")
    el = s._element
    ext = el.find(f"{{{NS_P}}}extLst")
    frag = etree.fromstring(MORPH_XML)
    ext.addprevious(frag) if ext is not None else el.append(frag)
    return s


def paper_slide(prs):
    s = frame(prs, "Bài báo LinCIR: huấn luyện truy xuất ảnh kết hợp chỉ bằng văn bản", (-1.8, 4.6, 4.0), (0.06, 3.4, 0.45))
    y, h, w = 1.9, 3.5, 3.85
    card(s, 0.6, y, w, h, "Vấn đề", ["Bộ ba CIR gán nhãn tay: đắt, nhỏ",
                                     "Pic2Word, SEARLE cần ảnh khi huấn luyện và câu mẫu cố định"], size=20)
    card(s, 0.6 + w + 0.3, y, w, h, "Ý tưởng LinCIR", ["Self-Masking Projection: học φ chỉ từ văn bản",
                                                       "Thêm nhiễu u·ε để φ dùng được cho vector ảnh"], size=20)
    card(s, 0.6 + 2 * (w + 0.3), y, w, h, "Kết quả bài báo", ["Tốt nhất trên 4 benchmark",
                                                              "Nhanh hơn Pic2Word 6 lần, SEARLE 8,4 lần",
                                                              "Vượt cả phương pháp có giám sát (FashionIQ)"], size=20)
    text(s, 0.6, 5.65, 12.1, 1.0, [[("Gu, Chun, Kim, Kang, Yun (NAVER) · CVPR 2024 · mã nguồn công khai ", {"color": MUTED}),
                                    ("→ nhóm dựng lại mã, tái hiện, rồi cải tiến", {"bold": True, "color": BLUE_DARK})]], size=20)
    return s


STEPS = [("Bài báo LinCIR", "SMP + nhiễu, chỉ dùng văn bản"), ("Cải tiến A, B", "A: thêm InfoNCE · B: nhiễu có hướng"),
         ("Dựng mã nguồn", "sai lệch 0 với CLIP gốc"), ("Tái hiện", "checkpoint chính thức khớp bài báo"),
         ("Thực nghiệm Kaggle", "baseline, A, B, A+B × 3 seed"), ("Kết quả, kiểm định", "so với baseline, 3 seed"),
         ("Phân tích nguyên nhân", "độ nhất quán φ ảnh – văn bản"), ("Đánh giá, kết luận", "H1–H3, hạn chế, hướng phát triển")]


def roadmap_slide(prs):
    s = frame(prs, "Lộ trình: từ bài báo đến bằng chứng cải tiến tốt hơn", (10.9, 4.8, 3.8), (12.8, 4.0, 0.45))
    w, h, gap, x0 = 2.8, 1.85, 0.3, 0.6
    for k, (head, desc) in enumerate(STEPS):
        r, c = divmod(k, 4)
        x, y = x0 + c * (w + gap), 1.75 + r * (h + 0.3)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, TINT)
        text(s, x + 0.15, y + 0.12, w - 0.3, h - 0.2,
             [[(f"{k + 1}  ", {"bold": True, "color": BLUE}), (head, {"bold": True, "color": BLUE_DARK})],
              [(desc, {"color": NAVY})]], size=20)
        if c < 3:
            shape(s, MSO_SHAPE.CHEVRON, x + w + 0.07, y + h / 2 - 0.15, 0.16, 0.3, BLUE)
    text(s, 0.6, 6.05, 11.2, 0.6, [[("Kết luận chính: ", {"bold": True, "color": BLUE_DARK}),
                                    ("B tốt hơn có ý nghĩa thống kê, A làm giảm hiệu năng", {})]], size=20)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", default=str(Path(__file__).resolve().parent / "Slides_Nhom8_LinCIR.pptx"))
    deck = Path(ap.parse_args().deck)
    prs = Presentation(deck)
    titles = [next((sh.text_frame.text for sh in s.shapes if sh.name == "!!title"), "") for s in prs.slides]
    if any(t.startswith("Bài báo LinCIR:") for t in titles):
        sys.exit("Deck đã có slide tóm tắt bài báo, không chèn lại.")
    shutil.copy(deck, deck.with_name(f"{deck.stem}_truocKhiThemTomTat_{dt.datetime.now():%Y%m%d-%H%M}.pptx"))
    paper_slide(prs)
    roadmap_slide(prs)
    lst = prs.slides._sldIdLst
    ids = list(lst)
    new = ids[-2:]
    for e in new:
        lst.remove(e)
    ids[0].addnext(new[0])
    new[0].addnext(new[1])
    for i, s in enumerate(prs.slides, start=1):
        for sh in s.shapes:
            if sh.name == "!!num":
                runs = sh.text_frame.paragraphs[0].runs
                runs[0].text = str(i)
                for r in runs[1:]:
                    r.text = ""
    # setup slide: name the four variants explicitly
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.startswith("ViT-L/14, batch 512"):
                ps = sh.text_frame.paragraphs
                for p, t in zip(ps, ["Baseline, A, B, A+B", "ViT-L/14, batch 512", "5.000 bước × 3 seed"]):
                    p.runs[0].text = t
    prs.save(deck)
    print("đã chèn slide 2 (tóm tắt bài báo), 3 (lộ trình);", len(prs.slides), "slide")


if __name__ == "__main__":
    main()
