# Official plan notes

This note records current confirmed facts and explicitly separates them from the next-stage reconstruction work.

## Current status of the reconstruction

The investigation is being reset around the process documented in [investigation-plan.md](investigation-plan.md).

Important distinction:

- the **grade-separated relationship** around Route 45 / Nakahara Kaido, the surface roads and Sotetsu railway is supported by public geospatial evidence;
- the exact **future surface-plan geometry** of the No.1 intersection must still be tied to Yokohama road-ledger / planning geometry before it is treated as reconstructed.

`docs/generated/06-official-2026-schematic.*` is therefore a provisional explanatory sketch, not an accepted reconstruction.

## No.1 intersection — official statements

Yokohama construction material states that the intersection shape is being changed to connect the existing road from the Mitsukyo-station side with the newly constructed road and that new pedestrian crossings/signals are being provided.

Primary source landing page:

- https://www.city.yokohama.lg.jp/kurashi/machizukuri-kankyo/toshiseibi/jokyo/kukakuseiri/endouchiku/ikkichiku/5.html

August 2026 construction briefing:

- https://www.city.yokohama.lg.jp/kurashi/machizukuri-kankyo/toshiseibi/jokyo/kukakuseiri/endouchiku/ikkichiku/5.files/0039_20260807.pdf

The August 2026 completion illustration is useful for identifying planned features such as intersection modification, channelisation/traffic-island treatment, crossings and signals. It must not be treated as survey-grade linework until it has been checked/georeferenced against the current legal project plan and road-ledger base.

## Grade separation

The project reconstruction must preserve the existing vertical separation. OpenStreetMap has provided useful corroboration (`tunnel=yes / layer=-1` for the relevant Route 45 underpass geometry and `layer=1` for railway geometry), but OSM is no longer the primary base for the detailed plan reconstruction.

For detailed existing geometry, use the Yokohama road-ledger / R-Mappy sources registered in [../sources/source-register.md](../sources/source-register.md).

## 2018 signal-pattern study

Yokohama's first-phase newsletter No.7 (2018-05-18) published a study concept for No.1 intersection in which the movement groups were described as:

1. Mitsukyo-Shimokusayanagi through / left-turn movement
2. Mitsukyo-Shimokusayanagi right-turn movement (two directions)
3. Nakahara Kaido side-road west movement
4. Nakahara Kaido side-road east movement
5. pedestrian movement

Direct source:

- https://www.city.yokohama.lg.jp/kurashi/machizukuri-kankyo/toshiseibi/jokyo/kukakuseiri/endouchiku/ikkichiku/news.files/0008_20190313.pdf

The source states that the concept may change through later coordination / actual operation. Therefore it remains **historical signal-study evidence** only and must not be presented as the confirmed 2026 final indication sequence or timing.

## 2017 side-road discussion

First-phase newsletter No.6 explicitly discusses `中原街道の側道` and the relationship between closely spaced intersections / school-route handling around No.1 intersection.

Direct source:

- https://www.city.yokohama.lg.jp/kurashi/machizukuri-kankyo/toshiseibi/jokyo/kukakuseiri/endouchiku/ikkichiku/news.files/0007_20190313.pdf

This is important historical evidence for identifying the surface side-road concept, but the physical segment mapping still has to be matched to the current road-ledger geometry.

## Source / visualization rules

- `Observed`: directly supported existing condition.
- `Official plan`: directly stated or drawn in an official project source.
- `Derived`: transformed/georeferenced/simplified from registered sources.
- `Interpretation`: consistent engineering interpretation, but not explicitly stated by the source.
- `Unknown`: evidence insufficient.

Do not publish exact final signal-head locations, lane assignments, timing, phase sequence, turning permissions or survey-grade geometry unless a current official source supports them.
