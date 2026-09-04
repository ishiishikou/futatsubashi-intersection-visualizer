#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import cairosvg
import svgwrite

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1600, 1050
FONT = "'Noto Sans CJK JP','Noto Sans JP',sans-serif"
C = {
    "bg": "#f8fafc",
    "card": "#ffffff",
    "border": "#cbd5e1",
    "text": "#0f172a",
    "muted": "#475569",
    "surface": "#475569",
    "surface_fill": "#e2e8f0",
    "connector": "#ea580c",
    "under": "#15803d",
    "rail": "#7c2d12",
    "crosswalk": "#dc2626",
    "ped": "#0369a1",
    "island": "#f1f5f9",
    "note": "#fff7ed",
    "note_border": "#fed7aa",
}


def text(dwg, x, y, value, *, size=22, weight=500, fill=None, anchor="start"):
    t = dwg.text(
        "",
        insert=(x, y),
        font_family=FONT,
        font_size=size,
        font_weight=weight,
        fill=fill or C["text"],
        text_anchor=anchor,
    )
    for i, line in enumerate(value.split("\n")):
        t.add(dwg.tspan(line, x=[x], dy=[0 if i == 0 else size * 1.28]))
    dwg.add(t)


def line(dwg, p1, p2, *, stroke, width=8, dash=None, opacity=1.0):
    attrs = dict(
        stroke=stroke,
        stroke_width=width,
        stroke_linecap="round",
        stroke_linejoin="round",
        stroke_opacity=opacity,
        fill="none",
    )
    if dash:
        attrs["stroke_dasharray"] = dash
    dwg.add(dwg.line(start=p1, end=p2, **attrs))


def path(dwg, d, *, stroke, width=8, dash=None, opacity=1.0, fill="none"):
    attrs = dict(
        d=d,
        stroke=stroke,
        stroke_width=width,
        stroke_linecap="round",
        stroke_linejoin="round",
        stroke_opacity=opacity,
        fill=fill,
    )
    if dash:
        attrs["stroke_dasharray"] = dash
    dwg.add(dwg.path(**attrs))


def crosswalk(dwg, cx, cy, angle=0, length=90, width=36):
    # A simplified zebra crossing: official 2026 completion image shows multiple crossings
    # around the traffic island. Positioning here is schematic, not survey-grade geometry.
    g = dwg.g(transform=f"translate({cx},{cy}) rotate({angle})")
    g.add(dwg.rect(insert=(-length / 2, -width / 2), size=(length, width), rx=3, ry=3, fill="#fee2e2", stroke=C["crosswalk"], stroke_width=2))
    for x in range(int(-length / 2 + 8), int(length / 2 - 6), 14):
        g.add(dwg.line(start=(x, -width / 2 + 4), end=(x, width / 2 - 4), stroke=C["crosswalk"], stroke_width=4, stroke_linecap="round"))
    dwg.add(g)


def ped_signal(dwg, x, y):
    dwg.add(dwg.rect(insert=(x - 10, y - 17), size=(20, 34), rx=4, ry=4, fill="#0f172a", stroke="#ffffff", stroke_width=1.5))
    dwg.add(dwg.circle(center=(x, y - 7), r=4.2, fill="#ef4444"))
    dwg.add(dwg.circle(center=(x, y + 7), r=4.2, fill="#22c55e"))


def panel(dwg, x, y, w, h, title, subtitle=None):
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=18, ry=18, fill=C["card"], stroke=C["border"], stroke_width=2))
    text(dwg, x + 24, y + 44, title, size=27, weight=700)
    if subtitle:
        text(dwg, x + 24, y + 76, subtitle, size=18, weight=500, fill=C["muted"])


def draw_surface_plan(dwg):
    x, y, w, h = 55, 145, 980, 700
    panel(dwg, x, y, w, h, "地上：1号交差点の完成形を単純化", "横浜市の2026年8月『完成イメージ』を、構造だけ分かるよう模式化")

    ox, oy = x + 55, y + 105

    # Existing surface road from Mitsukyo-station side (lower-right to center).
    path(dwg, f"M {ox+815},{oy+505} C {ox+690},{oy+465} {ox+570},{oy+420} {ox+445},{oy+360}", stroke=C["surface_fill"], width=86)
    path(dwg, f"M {ox+815},{oy+505} C {ox+690},{oy+465} {ox+570},{oy+420} {ox+445},{oy+360}", stroke=C["surface"], width=5)

    # New connection bends around the traffic island toward the new road.
    path(dwg, f"M {ox+445},{oy+360} C {ox+365},{oy+315} {ox+300},{oy+250} {ox+270},{oy+180} C {ox+245},{oy+125} {ox+210},{oy+88} {ox+155},{oy+72}", stroke="#ffedd5", width=92)
    path(dwg, f"M {ox+445},{oy+360} C {ox+365},{oy+315} {ox+300},{oy+250} {ox+270},{oy+180} C {ox+245},{oy+125} {ox+210},{oy+88} {ox+155},{oy+72}", stroke=C["connector"], width=18)

    # Additional surface approaches seen in the official completion image.
    path(dwg, f"M {ox+270},{oy+180} C {ox+390},{oy+168} {ox+505},{oy+155} {ox+645},{oy+90}", stroke=C["surface_fill"], width=62)
    path(dwg, f"M {ox+270},{oy+180} C {ox+390},{oy+168} {ox+505},{oy+155} {ox+645},{oy+90}", stroke=C["surface"], width=4)
    path(dwg, f"M {ox+515},{oy+405} C {ox+620},{oy+330} {ox+705},{oy+245} {ox+810},{oy+145}", stroke=C["surface_fill"], width=62)
    path(dwg, f"M {ox+515},{oy+405} C {ox+620},{oy+330} {ox+705},{oy+245} {ox+810},{oy+145}", stroke=C["surface"], width=4)

    # Traffic island, matching the broad U/oval shape in the official 2026 completion image.
    island_path = (
        f"M {ox+405},{oy+230} "
        f"C {ox+455},{oy+175} {ox+555},{oy+160} {ox+625},{oy+205} "
        f"C {ox+675},{oy+238} {ox+682},{oy+305} {ox+648},{oy+347} "
        f"C {ox+605},{oy+400} {ox+505},{oy+402} {ox+450},{oy+350} "
        f"C {ox+415},{oy+316} {ox+393},{oy+270} {ox+405},{oy+230} Z"
    )
    path(dwg, island_path, stroke=C["surface"], width=4, fill=C["island"])
    text(dwg, ox + 535, oy + 284, "交通島", size=24, weight=700, anchor="middle")

    # Crosswalks: approximate locations from the completion image.
    crossings = [
        (ox + 235, oy + 132, 26),
        (ox + 315, oy + 182, -8),
        (ox + 640, oy + 206, 36),
        (ox + 740, oy + 375, 29),
        (ox + 785, oy + 495, 23),
        (ox + 165, oy + 178, 76),
    ]
    for cx, cy, angle in crossings:
        crosswalk(dwg, cx, cy, angle)
        ped_signal(dwg, cx - 42, cy - 25)
        ped_signal(dwg, cx + 42, cy + 25)

    # Labels and leader lines.
    text(dwg, ox + 72, oy + 35, "新設道路側\n（三ツ境下草柳線）", size=22, weight=700, fill=C["connector"])
    line(dwg, (ox + 175, oy + 73), (ox + 210, oy + 97), stroke=C["connector"], width=3)

    text(dwg, ox + 700, oy + 555, "三ツ境駅前からの\n既存道路側", size=22, weight=700, fill=C["surface"])
    line(dwg, (ox + 720, oy + 508), (ox + 678, oy + 478), stroke=C["surface"], width=3)

    text(dwg, ox + 500, oy + 84, "横断歩道・歩行者信号を複数追加", size=20, weight=700, fill=C["ped"], anchor="middle")
    text(dwg, ox + 500, oy + 595, "※線形・横断歩道位置は読みやすさのため単純化。正確な寸法図ではありません。", size=18, weight=500, fill=C["muted"], anchor="middle")


def draw_levels(dwg):
    x, y, w, h = 1060, 145, 485, 700
    panel(dwg, x, y, w, h, "上下関係", "ここが今回の重要点")

    cx = x + w / 2

    # Rail: upper level.
    text(dwg, x + 38, y + 145, "上", size=24, weight=700, fill=C["rail"])
    line(dwg, (x + 100, y + 140), (x + w - 48, y + 185), stroke="#ffffff", width=24)
    line(dwg, (x + 100, y + 140), (x + w - 48, y + 185), stroke=C["rail"], width=10)
    text(dwg, cx, y + 125, "相鉄線", size=22, weight=700, fill=C["rail"], anchor="middle")

    # Ground: surface intersection.
    text(dwg, x + 38, y + 330, "地上", size=24, weight=700, fill=C["surface"])
    dwg.add(dwg.rect(insert=(x + 100, y + 285), size=(w - 150, 88), rx=18, ry=18, fill="#ffedd5", stroke=C["connector"], stroke_width=4))
    text(dwg, cx + 15, y + 322, "1号交差点", size=25, weight=700, fill=C["connector"], anchor="middle")
    text(dwg, cx + 15, y + 350, "交通島・横断歩道・信号", size=18, weight=500, fill=C["muted"], anchor="middle")

    # Underpass: lower level.
    text(dwg, x + 38, y + 520, "下", size=24, weight=700, fill=C["under"])
    path(dwg, f"M {x+105},{y+520} C {x+185},{y+490} {x+285},{y+548} {x+w-45},{y+515}", stroke=C["under"], width=14, dash="22,14")
    text(dwg, cx + 10, y + 575, "県道45号（中原街道）\nアンダーパス", size=22, weight=700, fill=C["under"], anchor="middle")

    # Vertical separators / explanation.
    line(dwg, (x + 74, y + 205), (x + w - 36, y + 205), stroke=C["border"], width=2, dash="7,7")
    line(dwg, (x + 74, y + 420), (x + w - 36, y + 420), stroke=C["border"], width=2, dash="7,7")

    dwg.add(dwg.rect(insert=(x + 30, y + 615), size=(w - 60, 62), rx=14, ry=14, fill=C["note"], stroke=C["note_border"], stroke_width=2))
    text(dwg, cx, y + 652, "3つを同じ平面の交差点として見ると誤解します", size=18, weight=700, fill="#9a3412", anchor="middle")


def main():
    svg = OUT / "06-official-2026-schematic.svg"
    png = OUT / "06-official-2026-schematic.png"
    dwg = svgwrite.Drawing(str(svg), size=(W, H), viewBox=f"0 0 {W} {H}")
    dwg.add(dwg.rect(insert=(0, 0), size=(W, H), fill=C["bg"]))

    text(dwg, 55, 58, "1号交差点：2026年8月の完成イメージを立体構造と合わせて読む", size=36, weight=700)
    text(dwg, 55, 105, "現況OSMで確認した上下関係と、横浜市の最新工事説明会資料を分けて重ねずに整理", size=21, weight=500, fill=C["muted"])

    draw_surface_plan(dwg)
    draw_levels(dwg)

    dwg.add(dwg.rect(insert=(55, 875), size=(1490, 115), rx=16, ry=16, fill=C["card"], stroke=C["border"], stroke_width=2))
    text(dwg, 80, 914, "結論", size=22, weight=700)
    text(dwg, 155, 914, "県道45号のアンダーパスを新しい大交差点に作り替えるのではなく、地上で既存道路と新設道路を交通島まわりに接続し、横断歩道・信号を追加する計画です。", size=20, weight=600)
    text(dwg, 155, 954, "2018年資料には5段階の信号パターン検討案がありますが、2026年の最終的な車両信号現示・秒数までは今回の公開資料から断定していません。", size=18, weight=500, fill=C["muted"])

    text(dwg, W - 55, H - 26, "Sources: 横浜市 工事説明会資料（2026-08-06/08）・OpenStreetMap current geometry", size=18, weight=500, fill=C["muted"], anchor="end")

    dwg.save()
    cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=W)


if __name__ == "__main__":
    main()
