"""Render audit notices only. No road geometry is inferred here."""
from pathlib import Path
import xml.etree.ElementTree as ET
import cairosvg
from validate_evidence import ROOT, read, validate

NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
OUT=ROOT/'docs/generated'

def notice(name,title,lines,status):
    svg=ET.Element(f'{{{NS}}}svg',{'width':'1200','height':'600','viewBox':'0 0 1200 600','data-status':status})
    ET.SubElement(svg,f'{{{NS}}}title').text=title
    ET.SubElement(svg,f'{{{NS}}}rect',{'width':'1200','height':'600','fill':'#f8fafc'})
    for i,(text,size,color) in enumerate([(title,38,'#9a3412')]+[(s,26,'#0f172a') for s in lines]):
        el=ET.SubElement(svg,f'{{{NS}}}text',{'x':'50','y':str(85+i*72),'font-size':str(size),'font-family':'Noto Sans CJK JP, sans-serif','fill':color})
        el.text=text
    ET.indent(svg)
    path=OUT/f'{name}.svg';ET.ElementTree(svg).write(path,encoding='utf-8',xml_declaration=True)
    cairosvg.svg2png(url=str(path),write_to=str(OUT/f'{name}.png'))

def main():
    errors=validate(read(ROOT/'data/evidence.json'),read(ROOT/'data/gates.json'),read(ROOT/'data/osm-corroboration.json'))
    if errors:raise ValueError(errors)
    OUT.mkdir(exist_ok=True)
    notice('evidence-status','精密復元は未完了：Gate 1で停止',[
        '確認済み：資料の版・根拠14件・OSM補助データ23 way',
        '旧図の問題：交通島・横断歩道配置・歩行者の斜め横断',
        '停止理由：道路台帳の利用規約同意待ち／対象図面未閲覧',
        '未確定：現況基図・位置合わせ・完成後の右左折・最終信号',
        '調査 2026-11-03／再開 11-04　詳細：docs/independent-audit.md'
    ],'partial')
    notice('05-signal-phases-2018','旧信号模式図を撤回しました',[
        '原資料にない斜め横断と、不整合のある車両矢印を削除。',
        '2018年資料の5群は docs/movement-review.md の表を参照。',
        '2026年の最終現示・秒数・灯器位置は未確定です。',
        '道路構造・通行案内として旧図を使用しないでください。'
    ],'withdrawn')
    notice('06-official-2026-schematic','旧完成模式図を撤回しました',[
        '基準点なしの線形・楕円交通島・横断歩道配置を撤回。',
        '道路台帳と版を確認した計画図の位置合わせが必要です。',
        '基準点・変換係数・残差は未計測。誤差ゼロではありません。',
        '詳細：docs/independent-audit.md／data/gates.json'
    ],'withdrawn')
    (OUT/'index.html').write_text('''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>二ツ橋1号交差点：検証状況</title><style>body{font-family:system-ui;margin:24px;max-width:1200px}img{width:100%;height:auto}p{line-height:1.7}</style><h1>精密復元は未完了</h1><p>道路台帳の対象図面は未閲覧です。以下は検証状況と旧図の撤回通知です。</p><p><a href="../independent-audit.md">調査記録</a> ／ <a href="../movement-review.md">動線・信号</a></p>'''+''.join(f'<p><a href="{n}.svg"><img src="{n}.png" alt="{label}"></a></p>' for n,label in [('evidence-status','検証状況'),('05-signal-phases-2018','信号図撤回'),('06-official-2026-schematic','完成図撤回')])+ '</html>')

if __name__=='__main__':main()
