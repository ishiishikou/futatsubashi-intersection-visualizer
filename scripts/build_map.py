#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import cairosvg
import geopandas as gpd
import osmnx as ox
import svgwrite
from shapely.geometry import LineString, MultiLineString
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.json"
OUT_DIR = ROOT / "docs" / "generated"
WIDTH = 1600
HEIGHT = 1000
PAD = 90

COLORS = {
    "bg": "#f8fafc",
    "road": "#cbd5e1",
    "route45": "#15803d",
    "underpass": "#166534",
    "connector": "#ea580c",
    "rail": "#7c2d12",
    "rail_halo": "#ffffff",
    "text": "#0f172a",
    "muted": "#475569",
    "panel": "#ffffff",
    "border": "#cbd5e1",
}


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def text_has_any(value, needles: Iterable[str]) -> bool:
    if value is None:
        return False
    text = str(value)
    return any(n in text for n in needles)


def truthy_tag(value) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, tuple, set)):
        return any(truthy_tag(v) for v in value)
    return str(value).strip().lower() in {"yes", "true", "1", "covered", "tunnel"}


def layer_num(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (list, tuple, set)):
        nums = [layer_num(v) for v in value]
        return min(nums) if nums else 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def only_lines(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    return gdf[gdf.geometry.geom_type.isin(["LineString", "MultiLineString"])].copy()


def project_pair(roads: gpd.GeoDataFrame, rail: gpd.GeoDataFrame):
    roads_p = ox.projection.project_gdf(roads)
    rail_p = rail.to_crs(roads_p.crs)
    return roads_p, rail_p


def select_route45(roads: gpd.GeoDataFrame, cfg: dict) -> gpd.GeoDataFrame:
    name_keys = cfg["route45_name_keywords"]
    ref_keys = cfg["route45_ref_keywords"]
    mask = roads.apply(
        lambda r: text_has_any(r.get("name"), name_keys)
        or text_has_any(r.get("ref"), ref_keys),
        axis=1,
    )
    return roads[mask].copy()


def select_connector(roads: gpd.GeoDataFrame, cfg: dict) -> gpd.GeoDataFrame:
    keys = cfg["surface_connector_keywords"]
    mask = roads.apply(lambda r: text_has_any(r.get("name"), keys), axis=1)
    return roads[mask].copy()


def below_grade_mask(gdf: gpd.GeoDataFrame):
    return gdf.apply(
        lambda r: (
            truthy_tag(r.get("tunnel"))
            or truthy_tag(r.get("covered"))
            or layer_num(r.get("layer")) < 0
        ),
        axis=1,
    )


def rail_above_grade_mask(gdf: gpd.GeoDataFrame):
    return gdf.apply(
        lambda r: truthy_tag(r.get("bridge")) or layer_num(r.get("layer")) > 0,
        axis=1,
    )


def iter_lines(geom):
    if isinstance(geom, LineString):
        yield geom
    elif isinstance(geom, MultiLineString):
        yield from geom.geoms


def all_bounds(*gdfs: gpd.GeoDataFrame):
    geoms = []
    for gdf in gdfs:
        if gdf is not None and not gdf.empty:
            geoms.extend(list(gdf.geometry))
    if not geoms:
        raise RuntimeError("No geometry found for SVG bounds.")
    return unary_union(geoms).bounds


def make_transform(bounds, width=WIDTH, height=HEIGHT, pad=PAD):
    minx, miny, maxx, maxy = bounds
    spanx = max(maxx - minx, 1)
    spany = max(maxy - miny, 1)
    scale = min((width - 2 * pad) / spanx, (height - 2 * pad) / spany)
    used_w = spanx * scale
    used_h = spany * scale
    xoff = (width - used_w) / 2
    yoff = (height - used_h) / 2

    def xy(x, y):
        sx = xoff + (x - minx) * scale
        sy = height - (yoff + (y - miny) * scale)
        return sx, sy

    return xy, scale


def line_path(geom, xy) -> str:
    pts = [xy(x, y) for x, y in geom.coords]
    if not pts:
        return ""
    head = f"M {pts[0][0]:.2f},{pts[0][1]:.2f}"
    tail = " ".join(f"L {x:.2f},{y:.2f}" for x, y in pts[1:])
    return f"{head} {tail}".strip()


def draw_gdf(
    dwg,
    group,
    gdf,
    xy,
    *,
    stroke,
    width,
    opacity=1.0,
    dash=None,
    linecap="round",
):
    if gdf is None or gdf.empty:
        return
    for geom in gdf.geometry:
        for line in iter_lines(geom):
            d = line_path(line, xy)
            if not d:
                continue
            attrs = {
                "fill": "none",
                "stroke": stroke,
                "stroke_width": width,
                "stroke_opacity": opacity,
                "stroke_linecap": linecap,
                "stroke_linejoin": "round",
                "vector_effect": "non-scaling-stroke",
            }
            if dash:
                attrs["stroke_dasharray"] = dash
            group.add(dwg.path(d=d, **attrs))


def centroid_xy(gdf, xy):
    if gdf is None or gdf.empty:
        return None
    c = unary_union(list(gdf.geometry)).centroid
    return xy(c.x, c.y)


def add_label(dwg, x, y, text, *, anchor="middle", size=30, weight=700, fill=None):
    fill = fill or COLORS["text"]
    lines = text.split("\n")
    t = dwg.text(
        "",
        insert=(x, y),
        text_anchor=anchor,
        fill=fill,
        font_size=size,
        font_family="'Noto Sans CJK JP','Noto Sans JP',sans-serif",
        font_weight=weight,
    )
    for i, line in enumerate(lines):
        t.add(dwg.tspan(line, x=[x], dy=[0 if i == 0 else size * 1.25]))
    dwg.add(t)


def add_callout(dwg, x, y, title, body, *, accent, box_w=420, box_h=150):
    g = dwg.g()
    g.add(
        dwg.rect(
            insert=(x, y),
            size=(box_w, box_h),
            rx=18,
            ry=18,
            fill=COLORS["panel"],
            stroke=accent,
            stroke_width=3,
        )
    )
    g.add(
        dwg.text(
            title,
            insert=(x + 24, y + 42),
            fill=accent,
            font_size=28,
            font_family="'Noto Sans CJK JP','Noto Sans JP',sans-serif",
            font_weight=700,
        )
    )
    body_t = dwg.text(
        "",
        insert=(x + 24, y + 82),
        fill=COLORS["muted"],
        font_size=22,
        font_family="'Noto Sans CJK JP','Noto Sans JP',sans-serif",
        font_weight=500,
    )
    for i, line in enumerate(body.split("\n")):
        body_t.add(dwg.tspan(line, x=[x + 24], dy=[0 if i == 0 else 30]))
    g.add(body_t)
    dwg.add(g)


def render_svg_current(roads, rail, route45, underpass, connector, out_path: Path):
    bounds = all_bounds(roads, rail)
    xy, _ = make_transform(bounds)
    dwg = svgwrite.Drawing(str(out_path), size=(WIDTH, HEIGHT), viewBox=f"0 0 {WIDTH} {HEIGHT}")
    dwg.add(dwg.rect(insert=(0, 0), size=(WIDTH, HEIGHT), fill=COLORS["bg"]))

    add_label(dwg, 70, 60, "現況構造：OSMの実データを高さタグ付きで表示", anchor="start", size=34)
    add_label(
        dwg,
        70,
        105,
        "まず現況の立体関係だけを検証し、将来計画はまだ重ねない",
        anchor="start",
        size=22,
        weight=500,
        fill=COLORS["muted"],
    )

    g = dwg.g(id="map")
    draw_gdf(dwg, g, roads, xy, stroke=COLORS["road"], width=4, opacity=0.95)
    draw_gdf(dwg, g, route45, xy, stroke=COLORS["route45"], width=10, opacity=0.96)
    draw_gdf(
        dwg,
        g,
        underpass,
        xy,
        stroke=COLORS["underpass"],
        width=16,
        opacity=1,
        dash="18,12",
    )
    draw_gdf(dwg, g, connector, xy, stroke=COLORS["connector"], width=11, opacity=1)

    # Railway is deliberately drawn after the road underpass so the over/under relation is visible.
    draw_gdf(dwg, g, rail, xy, stroke=COLORS["rail_halo"], width=15, opacity=1)
    draw_gdf(dwg, g, rail, xy, stroke=COLORS["rail"], width=7, opacity=1)
    dwg.add(g)

    p = centroid_xy(underpass, xy)
    if p:
        add_label(dwg, p[0] + 95, p[1] + 75, "県道45号\n線路下区間", anchor="start", size=27, fill=COLORS["underpass"])

    p = centroid_xy(rail, xy)
    if p:
        add_label(dwg, p[0] - 30, p[1] - 45, "相鉄線", anchor="end", size=28, fill=COLORS["rail"])

    if connector is not None and not connector.empty:
        p = centroid_xy(connector, xy)
        if p:
            add_label(dwg, p[0] + 20, p[1] - 35, "三ツ境下草柳線", anchor="start", size=25, fill=COLORS["connector"])

    legend_x, legend_y = 70, 770
    dwg.add(
        dwg.rect(
            insert=(legend_x, legend_y),
            size=(620, 160),
            rx=16,
            ry=16,
            fill="#ffffff",
            stroke=COLORS["border"],
            stroke_width=2,
        )
    )
    items = [
        (COLORS["route45"], None, "中原街道（県道45号）"),
        (COLORS["underpass"], "18,12", "線路下・地下扱いの区間（OSMタグ）"),
        (COLORS["rail"], None, "相鉄線"),
        (COLORS["connector"], None, "三ツ境下草柳線（OSMで名称一致した場合）"),
    ]
    for i, (color, dash, label) in enumerate(items):
        yy = legend_y + 32 + i * 31
        attrs = {"stroke": color, "stroke_width": 8, "stroke_linecap": "round"}
        if dash:
            attrs["stroke_dasharray"] = dash
        dwg.add(dwg.line(start=(legend_x + 22, yy), end=(legend_x + 95, yy), **attrs))
        add_label(dwg, legend_x + 115, yy + 7, label, anchor="start", size=19, weight=500)

    add_label(
        dwg,
        WIDTH - 70,
        HEIGHT - 35,
        "© OpenStreetMap contributors (ODbL)",
        anchor="end",
        size=18,
        weight=500,
        fill=COLORS["muted"],
    )
    dwg.save()


def render_svg_grade_separation(route45, underpass, rail, out_path: Path):
    focus = gpd.GeoDataFrame(
        geometry=list(route45.geometry) + list(rail.geometry),
        crs=route45.crs,
    )
    bounds = all_bounds(focus)
    xy, _ = make_transform(bounds, width=WIDTH, height=HEIGHT, pad=150)

    dwg = svgwrite.Drawing(str(out_path), size=(WIDTH, HEIGHT), viewBox=f"0 0 {WIDTH} {HEIGHT}")
    dwg.add(dwg.rect(insert=(0, 0), size=(WIDTH, HEIGHT), fill=COLORS["bg"]))

    add_label(dwg, 70, 65, "立体関係だけを分離して確認", anchor="start", size=38)
    add_label(
        dwg,
        70,
        115,
        "同じ平面交差点として描かず、OSMの tunnel / layer / bridge タグを優先",
        anchor="start",
        size=22,
        weight=500,
        fill=COLORS["muted"],
    )

    g = dwg.g(id="grade-separation")
    draw_gdf(dwg, g, route45, xy, stroke=COLORS["route45"], width=18, opacity=0.95)
    draw_gdf(dwg, g, underpass, xy, stroke=COLORS["underpass"], width=26, opacity=1, dash="22,14")
    draw_gdf(dwg, g, rail, xy, stroke=COLORS["rail_halo"], width=22, opacity=1)
    draw_gdf(dwg, g, rail, xy, stroke=COLORS["rail"], width=10, opacity=1)
    dwg.add(g)

    p_under = centroid_xy(underpass, xy)
    p_rail = centroid_xy(rail, xy)

    if p_under:
        add_callout(
            dwg,
            80,
            720,
            "県道45号：下",
            "tunnel / covered / layer<0 の\nいずれかをOSMから検出",
            accent=COLORS["underpass"],
            box_w=450,
            box_h=155,
        )
        dwg.add(
            dwg.line(
                start=(530, 760),
                end=(p_under[0] - 15, p_under[1] + 10),
                stroke=COLORS["underpass"],
                stroke_width=3,
            )
        )

    if p_rail:
        add_callout(
            dwg,
            1070,
            720,
            "相鉄線：上",
            "道路の下区間より後に描画し、\n上下関係を視覚的に固定",
            accent=COLORS["rail"],
            box_w=450,
            box_h=155,
        )
        dwg.add(
            dwg.line(
                start=(1070, 760),
                end=(p_rail[0] + 15, p_rail[1] - 10),
                stroke=COLORS["rail"],
                stroke_width=3,
            )
        )

    add_label(
        dwg,
        WIDTH / 2,
        930,
        "この図で上下関係を確認できてから、地上側の新設道路・信号を別レイヤーで追加する",
        anchor="middle",
        size=24,
        weight=600,
    )
    add_label(
        dwg,
        WIDTH - 70,
        HEIGHT - 30,
        "© OpenStreetMap contributors (ODbL)",
        anchor="end",
        size=18,
        weight=500,
        fill=COLORS["muted"],
    )
    dwg.save()


def write_metadata(cfg, center, roads, rail, route45, underpass, connector):
    def slim_records(gdf):
        rows = []
        if gdf is None or gdf.empty:
            return rows
        keep = ["name", "ref", "tunnel", "covered", "layer", "bridge", "highway", "railway"]
        for idx, row in gdf.iterrows():
            item = {"osm_index": str(idx)}
            for key in keep:
                if key in row and row.get(key) is not None:
                    value = row.get(key)
                    if isinstance(value, (list, tuple, set)):
                        value = list(value)
                    item[key] = value
            rows.append(item)
        return rows

    meta = {
        "center_query": cfg["center_query"],
        "center_latlon": [center[0], center[1]],
        "distance_m": cfg["distance_m"],
        "counts": {
            "road_features": int(len(roads)),
            "rail_features": int(len(rail)),
            "route45_features": int(len(route45)),
            "underpass_features": int(len(underpass)),
            "surface_connector_features": int(len(connector)),
        },
        "route45_tags": slim_records(route45),
        "underpass_tags": slim_records(underpass),
        "rail_tags": slim_records(rail),
        "surface_connector_tags": slim_records(connector),
    }
    (OUT_DIR / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def write_index():
    html = """<!doctype html>
<html lang="ja">
<meta charset="utf-8">
<title>Futatsubashi intersection visualizer</title>
<style>
body{font-family:system-ui,-apple-system,"Noto Sans JP",sans-serif;margin:40px;background:#f8fafc;color:#0f172a}
main{max-width:1200px;margin:auto}
figure{background:white;padding:18px;border:1px solid #cbd5e1;border-radius:16px;margin:24px 0}
img{width:100%;height:auto;display:block}
small{color:#475569}
</style>
<main>
<h1>二ツ橋周辺・現況構造の検証</h1>
<p>将来計画を重ねる前に、OpenStreetMap の公開データだけで現況の道路と鉄道の上下関係を確認します。</p>
<figure><img src="01-current-osm.png" alt="現況OSM構造"><figcaption>01: 現況道路・鉄道・高さタグ</figcaption></figure>
<figure><img src="02-grade-separation.png" alt="立体交差"><figcaption>02: 県道45号と相鉄線の立体関係だけを抽出</figcaption></figure>
<p><small>© OpenStreetMap contributors (ODbL)</small></p>
</main>
</html>
"""
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")


def main():
    cfg = load_config()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ox.settings.use_cache = True
    ox.settings.log_console = True

    center = ox.geocode(cfg["center_query"])
    roads = ox.features_from_point(center, tags={"highway": True}, dist=cfg["distance_m"])
    rail = ox.features_from_point(
        center,
        tags={"railway": cfg["railway_types"]},
        dist=cfg["distance_m"],
    )

    roads = only_lines(roads)
    rail = only_lines(rail)
    if roads.empty:
        raise RuntimeError("No road features were returned from OpenStreetMap.")
    if rail.empty:
        raise RuntimeError("No railway features were returned from OpenStreetMap.")

    roads_p, rail_p = project_pair(roads, rail)
    route45 = select_route45(roads_p, cfg)
    connector = select_connector(roads_p, cfg)

    if route45.empty:
        raise RuntimeError("Could not identify Route 45 / Nakahara Kaido from OSM tags.")

    underpass = route45[below_grade_mask(route45)].copy()
    rail_above = rail_p[rail_above_grade_mask(rail_p)].copy()

    if underpass.empty and rail_above.empty:
        raise RuntimeError(
            "No explicit grade-separation tags were found on Route 45 or the railway. "
            "Do not render a guessed flat intersection."
        )

    svg1 = OUT_DIR / "01-current-osm.svg"
    svg2 = OUT_DIR / "02-grade-separation.svg"
    render_svg_current(roads_p, rail_p, route45, underpass, connector, svg1)
    render_svg_grade_separation(route45, underpass, rail_p, svg2)

    cairosvg.svg2png(url=str(svg1), write_to=str(OUT_DIR / "01-current-osm.png"), output_width=1600)
    cairosvg.svg2png(url=str(svg2), write_to=str(OUT_DIR / "02-grade-separation.png"), output_width=1600)

    write_metadata(cfg, center, roads_p, rail_p, route45, underpass, connector)
    write_index()

    print(json.dumps({
        "center": center,
        "route45_features": len(route45),
        "underpass_features": len(underpass),
        "rail_features": len(rail_p),
        "rail_above_features": len(rail_above),
        "connector_features": len(connector),
        "outputs": [str(svg1.relative_to(ROOT)), str(svg2.relative_to(ROOT))],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
