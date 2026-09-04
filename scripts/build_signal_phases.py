#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import cairosvg
import svgwrite

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1600, 1000
FONT = "'Noto Sans CJK JP','Noto Sans JP',sans-serif"
C = {
    "bg": "#f8fafc",
    "card": "#ffffff",
    "border": "#cbd5e1",
    "text": "#0f172a",
    "muted": "#475569",
    "inactive": "#cbd5e1",
    "active": "#15803d",
    "ped": "#0369a1",
    "warning": "#b45309",
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
        t.add(dwg.tspan(line, x=[x], dy=[0 if i == 0 else size * 1.25]))
    dwg.add(t)


def arrow_marker(dwg, color, marker_id):
    m = dwg.marker(insert=(10, 5), size=(10, 10), orient="auto", id=marker_id)
    m.add(dwg.path(d="M 0 0 L 10 5 L 0 10 z", fill=color))
    dwg.defs.add(m)
    return m


def route(dwg, start, end, *, color, width=8, marker=None, dash=None):
    attrs = dict(stroke=color, stroke_width=width, stroke_linecap="round")
    if marker is not None:
        attrs["marker_end"] = marker.get_funciri()
    if dash:
        attrs["stroke_dasharray"] = dash
    dwg.add(dwg.line(start=start, end=end, **attrs))


def base_intersection(dwg, x, y, w, h):
    cx = x + w / 2
    cy = y + h * 0.56
    left = x + 38
    right = x + w - 38
    bottom = y + h - 34

    # The 2018 source identifies the horizontal road as Mitsukyo-Shimokusayanagi
    # and two separate Nakahara-kaido side-road approaches. This is schematic only.
    route(dwg, (left, cy), (right, cy), color=C["inactive"], width=16)
    route(dwg, (cx - 58, bottom), (cx - 18, cy + 6), color=C["inactive"], width=14)
    route(dwg, (cx + 58, bottom), (cx + 18, cy + 6), color=C["inactive"], width=14)

    text(dwg, cx, y + 28, "三ツ境下草柳線", size=17, weight=600, fill=C["muted"], anchor="middle")
    text(dwg, cx - 80, bottom + 18, "側道 西", size=16, weight=500, fill=C["muted"], anchor="middle")
    text(dwg, cx + 80, bottom + 18, "側道 東", size=16, weight=500, fill=C["muted"], anchor="middle")
    return cx, cy, left, right, bottom


def card(dwg, x, y, w, h, number, title, description, mode, green, blue):
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=18, ry=18, fill=C["card"], stroke=C["border"], stroke_width=2))
    text(dwg, x + 22, y + 38, f"{number}", size=26, weight=700)
    text(dwg, x + 62, y + 38, title, size=23, weight=700)
    text(dwg, x + 22, y + 72, description, size=17, weight=500, fill=C["muted"])

    ix, iy, iw, ih = x + 18, y + 96, w - 36, h - 126
    cx, cy, left, right, bottom = base_intersection(dwg, ix, iy, iw, ih)

    if mode == "main":
        route(dwg, (left + 20, cy), (right - 20, cy), color=C["active"], width=10, marker=green)
        # Small diverging arrows convey left-turn permission without asserting exact lane geometry.
        route(dwg, (cx - 88, cy), (cx - 45, cy + 58), color=C["active"], width=7, marker=green)
        route(dwg, (cx + 88, cy), (cx + 45, cy + 58), color=C["active"], width=7, marker=green)
    elif mode == "right":
        route(dwg, (cx - 100, cy), (cx - 42, cy + 68), color=C["active"], width=9, marker=green)
        route(dwg, (cx + 100, cy), (cx + 42, cy + 68), color=C["active"], width=9, marker=green)
    elif mode == "west":
        route(dwg, (cx - 58, bottom - 12), (cx - 12, cy - 2), color=C["active"], width=9, marker=green)
    elif mode == "east":
        route(dwg, (cx + 58, bottom - 12), (cx + 12, cy - 2), color=C["active"], width=9, marker=green)
    elif mode == "ped":
        # Cars are intentionally not given active arrows in this phase.
        route(dwg, (cx - 82, cy - 52), (cx + 82, cy + 52), color=C["ped"], width=7, marker=blue, dash="12,8")
        route(dwg, (cx + 82, cy - 52), (cx - 82, cy + 52), color=C["ped"], width=7, marker=blue, dash="12,8")
        text(dwg, cx, cy + 8, "歩行者", size=20, weight=700, fill=C["ped"], anchor="middle")


def main():
    svg = OUT / "05-signal-phases-2018.svg"
    png = OUT / "05-signal-phases-2018.png"
    dwg = svgwrite.Drawing(str(svg), size=(W, H), viewBox=f"0 0 {W} {H}")
    dwg.add(dwg.rect(insert=(0, 0), size=(W, H), fill=C["bg"]))

    text(dwg, 70, 60, "1号交差点：2018年に公表された信号パターン検討案", size=36, weight=700)
    text(dwg, 70, 105, "これは最終信号現示ではありません。横浜市資料の5段階を、道路の上下関係を誤解しないよう地上部分だけで模式化しています。", size=20, weight=500, fill=C["muted"])

    green = arrow_marker(dwg, C["active"], "green-arrow")
    blue = arrow_marker(dwg, C["ped"], "blue-arrow")

    cards = [
        ("①", "本線", "直進・左折", "main"),
        ("②", "本線", "右折（2方向）", "right"),
        ("③", "側道 西", "西側から進行", "west"),
        ("④", "側道 東", "東側から進行", "east"),
        ("⑤", "歩行者", "車両と分離", "ped"),
    ]
    gap = 18
    card_w = (W - 140 - gap * 4) / 5
    x = 70
    for num, title, desc, mode in cards:
        card(dwg, x, 160, card_w, 610, num, title, desc, mode, green, blue)
        x += card_w + gap

    dwg.add(dwg.rect(insert=(70, 805), size=(1460, 110), rx=16, ry=16, fill="#fff7ed", stroke="#fed7aa", stroke_width=2))
    text(dwg, 94, 842, "読み方", size=21, weight=700, fill=C["warning"])
    text(dwg, 185, 842, "県道45号の線路下本線を5段階で止める図ではなく、地上の三ツ境下草柳線と中原街道側道を分けて処理する検討案です。", size=19, weight=600)
    text(dwg, 185, 878, "横浜市は当時『歩行者、車両の双方が交差点内で錯綜しないよう検討』と説明し、運用状況等で変更する可能性も明記しています。", size=18, weight=500, fill=C["muted"])

    text(dwg, W - 70, H - 32, "Source: 横浜市 第1期地区まちづくりニュース 第7号 別紙 (2018-05-18)", size=17, weight=500, fill=C["muted"], anchor="end")
    dwg.save()
    cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=W)


if __name__ == "__main__":
    main()
