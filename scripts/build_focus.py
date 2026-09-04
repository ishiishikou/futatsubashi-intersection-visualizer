#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import cairosvg
import geopandas as gpd
import osmnx as ox
import svgwrite
from shapely.geometry import LineString, MultiLineString, Point
from shapely.ops import nearest_points, unary_union

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "generated"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

W, H = 1600, 1000
FONT = "'Noto Sans CJK JP','Noto Sans JP',sans-serif"
C = {
    "bg": "#f8fafc",
    "surface": "#94a3b8",
    "surface_minor": "#cbd5e1",
    "route45": "#15803d",
    "under": "#166534",
    "connector": "#ea580c",
    "rail": "#7c2d12",
    "rail_halo": "#ffffff",
    "text": "#0f172a",
    "muted": "#475569",
    "panel": "#ffffff",
    "border": "#cbd5e1",
}


def only_lines(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    return gdf[gdf.geometry.geom_type.isin(["LineString", "MultiLineString"])].copy()


def text_has(value, needles: list[str]) -> bool:
    if value is None:
        return False
    s = str(value)
    return any(n in s for n in needles)


def truthy(value) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, tuple, set)):
        return any(truthy(v) for v in value)
    return str(value).strip().lower() in {"yes", "true", "1", "covered", "tunnel"}


def layer_num(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (list, tuple, set)):
        vals = [layer_num(v) for v in value]
        return min(vals) if vals else 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def iter_lines(geom):
    if isinstance(geom, LineString):
        yield geom
    elif isinstance(geom, MultiLineString):
        yield from geom.geoms


def line_path(line, xy) -> str:
    pts = [xy(x, y) for x, y in line.coords]
    if not pts:
        return ""
    return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def draw_gdf(dwg, group, gdf, xy, stroke, width, *, opacity=1.0, dash=None):
    if gdf is None or gdf.empty:
        return
    for geom in gdf.geometry:
        for line in iter_lines(geom):
            d = line_path(line, xy)
            if not d:
                continue
            attrs = dict(
                fill="none",
                stroke=stroke,
                stroke_width=width,
                stroke_opacity=opacity,
                stroke_linecap="round",
                stroke_linejoin="round",
            )
            if dash:
                attrs["stroke_dasharray"] = dash
            group.add(dwg.path(d=d, **attrs))


def add_text(dwg, x, y, text, *, size=26, weight=600, fill=None, anchor="start"):
    t = dwg.text(
        "",
        insert=(x, y),
        font_family=FONT,
        font_size=size,
        font_weight=weight,
        fill=fill or C["text"],
        text_anchor=anchor,
    )
    for i, line in enumerate(text.split("\n")):
        t.add(dwg.tspan(line, x=[x], dy=[0 if i == 0 else size * 1.25]))
    dwg.add(t)


def project_pair(roads, rail):
    roads_p = ox.projection.project_gdf(roads)
    return roads_p, rail.to_crs(roads_p.crs)


def select_route45(roads):
    return roads[
        roads.apply(
            lambda r: text_has(r.get("name"), CFG["route45_name_keywords"])
            or text_has(r.get("ref"), CFG["route45_ref_keywords"]),
            axis=1,
        )
    ].copy()


def select_connector(roads):
    return roads[
        roads.apply(
            lambda r: text_has(r.get("name"), CFG["surface_connector_keywords"]), axis=1
        )
    ].copy()


def under_mask(gdf):
    return gdf.apply(
        lambda r: truthy(r.get("tunnel"))
        or truthy(r.get("covered"))
        or layer_num(r.get("layer")) < 0,
        axis=1,
    )


def surface_mask(gdf):
    return gdf.apply(
        lambda r: not truthy(r.get("tunnel"))
        and not truthy(r.get("covered"))
        and layer_num(r.get("layer")) >= 0,
        axis=1,
    )


def make_xy(bounds, x, y, w, h, pad=35):
    minx, miny, maxx, maxy = bounds
    sx = max(maxx - minx, 1.0)
    sy = max(maxy - miny, 1.0)
    scale = min((w - 2 * pad) / sx, (h - 2 * pad) / sy)
    used_w, used_h = sx * scale, sy * scale
    ox0 = x + (w - used_w) / 2

    def xy(px, py):
        return (
            ox0 + (px - minx) * scale,
            y + h - ((h - used_h) / 2 + (py - miny) * scale),
        )

    return xy


def crop(gdf, polygon):
    if gdf is None or gdf.empty:
        return gdf
    out = gdf[gdf.geometry.intersects(polygon)].copy()
    out["geometry"] = out.geometry.intersection(polygon)
    return only_lines(out)


def centroid_point(gdf):
    return unary_union(list(gdf.geometry)).centroid


def crossing_focus(underpass, rail) -> Point:
    """Center the local view on the actual XY crossing of the grade-separated layers."""
    under_geom = unary_union(list(underpass.geometry))
    rail_geom = unary_union(list(rail.geometry))
    crossing = under_geom.intersection(rail_geom)
    if not crossing.is_empty:
        return crossing.centroid
    a, b = nearest_points(under_geom, rail_geom)
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2)


def add_legend(dwg, x, y):
    items = [
        (C["surface"], None, "地上道路（OSM layer 0相当）"),
        (C["under"], "18,12", "県道45号の線路下区間（tunnel=yes / layer=-1）"),
        (C["rail"], None, "相鉄線（layer=1）"),
        (C["connector"], None, "三ツ境下草柳線（OSM上 highway=construction）"),
    ]
    dwg.add(dwg.rect(insert=(x, y), size=(690, 158), rx=16, ry=16, fill=C["panel"], stroke=C["border"], stroke_width=2))
    for i, (color, dash, label) in enumerate(items):
        yy = y + 29 + i * 31
        attrs = dict(stroke=color, stroke_width=8, stroke_linecap="round")
        if dash:
            attrs["stroke_dasharray"] = dash
        dwg.add(dwg.line(start=(x + 22, yy), end=(x + 98, yy), **attrs))
        add_text(dwg, x + 118, yy + 7, label, size=19, weight=500)


def render_local(roads, rail, route45, underpass, connector, focus_poly):
    roads_f = crop(roads, focus_poly)
    rail_f = crop(rail, focus_poly)
    route_f = crop(route45, focus_poly)
    under_f = crop(underpass, focus_poly)
    conn_f = crop(connector, focus_poly)

    bounds = focus_poly.bounds
    xy = make_xy(bounds, 70, 150, 1460, 700, pad=20)
    dwg = svgwrite.Drawing(str(OUT / "03-local-focus.svg"), size=(W, H), viewBox=f"0 0 {W} {H}")
    dwg.add(dwg.rect(insert=(0, 0), size=(W, H), fill=C["bg"]))
    add_text(dwg, 70, 58, "交差点周辺だけに拡大：現況の上下関係", size=36, weight=700)
    add_text(dwg, 70, 105, "県道45号のアンダーパスと相鉄線が平面上で交わる点を中心に、約250m圏だけを表示", size=21, weight=500, fill=C["muted"])

    g = dwg.g(id="local-focus")
    draw_gdf(dwg, g, roads_f, xy, C["surface_minor"], 5, opacity=0.9)
    draw_gdf(dwg, g, route_f, xy, C["route45"], 13, opacity=0.96)
    draw_gdf(dwg, g, under_f, xy, C["under"], 20, dash="18,12")
    draw_gdf(dwg, g, conn_f, xy, C["connector"], 16)
    draw_gdf(dwg, g, rail_f, xy, C["rail_halo"], 19)
    draw_gdf(dwg, g, rail_f, xy, C["rail"], 9)
    dwg.add(g)

    if not under_f.empty:
        p = centroid_point(under_f)
        px, py = xy(p.x, p.y)
        add_text(dwg, px + 26, py + 62, "県道45号\n線路下", size=24, fill=C["under"])
    if not rail_f.empty:
        p = centroid_point(rail_f)
        px, py = xy(p.x, p.y)
        add_text(dwg, px - 20, py - 32, "相鉄線（上）", size=23, fill=C["rail"], anchor="end")
    if not conn_f.empty:
        p = centroid_point(conn_f)
        px, py = xy(p.x, p.y)
        add_text(dwg, px + 20, py - 25, "三ツ境下草柳線\n（工事中）", size=23, fill=C["connector"])

    add_legend(dwg, 70, 805)
    add_text(dwg, W - 70, H - 32, "© OpenStreetMap contributors (ODbL)", size=18, weight=500, fill=C["muted"], anchor="end")
    dwg.save()
    cairosvg.svg2png(url=str(OUT / "03-local-focus.svg"), write_to=str(OUT / "03-local-focus.png"), output_width=W)


def panel(dwg, x, title, subtitle, bounds, roads, rail, route45, underpass, connector, mode):
    y, pw, ph = 165, 350, 650
    dwg.add(dwg.rect(insert=(x, y), size=(pw, ph), rx=18, ry=18, fill=C["panel"], stroke=C["border"], stroke_width=2))
    add_text(dwg, x + 18, y + 42, title, size=25, weight=700)
    add_text(dwg, x + 18, y + 72, subtitle, size=19, weight=500, fill=C["muted"])
    xy = make_xy(bounds, x + 12, y + 92, pw - 24, ph - 115, pad=8)
    g = dwg.g()
    if mode == "surface":
        surf = roads[surface_mask(roads)].copy()
        draw_gdf(dwg, g, surf, xy, C["surface"], 7, opacity=0.9)
        draw_gdf(dwg, g, connector, xy, C["connector"], 15)
    elif mode == "under":
        draw_gdf(dwg, g, route45, xy, C["route45"], 8, opacity=0.22)
        draw_gdf(dwg, g, underpass, xy, C["under"], 19, dash="18,12")
    elif mode == "rail":
        draw_gdf(dwg, g, rail, xy, C["rail"], 11)
    else:
        surf = roads[surface_mask(roads)].copy()
        draw_gdf(dwg, g, surf, xy, C["surface_minor"], 5, opacity=0.85)
        draw_gdf(dwg, g, route45, xy, C["route45"], 10, opacity=0.9)
        draw_gdf(dwg, g, underpass, xy, C["under"], 17, dash="18,12")
        draw_gdf(dwg, g, connector, xy, C["connector"], 13)
        draw_gdf(dwg, g, rail, xy, C["rail_halo"], 16)
        draw_gdf(dwg, g, rail, xy, C["rail"], 8)
    dwg.add(g)


def render_exploded(roads, rail, route45, underpass, connector, focus_poly):
    roads_f = crop(roads, focus_poly)
    rail_f = crop(rail, focus_poly)
    route_f = crop(route45, focus_poly)
    under_f = crop(underpass, focus_poly)
    conn_f = crop(connector, focus_poly)
    bounds = focus_poly.bounds

    dwg = svgwrite.Drawing(str(OUT / "04-layer-exploded.svg"), size=(W, H), viewBox=f"0 0 {W} {H}")
    dwg.add(dwg.rect(insert=(0, 0), size=(W, H), fill=C["bg"]))
    add_text(dwg, 70, 58, "同じ場所を4枚に分解すると、どれが上下か分かる", size=36, weight=700)
    add_text(dwg, 70, 105, "各パネルは同じ縮尺・同じ向き。最後だけ全レイヤーを重ねています。", size=21, weight=500, fill=C["muted"])

    xs = [55, 430, 805, 1180]
    panel(dwg, xs[0], "① 地上", "側道・三ツ境下草柳線", bounds, roads_f, rail_f, route_f, under_f, conn_f, "surface")
    panel(dwg, xs[1], "② 下", "県道45号アンダーパス", bounds, roads_f, rail_f, route_f, under_f, conn_f, "under")
    panel(dwg, xs[2], "③ 上", "相鉄線", bounds, roads_f, rail_f, route_f, under_f, conn_f, "rail")
    panel(dwg, xs[3], "④ 重ねる", "①＋②＋③", bounds, roads_f, rail_f, route_f, under_f, conn_f, "combined")

    add_text(dwg, 70, 875, "OSMで確認できるタグ：県道45号 tunnel=yes / layer=-1、相模鉄道本線 layer=1、三ツ境下草柳線 highway=construction", size=20, weight=600)
    add_text(dwg, 70, 914, "この段階では横浜市の完成計画や信号位置はまだ追加していません。現況の立体関係だけを検証しています。", size=19, weight=500, fill=C["muted"])
    add_text(dwg, W - 70, H - 32, "© OpenStreetMap contributors (ODbL)", size=18, weight=500, fill=C["muted"], anchor="end")
    dwg.save()
    cairosvg.svg2png(url=str(OUT / "04-layer-exploded.svg"), write_to=str(OUT / "04-layer-exploded.png"), output_width=W)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ox.settings.use_cache = True
    ox.settings.log_console = True

    center = ox.geocode(CFG["center_query"])
    roads = only_lines(ox.features_from_point(center, tags={"highway": True}, dist=CFG["distance_m"]))
    rail = only_lines(ox.features_from_point(center, tags={"railway": CFG["railway_types"]}, dist=CFG["distance_m"]))
    roads_p, rail_p = project_pair(roads, rail)

    route45 = select_route45(roads_p)
    connector = select_connector(roads_p)
    underpass = route45[under_mask(route45)].copy()
    if underpass.empty:
        raise RuntimeError("Route 45 underpass was not found from OSM tunnel/layer tags")

    focus_center = crossing_focus(underpass, rail_p)
    focus_poly = focus_center.buffer(250)

    render_local(roads_p, rail_p, route45, underpass, connector, focus_poly)
    render_exploded(roads_p, rail_p, route45, underpass, connector, focus_poly)

    print(json.dumps({
        "focus_center_projected": [focus_center.x, focus_center.y],
        "focus_radius_m": 250,
        "outputs": [
            "docs/generated/03-local-focus.svg",
            "docs/generated/03-local-focus.png",
            "docs/generated/04-layer-exploded.svg",
            "docs/generated/04-layer-exploded.png",
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
