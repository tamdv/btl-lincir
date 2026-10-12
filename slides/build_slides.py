"""[NHOM8] Presentation deck (16:9, Helvetica, white/blue, Morph transitions) -> slides/Slides_Nhom8_LinCIR.pptx

Design rules (from Tâm): 16:9; white + fresh blue palette, modern, restrained; Morph between slides; text >= 20 pt;
Helvetica; titles state the point of the slide; footer = slide number only; reuse the existing diagrams.

Morph: every slide carries the same named shapes ("!!orb", "!!dot", "!!title", "!!num"); PowerPoint matches shapes whose
names start with "!!" across consecutive slides and animates position, size and text between them.

Results come from results/assets.json (scripts/make_report_assets.py); missing numbers show as amber placeholders.
Run:  python slides/build_slides.py   then   ./slides/to_pdf.sh   (PowerPoint export for checking)
"""
import copy
import json
import statistics
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "slides" / "Slides_Nhom8_LinCIR.pptx"
FIG = ROOT / "report" / "figures"
RES = ROOT / "results"

# palette: white dominant, one fresh blue, navy text, light tint for surfaces
BLUE = RGBColor(0x1E, 0x6F, 0xE8)
BLUE_DARK = RGBColor(0x14, 0x4F, 0xB0)
NAVY = RGBColor(0x0F, 0x1C, 0x3F)
TINT = RGBColor(0xEA, 0xF2, 0xFF)
TINT2 = RGBColor(0xD6, 0xE6, 0xFF)
MUTED = RGBColor(0x5B, 0x6B, 0x82)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
AMBER = RGBColor(0xB4, 0x6B, 0x00)
FONT = "Helvetica"
MIN_PT = 20

W, H = Inches(13.333), Inches(7.5)

# orb (big light circle) and dot (small blue circle) positions per slide: x, y, diameter (inches) -> Morph motion
ORB = [(7.6, -1.2, 7.4), (10.6, -2.4, 4.6), (-1.6, 4.4, 4.2), (10.9, 4.6, 4.0), (10.6, -2.4, 4.6), (-2.0, -2.0, 4.0),
       (10.9, 4.8, 3.8), (11.2, -2.2, 4.2), (-1.8, 4.6, 4.0), (10.8, 4.9, 3.8), (11.0, -2.3, 4.4), (-2.0, 4.5, 4.2),
       (10.9, 4.8, 3.9), (11.2, -2.4, 4.4), (-1.9, -2.2, 4.0), (10.8, 4.7, 4.0), (6.9, -0.6, 8.2)]
DOT = [(7.2, 5.6, 0.9), (12.25, 0.55, 0.45), (0.06, 6.6, 0.45), (12.8, 3.6, 0.45), (12.25, 0.55, 0.45), (0.06, 3.4, 0.45),
       (12.8, 4.2, 0.45), (12.3, 0.55, 0.45), (0.06, 6.6, 0.45), (12.8, 3.4, 0.45), (12.3, 0.55, 0.45), (0.06, 6.6, 0.45),
       (12.8, 4.0, 0.45), (12.3, 0.55, 0.45), (0.06, 3.6, 0.45), (12.8, 3.8, 0.45), (6.4, 5.4, 1.0)]

NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
MORPH_XML = (
    '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
    '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" '
    'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" Requires="p159">'
    '<p:transition spd="slow" p14:dur="1200"><p159:morph option="byObject"/></p:transition></mc:Choice>'
    '<mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')


def _sha(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------- primitives


def _font(run, size, bold=False, color=NAVY, italic=False):
    run.font.name = FONT
    run.font.size = Pt(max(size, MIN_PT))
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def text(slide, x, y, w, h, parts, size=22, color=NAVY, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         name=None, line=1.1):
    """parts: str | list of paragraphs; a paragraph is str or list of (text, {bold, color, italic, size})."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    paras = parts if isinstance(parts, list) else [parts]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line
        runs = para if isinstance(para, list) else [(para, {})]
        for t, o in runs:
            r = p.add_run()
            r.text = t
            _font(r, o.get("size", size), o.get("bold", bold), o.get("color", color), o.get("italic", False))
    return tb


def bullets(slide, x, y, w, h, items, size=22, gap=10):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = 1.08
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Inches(0.32)))
        pPr.set("indent", str(-Inches(0.32)))
        bu = etree.SubElement(pPr, "{http://schemas.openxmlformats.org/drawingml/2006/main}buClr")
        etree.SubElement(bu, "{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr").set("val", "1E6FE8")
        etree.SubElement(pPr, "{http://schemas.openxmlformats.org/drawingml/2006/main}buChar").set("char", "•")
        runs = it if isinstance(it, list) else [(it, {})]
        for t, o in runs:
            r = p.add_run()
            r.text = t
            _font(r, o.get("size", size), o.get("bold", False), o.get("color", NAVY))
    return tb


def shape(slide, kind, x, y, w, h, fill, name=None, line=None):
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line:
        s.line.color.rgb = line
        s.line.width = Pt(1.25)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if name:
        s.name = name
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.08
    return s


def card(slide, x, y, w, h, heading, body, fill=TINT, head_color=BLUE_DARK, size=21):
    shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill)
    text(slide, x + 0.25, y + 0.18, w - 0.5, 0.55, heading, size=22, bold=True, color=head_color)
    if isinstance(body, list) and body and not isinstance(body[0], tuple):
        bullets(slide, x + 0.25, y + 0.8, w - 0.5, h - 0.95, body, size=size, gap=6)
    else:
        text(slide, x + 0.25, y + 0.8, w - 0.5, h - 0.95, body, size=size)


def stat(slide, x, y, w, value, label, color=BLUE):
    text(slide, x, y, w, 0.95, value, size=48, bold=True, color=color)
    text(slide, x, y + 0.95, w, 0.85, label, size=20, color=MUTED)


def image(slide, path, x, y, w=None, h=None):
    if not Path(path).exists():
        ph = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w or 6, h or 3, TINT)
        text(slide, x + 0.3, y + 0.3, (w or 6) - 0.6, 1.2, f"[Chờ kết quả: {Path(path).name}]", size=20, color=AMBER)
        return ph
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)


def placeholder(slide, x, y, w, h, msg):
    shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, TINT)
    text(slide, x + 0.3, y + 0.25, w - 0.6, h - 0.5, msg, size=22, color=AMBER)


def table(slide, x, y, w, rows, col_w, size=20, header_fill=BLUE, highlight_row=None):
    nr, nc = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(0.5 * nr)).table
    for j, cw in enumerate(col_w):
        gt.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = gt.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.08)
            c.margin_top = c.margin_bottom = Inches(0.04)
            c.fill.solid()
            c.fill.fore_color.rgb = header_fill if i == 0 else (TINT if i == highlight_row else WHITE)
            tf = c.text_frame
            tf.paragraphs[0].text = ""
            r = tf.paragraphs[0].add_run()
            r.text = str(v)
            amber = str(v).startswith("[")
            _font(r, size, bold=(i == 0 or i == highlight_row), color=WHITE if i == 0 else (AMBER if amber else NAVY))
            tf.paragraphs[0].alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
    return gt


# ---------------------------------------------------------------- slide frame


class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = W, H
        self.blank = self.prs.slide_layouts[6]
        self.n = 0

    def new(self, title, notes="", title_size=32, cover=False):
        s = self.prs.slides.add_slide(self.blank)
        bg = s.background.fill
        bg.solid()
        bg.fore_color.rgb = WHITE
        i = self.n
        ox, oy, od = ORB[i % len(ORB)]
        shape(s, MSO_SHAPE.OVAL, ox, oy, od, od, TINT, name="!!orb")
        dx, dy, dd = DOT[i % len(DOT)]
        shape(s, MSO_SHAPE.OVAL, dx, dy, dd, dd, BLUE, name="!!dot")
        if not cover:
            text(s, 0.6, 0.38, 11.4, 1.25, title, size=title_size, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, name="!!title")
            text(s, 11.9, 6.82, 1.0, 0.5, str(i + 1), size=20, color=MUTED, align=PP_ALIGN.RIGHT, name="!!num")
        if notes:
            s.notes_slide.notes_text_frame.text = notes
        self.n += 1
        return s

    def save(self):
        global OUT
        stamp = OUT.with_suffix(".generated.sha256")
        if OUT.exists() and (not stamp.exists() or stamp.read_text().strip() != _sha(OUT)):
            # edited by hand in PowerPoint after the last build: never overwrite it
            OUT = OUT.with_name(OUT.stem + "_auto.pptx")
            print(f"[!] Slides đã được sửa tay -> không ghi đè; bản tự sinh ghi vào {OUT.name}")
        for s in self.prs.slides:  # Morph transition on every slide
            el = s._element
            frag = etree.fromstring(MORPH_XML)
            timing = el.find(f"{{{NS_P}}}timing")
            if timing is not None:
                timing.addprevious(frag)
            else:
                ext = el.find(f"{{{NS_P}}}extLst")
                ext.addprevious(frag) if ext is not None else el.append(frag)
        self.prs.save(OUT)
        if OUT.name == "Slides_Nhom8_LinCIR.pptx":
            OUT.with_suffix(".generated.sha256").write_text(_sha(OUT))


# ---------------------------------------------------------------- results


def assets():
    p = RES / "assets.json"
    return json.loads(p.read_text()) if p.exists() else {}


def ms(v):
    v = [x for x in (v or []) if x is not None]
    if not v:
        return "[chờ]"
    s = f"{statistics.mean(v):.2f}" if len(v) == 1 else f"{statistics.mean(v):.2f} ± {statistics.stdev(v):.2f}"
    return s.replace(".", ",")


# ---------------------------------------------------------------- content


def build():
    d = Deck()
    A = assets()
    main = A.get("main", {})

    # 1 cover
    s = d.new("", notes="Tâm: giới thiệu đề tài, môn học, giảng viên và nhóm; mục tiêu: tái hiện và cải tiến LinCIR, chứng minh bằng kiểm định thống kê.", cover=True)
    text(s, 0.8, 1.0, 7.4, 0.5, "TÌM KIẾM VÀ TRUY XUẤT THÔNG TIN · NHÓM 8", size=20, bold=True, color=BLUE, name="!!title")
    text(s, 0.8, 1.7, 7.6, 2.8, [[("Truy xuất ảnh kết hợp chỉ huấn luyện bằng văn bản", {"size": 40, "bold": True})],
                                 [("Tái hiện và cải tiến LinCIR (CVPR 2024)", {"size": 28, "color": BLUE_DARK})]], line=1.05)
    text(s, 0.8, 4.65, 7.6, 1.9, ["Giảng viên: TS. Đào Thị Thuý Quỳnh · Lớp M25CQHT02-B",
                                  "Đào Văn Tâm · Lâm Thành Trung · Nguyễn Xuân Tùng",
                                  "Trần Quang Đức Dũng · Mekdala Nounou"], size=20, color=MUTED)
    image(s, FIG / "cir_example_slide.png", 8.3, 1.9, w=4.6)

    # 2 problem
    s = d.new("Truy vấn gồm một ảnh tham chiếu và một câu mô tả thay đổi",
              notes="Nou: ví dụ chiếc váy — ảnh tham chiếu + “màu bạc, tay ngắn hơn” → ảnh đích. Nhu cầu thông tin không diễn đạt trọn bằng chỉ chữ hay chỉ ảnh.")
    image(s, FIG / "cir_example_slide.png", 0.6, 1.85, w=8.2)
    card(s, 9.2, 1.9, 3.5, 4.6, "CIR", ["Giữ đặc điểm của ảnh", "Áp dụng phần thay đổi", "Trả về danh sách ảnh có xếp hạng"])

    # 3 why zero-shot
    s = d.new("Dữ liệu bộ ba đắt và nhỏ nên cần CIR không cần mẫu",
              notes="Nou: bộ ba ⟨ảnh, câu, ảnh đích⟩ phải gán nhãn tay; mô hình có giám sát khó tổng quát; zero-shot không dùng bộ ba nào khi huấn luyện.")
    stat(s, 0.8, 2.0, 3.6, "46,6k", "bộ ba FashionIQ")
    stat(s, 4.5, 2.0, 3.6, "28,8k", "bộ ba CIRR")
    stat(s, 8.2, 2.0, 4.2, "0", "bộ ba dùng trong zero-shot CIR", color=BLUE_DARK)
    card(s, 0.8, 4.35, 11.7, 2.1, "Hệ quả", [[("Có giám sát: ", {"bold": True}), ("gán nhãn thủ công, khó mở rộng sang lĩnh vực mới", {})],
                                           [("Zero-shot: ", {"bold": True}), ("huấn luyện trên dữ liệu sẵn có, đánh giá trực tiếp trên bộ CIR", {})]])

    # 4 IR link
    s = d.new("CIR là truy xuất có xếp hạng, đo bằng R@K và mAP@K",
              notes="Nou: liên hệ chương I — mô hình tìm kiếm cổ điển, Precision/Recall; danh sách xếp hạng → R@K (một ảnh đúng), mAP@K (nhiều ảnh đúng); tìm kiếm vector theo cosine khác mô hình Boolean khớp chính xác trên chỉ mục ngược.")
    card(s, 0.6, 1.9, 3.9, 3.6, "Chương I", ["Nhu cầu → truy vấn → xếp hạng", "Precision, Recall", "Boolean + chỉ mục ngược: khớp chính xác"])
    card(s, 4.75, 1.9, 3.9, 3.6, "Độ đo của CIR", ["R@K: ảnh đích nằm trong top-K", "mAP@K: nhiều ảnh đúng, thưởng vị trí cao"])
    card(s, 8.9, 1.9, 3.9, 3.6, "Tìm kiếm vector", ["Ảnh, truy vấn → vector CLIP", "Xếp hạng theo cosine"], fill=TINT2)
    text(s, 0.6, 5.8, 12.1, 0.6, [[("Nhóm báo cáo R@10, R@50 trên FashionIQ và mAP@K trên CIRCO", {"color": BLUE_DARK, "bold": True})]], size=22)

    # 5 pseudo token
    s = d.new("Ảnh được biến thành một “từ giả” [$] trong câu truy vấn",
              notes="Trung: ảnh → vector → φ → token [$]; ghép “a photo of [$] that …” → bộ mã hóa văn bản → vector truy vấn → tìm ảnh theo cosine. Chỉ cần học φ.")
    image(s, FIG / "lincir_infer_slide.png", 0.6, 2.0, w=12.1)

    # 6 limits of prior work
    s = d.new("Pic2Word và SEARLE học với câu mẫu cố định và cần ảnh",
              notes="Trung: hai hạn chế — chỉ thấy “a photo of [$]” nên kém với câu điều chỉnh phức tạp, giảm hiệu năng khi backbone lớn; phải chạy bộ mã hóa ảnh khi huấn luyện, tốn tính toán và lưu trữ.")
    card(s, 0.6, 1.9, 5.9, 3.0, "Câu mẫu cố định", ["Chỉ học trên “a photo of [$]”", "Kém với câu điều chỉnh phức tạp", "Giảm khi tăng kích thước backbone"])
    card(s, 6.8, 1.9, 5.9, 3.0, "Cần ảnh khi huấn luyện", ["Chạy bộ mã hóa ảnh mỗi bước", "Ảnh CC3M ≈ 430 GB, chú thích 125 MB"])
    text(s, 0.6, 5.3, 12.1, 1.0, [[("LinCIR bỏ cả hai hạn chế: ", {"bold": True, "color": BLUE_DARK}), ("chỉ huấn luyện bằng văn bản tự nhiên đa dạng", {})]], size=24)

    # 7 SMP
    s = d.new("LinCIR học từ giả chỉ bằng văn bản nhờ Self-Masking Projection",
              notes="Trung: z_c = C(câu); ê = φ(z_c + n); che cụm tính từ/danh từ bằng [$] → “[$] sleeps on [$]”; ép ẑ_c ≈ z_c bằng MSE. [$] phải tóm tắt nội dung thiết yếu của câu. Khối xanh lá là phần nhóm bổ sung.")
    image(s, FIG / "lincir_train_slide.png", 1.2, 1.75, w=10.9)

    # 8 noise / gap
    s = d.new("Nhiễu giúp φ dùng được vector ảnh dù hai miền lệch nhau",
              notes="Trung: khi suy luận φ nhận vector ảnh; vector ảnh và văn bản của CLIP nằm ở hai vùng (modality gap). Đo trên 5.000 cặp COCO: tâm cách 0,82, cosine cặp 0,26. LinCIR thêm nhiễu u·ε khi huấn luyện để φ chịu được.")
    stat(s, 0.8, 2.0, 3.8, "0,82", "khoảng cách tâm ảnh – văn bản")
    stat(s, 4.7, 2.0, 3.8, "0,26", "cosine trung bình cặp ảnh – chú thích")
    card(s, 8.6, 1.9, 4.1, 2.3, "Nhiễu của LinCIR", [[("n = u · ε", {"bold": True, "size": 24})], [("u ~ U(0,1), ε ~ N(0, I)", {})]])
    card(s, 0.8, 4.5, 11.9, 1.9, "Ý nghĩa", ["φ học trên vector văn bản có nhiễu nên vẫn hoạt động khi nhận vector ảnh"])

    # 9 code
    s = d.new("Mã nguồn chạy trên môi trường mới với sai lệch bằng 0",
              notes="Tâm: mã gốc cho transformers 4.34; viết lại encoder từ mô-đun con, thay tokenizer, sửa 4 lỗi. Bằng chứng: sai lệch 0 với CLIP gốc trên ViT-B/32 và ViT-L/14; checkpoint chính thức nạp khớp. Ba khác biệt bài báo – mã nguồn.")
    stat(s, 0.8, 1.95, 3.6, "0,00", "sai lệch so với CLIP gốc")
    stat(s, 0.8, 4.05, 3.6, "4", "lỗi mã gốc đã sửa")
    card(s, 4.7, 1.9, 3.9, 3.9, "Đã làm", ["Viết lại encoder văn bản", "Thay tokenizer, “$” = 259", "Kiểm chứng ViT-B/32, ViT-L/14"])
    card(s, 8.85, 1.9, 3.9, 3.9, "Bài báo ≠ mã nguồn", ["φ không có LayerNorm", "Thêm prompt Midjourney", "Từ khóa giữ cả từ hạn định"], fill=TINT2)

    # 10 reproduction
    off = main.get("EXP-000-official", {})
    g = lambda k: (f"{off[k][0]:.2f}".replace(".", ",") if off.get(k) else "[chờ]")
    s = d.new("Checkpoint chính thức tái hiện khớp bài báo, lệch tối đa 0,77 điểm",
              notes="Tùng: đánh giá checkpoint chính thức bằng mã đã chuyển đổi; FashionIQ val; lệch tối đa 0,77, TB R@10 +0,07. Chạy lại hai lần cho thứ hạng từng truy vấn giống hệt. CIRCO val mAP@5 = 10,50 làm mốc (bài báo chỉ có test).")
    rows = [["FashionIQ val", "Dress R@10", "Dress R@50", "Shirt R@10", "Shirt R@50", "Toptee R@10", "Toptee R@50", "TB R@10", "TB R@50"],
            ["Bài báo", "20,92", "42,44", "29,10", "46,81", "28,81", "50,18", "26,28", "46,49"],
            ["Nhóm chạy lại"] + [g(k) for k in ("dress_fiq_recall_at10", "dress_fiq_recall_at50", "shirt_fiq_recall_at10", "shirt_fiq_recall_at50",
                                                 "toptee_fiq_recall_at10", "toptee_fiq_recall_at50", "average_fiq_recall_at10", "average_fiq_recall_at50")]]
    table(s, 0.6, 1.95, 12.1, rows, [2.1] + [1.25] * 8, size=20, highlight_row=2)
    stat(s, 0.8, 4.2, 3.7, "0,77", "điểm lệch lớn nhất")
    stat(s, 4.7, 4.2, 3.9, g("circo_map_at5"), "CIRCO val mAP@5 (mốc)")
    stat(s, 8.8, 4.2, 3.9, "100%", "thứ hạng giống hệt khi chạy lại")

    # 11 improvement A
    s = d.new("Cải tiến A: thêm InfoNCE để từ giả phân biệt được các câu",
              notes="Trung: MSE chỉ kéo ẑ về z của chính câu đó, không đẩy câu khác ra xa; đánh giá là xếp hạng. Thêm λ·InfoNCE, τ = 0,07, 511 mẫu âm trong batch 512; giữ MSE để bảo toàn chuẩn vector. Chi phí +5%/bước.")
    card(s, 0.6, 1.9, 6.1, 2.2, "Vấn đề", ["MSE không phạt việc gần câu khác", "Đánh giá lại là xếp hạng"])
    card(s, 0.6, 4.3, 6.1, 2.2, "Giải pháp", [[("L = L_SMP + 0,5 · InfoNCE", {"bold": True})], [("τ = 0,07 · 511 mẫu âm trong batch", {})]], fill=TINT2)
    stat(s, 7.3, 2.0, 5.2, "+5%", "thời gian mỗi bước huấn luyện")
    a_main = main.get("EXP-002-infonce", {})
    b_main = main.get("EXP-001-baseline", {})
    stat(s, 7.3, 4.3, 5.2, (ms(a_main.get("average_fiq_recall_at10")) if a_main else "[chờ]"),
         "FashionIQ TB R@10 của A (baseline " + (ms(b_main.get("average_fiq_recall_at10")) if b_main else "[chờ]") + ")")

    # 12 improvement B
    s = d.new("Cải tiến B: dịch nhiễu theo hướng của modality gap",
              notes="Dũng: nhiễu LinCIR đẳng hướng, không đưa đầu vào φ về phía vùng ảnh. B: n = α·Δ + u·ε, Δ = tâm ảnh − tâm văn bản trên 5.000 cặp COCO val2017 (độc lập với tập đánh giá), α = 0,5.")
    card(s, 0.6, 1.9, 6.1, 2.2, "Nhiễu của LinCIR", ["Đẳng hướng: làm mờ vùng văn bản", "Không hướng về vùng ảnh"])
    card(s, 0.6, 4.3, 6.1, 2.2, "Nhiễu có hướng", [[("n = 0,5 · Δ + u · ε", {"bold": True})], [("Δ = tâm ảnh − tâm văn bản", {})]], fill=TINT2)
    stat(s, 7.3, 2.0, 5.2, "13,87", "độ lớn của Δ (5.000 cặp COCO)")
    stat(s, 7.3, 4.3, 5.2, "COCO val", "độc lập với FashionIQ, CIRCO")

    # 13 setup
    s = d.new("Mọi biến thể dùng cùng cấu hình, 3 seed và kiểm định theo truy vấn",
              notes="Tâm: Kaggle 2 × T4, mỗi run 1 GPU batch 512; 5.000 bước, checkpoint cuối, 3 seed; FashionIQ + CIRCO; bootstrap + Wilcoxon. Vận hành: lập lịch theo giới hạn 12 giờ/30 giờ; nghẽn CPU do spaCy → xử lý theo lô ×3,1, kết quả giống hệt.")
    card(s, 0.6, 1.9, 3.9, 3.4, "Cấu hình", ["ViT-L/14, batch 512", "5.000 bước", "3 seed / biến thể"])
    card(s, 4.75, 1.9, 3.9, 3.4, "Đánh giá", ["FashionIQ val", "CIRCO val", "Bootstrap + Wilcoxon"])
    card(s, 8.9, 1.9, 3.9, 3.4, "Vận hành Kaggle", ["2 × T4, 2 run song song", "Không vượt 12 giờ/phiên", "Nạp dữ liệu nhanh ×3,1"], fill=TINT2)
    text(s, 0.6, 5.65, 12.1, 0.9, [[("Chỉ khác đúng thành phần cải tiến ", {"bold": True, "color": BLUE_DARK}), ("→ chênh lệch là do cải tiến, không do cấu hình", {})]], size=22)

    # 14 main results
    s = d.new("Kết quả chính và kiểm định so với baseline",
              notes="Dũng: đọc bảng mean ± std qua 3 seed; kết luận theo p < 0,05 cho từng biến thể; nhấn mạnh KTC 95%. [Cập nhật tiêu đề thành kết luận chính khi có số liệu.]", title_size=32)
    rows = [["Biến thể", "FIQ TB R@10", "FIQ TB R@50", "CIRCO mAP@5"]]
    for prefix, label in (("EXP-001-baseline", "Baseline"), ("EXP-002-infonce", "A: + InfoNCE"),
                          ("EXP-003-gapnoise", "B: + nhiễu có hướng"), ("EXP-004-infonce-gapnoise", "A + B")):
        r = main.get(prefix, {})
        rows.append([label] + [ms(r.get(k)) if r else "[chờ]" for k in ("average_fiq_recall_at10", "average_fiq_recall_at50", "circo_map_at5")])
    table(s, 0.6, 1.95, 12.1, rows, [3.7, 2.8, 2.8, 2.8], size=20)
    sig = A.get("significance", {})
    if sig:
        lines = []
        for prefix, label in (("EXP-002-infonce", "A"), ("EXP-003-gapnoise", "B"), ("EXP-004-infonce-gapnoise", "A+B")):
            for r in sig.get(prefix, []):
                if r["metric"] in ("R@10", "ap5"):
                    lines.append(f"{label} · {r['dataset']} {r['metric'].replace('ap', 'mAP@')}: Δ {r['delta']:+.2f}, p = {r['p_boot']:.3f}".replace(".", ","))
        bullets(s, 0.8, 4.75, 11.8, 2.0, lines[:4], size=20, gap=2)
    else:
        placeholder(s, 0.6, 4.75, 12.1, 1.7, "[Chờ kết quả phiên eval: Δ, khoảng tin cậy 95% và p-value cho A, B, A+B]")

    # 15 why
    s = d.new("Vì sao: φ nhất quán hơn giữa ảnh và văn bản",
              notes="Dũng: (1) độ nhất quán φ ảnh–văn bản theo biến thể; (2) đường học; (3) ví dụ top-5. [Sửa tiêu đề theo kết quả thật.]")
    image(s, RES / "figures" / "modality_gap.png", 0.6, 1.95, w=6.0)
    image(s, RES / "figures" / "learning_curve.png", 6.8, 1.95, w=6.0)

    # 16 conclusion
    s = d.new("Kết luận, hạn chế và hướng phát triển",
              notes="Tùng: kết luận H1–H3 theo kiểm định; hạn chế: 5.000 bước, không quét λ/α, không có CIRR, CIRCO chỉ val; hướng phát triển.")
    placeholder(s, 0.6, 1.9, 6.0, 3.6, "[Kết luận H1–H3: điền sau phiên eval]")
    card(s, 6.9, 1.9, 5.8, 3.6, "Hạn chế → hướng phát triển", ["5.000 bước → đủ 20.000", "Chưa quét λ, α", "Thêm CIRR, CIRCO test", "Hướng C: từ khóa theo IDF"], fill=TINT2)

    # 17 thanks
    s = d.new("", notes="Cả nhóm: cảm ơn, mời hỏi đáp.", cover=True)
    text(s, 0.8, 2.2, 10.5, 1.0, "Cảm ơn thầy cô và các bạn", size=44, bold=True, name="!!title")
    text(s, 0.8, 3.4, 10.5, 0.8, "Hỏi đáp", size=28, color=BLUE)
    text(s, 11.9, 6.82, 1.0, 0.5, str(d.n), size=20, color=MUTED, align=PP_ALIGN.RIGHT, name="!!num")

    d.save()
    return d.n


if __name__ == "__main__":
    print(OUT, build(), "slides")
