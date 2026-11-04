"""Render Muse's design-study schematics.

These figures are a design proposal (私案), NOT a reconstruction of the
official plan. They must always carry the design-study disclaimer; the
validator enforces its presence. SVG is the master; PNG is a derivative.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import cairosvg
from validate_evidence import ROOT, read, validate

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
OUT = ROOT / 'docs/generated'

INK = '#0f172a'
MUTED = '#475569'
ACCENT = '#9a3412'
BLUE = '#1d4ed8'
GRAY = '#64748b'
GREEN = '#15803d'
RED = '#b91c1c'
FONT = 'Noto Sans CJK JP, sans-serif'


def el(parent, tag, **attrs):
    return ET.SubElement(parent, f'{{{NS}}}{tag}', {k: str(v) for k, v in attrs.items()})


def text(parent, x, y, s, size=20, fill=INK, anchor='start', weight=None, spacing=None):
    a = {'x': x, 'y': y, 'font-size': size, 'font-family': FONT, 'fill': fill, 'text-anchor': anchor}
    if weight:
        a['font-weight'] = weight
    if spacing:
        a['letter-spacing'] = spacing
    t = el(parent, 'text', **a)
    t.text = s
    return t


def box(parent, x, y, w, h, fill, stroke, r=10, dash=None, width=2):
    a = {'x': x, 'y': y, 'width': w, 'height': h, 'rx': r, 'fill': fill, 'stroke': stroke, 'stroke-width': width}
    if dash:
        a['stroke-dasharray'] = dash
    return el(parent, 'rect', **a)


def line(parent, x1, y1, x2, y2, stroke=INK, width=2, dash=None):
    a = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'stroke': stroke, 'stroke-width': width}
    if dash:
        a['stroke-dasharray'] = dash
    return el(parent, 'line', **a)


def header(svg, title, subtitle):
    text(svg, 50, 52, title, size=34, weight='bold')
    text(svg, 50, 90, subtitle, size=22, fill=ACCENT, weight='bold')


def save(svg, name):
    ET.indent(svg)
    path = OUT / f'{name}.svg'
    ET.ElementTree(svg).write(path, encoding='utf-8', xml_declaration=True)
    cairosvg.svg2png(url=str(path), write_to=str(OUT / f'{name}.png'))


def levels():
    svg = ET.Element(f'{{{NS}}}svg', {'width': '1200', 'height': '820', 'viewBox': '0 0 1200 820',
                                      'data-status': 'design-study', 'data-figure-class': 'design-study'})
    el(svg, 'title').text = '立体分離の模式図（設計検討・私案）'
    el(svg, 'rect', width='1200', height='820', fill='#f8fafc')
    header(svg, '立体分離の模式図（設計検討）',
           'Muse の設計検討（私案）／公式計画ではありません／復元図ではありません')

    # Band A: railway
    box(svg, 40, 116, 1120, 130, '#eef2ff', '#6366f1')
    text(svg, 64, 152, '鉄道：相鉄線', size=24, weight='bold')
    line(svg, 64, 196, 1136, 196, stroke='#4338ca', width=3)
    line(svg, 64, 208, 1136, 208, stroke='#4338ca', width=3)
    text(svg, 1136, 152, '地上の交通とは混ざらない', size=20, fill=MUTED, anchor='end')

    # connector A-B
    line(svg, 600, 246, 600, 302, stroke=MUTED, width=2, dash='6 5')
    text(svg, 616, 282, '交差箇所：立体分離（接続なし）', size=20, fill=MUTED)

    # Band B: surface
    box(svg, 40, 302, 1120, 140, '#f1f5f9', GRAY)
    text(svg, 64, 338, '地上：1号交差点（信号交差点）', size=24, weight='bold')
    for x, label in [(64, '西側側道'), (330, '駅側既存道路'), (620, '新設道路'), (880, '東側側道')]:
        box(svg, x, 356, 240, 44, '#ffffff', GRAY, r=8, width=1.5)
        text(svg, x + 120, 386, label, size=20, anchor='middle')
    line(svg, 64, 430, 1136, 430, stroke=GREEN, width=4)
    text(svg, 1136, 420, '歩道・横断歩道（地上）', size=19, fill=GREEN, anchor='end')

    # connector B-C
    line(svg, 300, 442, 300, 498, stroke=MUTED, width=2, dash='6 5')
    text(svg, 316, 478, '本線×地上：立体分離', size=20, fill=MUTED)
    line(svg, 900, 442, 900, 498, stroke=MUTED, width=2, dash='6 5')
    text(svg, 1136, 478, '地下通路：階段で接続', size=20, fill=MUTED, anchor='end')

    # Band C: underground
    box(svg, 40, 498, 1120, 140, '#fff7ed', '#ea580c')
    text(svg, 64, 534, '地下：地上とは接続しない構造物', size=24, weight='bold')
    box(svg, 64, 552, 660, 56, '#ffffff', '#ea580c', r=8, width=1.5)
    text(svg, 394, 588, '中原街道本線アンダーパス（二ツ橋地下道）', size=20, anchor='middle')
    box(svg, 748, 552, 388, 56, '#ffffff', GREEN, r=8, width=1.5)
    text(svg, 942, 588, '歩行者地下通路（階段）', size=20, anchor='middle')

    text(svg, 50, 692, '歩行者は地上横断が主動線、地下通路は補助という整理が私案。緑の線は地上の歩道・横断歩道を示す。', size=20, fill=MUTED)
    text(svg, 50, 728, 'この図は交差箇所ごとの上下関係を示す模式図です。全域が一律の三層構造であることを示すものではありません。', size=20, fill=MUTED)
    text(svg, 50, 764, '上下の分離関係は公式資料・現況データで確認済み。配置・縮尺は実測ではありません。', size=20, fill=MUTED)
    save(svg, 'design-levels-schematic')


def topology():
    svg = ET.Element(f'{{{NS}}}svg', {'width': '1200', 'height': '950', 'viewBox': '0 0 1200 950',
                                      'data-status': 'design-study', 'data-figure-class': 'design-study'})
    el(svg, 'title').text = '理想形の接続トポロジー（設計検討・私案）'
    el(svg, 'rect', width='1200', height='950', fill='#f8fafc')
    header(svg, '理想形の接続トポロジー（設計検討・私案）',
           'Muse の設計検討（私案）／公式計画ではありません／配置は模式化したもの')

    cx1, cx2, cy1, cy2 = 460, 740, 380, 500  # centre junction box

    # side arms (drawn first, under centre)
    box(svg, 545, 130, 110, 250, '#e2e8f0', GRAY)          # north arm (west side road)
    box(svg, 545, 500, 110, 212, '#e2e8f0', GRAY)          # south arm (east side road)
    # main axis band
    el(svg, 'rect', x='60', y='412', width='1080', height='56', fill='#dbeafe', stroke='none')
    # arms boxes
    box(svg, 60, 396, 250, 88, '#ffffff', BLUE)
    text(svg, 185, 434, '新設道路', size=22, anchor='middle', weight='bold')
    text(svg, 185, 464, '三ツ境下草柳線', size=19, anchor='middle', fill=MUTED)
    box(svg, 890, 396, 250, 88, '#ffffff', BLUE)
    text(svg, 1015, 434, '駅側既存道路', size=22, anchor='middle', weight='bold')
    text(svg, 1015, 464, '三ツ境駅方面', size=19, anchor='middle', fill=MUTED)
    text(svg, 600, 168, '西側側道', size=22, anchor='middle', weight='bold')
    text(svg, 600, 196, '中原街道（地上）', size=19, anchor='middle', fill=MUTED)
    text(svg, 600, 648, '東側側道', size=22, anchor='middle', weight='bold')
    text(svg, 600, 676, '中原街道（地上）', size=19, anchor='middle', fill=MUTED)

    # main axis through arrow
    line(svg, 330, 440, 870, 440, stroke=BLUE, width=6)
    el(svg, 'polygon', points='870,440 846,428 846,452', fill=BLUE)
    el(svg, 'polygon', points='330,440 354,428 354,452', fill=BLUE)
    text(svg, 430, 350, '主軸：直進・左折（群1）', size=21, anchor='middle', fill=BLUE, weight='bold')

    # right-turn note arrows (schematic curves)
    el(svg, 'path', d='M 700 412 Q 700 330 640 300', fill='none', stroke='#ea580c', **{'stroke-width': '4'})
    el(svg, 'polygon', points='636,296 652,306 630,314', fill='#ea580c')
    text(svg, 726, 322, '主軸の右折：専用現示（群2）', size=21, fill='#ea580c', weight='bold')

    # side road arrows
    line(svg, 585, 250, 585, 372, stroke=GRAY, width=4)
    el(svg, 'polygon', points='585,376 575,354 595,354', fill=GRAY)
    line(svg, 630, 508, 630, 620, stroke=GRAY, width=4)
    el(svg, 'polygon', points='630,624 620,602 640,602', fill=GRAY)
    text(svg, 676, 268, '側道：同時現示（群3）が私案', size=21, fill=MUTED, weight='bold')
    text(svg, 676, 300, '交錯する場合は西・東に分離', size=19, fill=MUTED)

    # pedestrian ticks on all four arms
    for (x, y) in [(420, 440), (780, 440), (600, 330), (600, 545)]:
        el(svg, 'circle', cx=str(x), cy=str(y), r='13', fill=GREEN)
        text(svg, x, y + 7, '歩', size=18, fill='#ffffff', anchor='middle', weight='bold')
    text(svg, 676, 560, '横断歩道：全脚設置＋歩行者群（群4）', size=21, fill=GREEN, weight='bold')

    # centre junction
    box(svg, cx1, cy1, cx2 - cx1, cy2 - cy1, '#ffffff', INK, width=2.5)
    text(svg, 600, 428, '1号交差点', size=26, anchor='middle', weight='bold')
    text(svg, 600, 462, '交通島：誘導＋歩行者待避', size=19, anchor='middle', fill=MUTED)
    text(svg, 600, 488, '信号交差点（私案）', size=19, anchor='middle', fill=MUTED)

    # bottom: separated structures
    box(svg, 60, 748, 1080, 64, '#fff7ed', '#ea580c', dash='8 6')
    text(svg, 84, 788, '中原街道本線（地下アンダーパス）', size=21, weight='bold')
    text(svg, 1116, 788, 'この交差点とは接続しない', size=21, anchor='end', fill=RED, weight='bold')
    box(svg, 60, 824, 1080, 56, '#f0fdf4', GREEN, dash='8 6')
    text(svg, 84, 860, '歩行者地下通路', size=21, weight='bold')
    text(svg, 1116, 860, '地上横断の補助（階段のみ）', size=21, anchor='end', fill=MUTED)

    text(svg, 50, 922, '右左折の可否・現示構成は私案であり、実際の交通規制・信号計画は未確定です。', size=20, fill=MUTED)
    save(svg, 'design-topology-schematic')


def main():
    errors = validate(read(ROOT / 'data/evidence.json'), read(ROOT / 'data/gates.json'), read(ROOT / 'data/osm-corroboration.json'))
    if errors:
        raise ValueError(errors)
    OUT.mkdir(exist_ok=True)
    levels()
    topology()
    (OUT / 'design-study.html').write_text('''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>二ツ橋1号交差点：Museの設計検討（私案）</title><style>body{font-family:system-ui;margin:24px;max-width:1200px}img{width:100%;height:auto}p{line-height:1.7}.warn{color:#9a3412;font-weight:bold}</style><h1>Museの設計検討（私案）</h1><p class="warn">これは設計検討であり、公式計画・完成形の復元ではありません。</p><p><a href="../design-study-muse.md">設計検討の本文</a> ／ <a href="index.html">検証状況ビュー</a></p>'''
        + ''.join(f'<p><a href="{n}.svg"><img src="{n}.png" alt="{label}"></a></p>' for n, label in
                  [('design-levels-schematic', '立体分離の模式図'), ('design-topology-schematic', '理想形の接続トポロジー')])
        + '</html>')


if __name__ == '__main__':
    main()
