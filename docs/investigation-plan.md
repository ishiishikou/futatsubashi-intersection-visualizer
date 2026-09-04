# Investigation plan: reconstruct the Futatsubashi No.1 intersection like a road engineer

## Purpose

Reconstruct the current and planned road structure around the No.1 intersection in the Futatsubashi / Mitsukyo area without guessing missing geometry from schematic illustrations.

The goal is not to draw a plausible-looking completion image. The goal is to establish a traceable evidence chain from official/current geometry to the planned surface intersection, then add traffic movements and signal-control interpretation only after the geometry is stable.

## Core principle

Work in the same order a road/intersection engineer would use:

1. establish the existing condition,
2. separate plan geometry from elevation/grade separation,
3. identify each road and its function,
4. georeference the official plan onto the existing condition,
5. trace only geometry that the official plan supports,
6. examine each approach and movement separately,
7. add signal control last,
8. iterate when geometry, control, or traffic movements conflict.

Do not infer final geometry from an explanatory illustration alone.

## Evidence hierarchy

When sources disagree, prefer them in this order unless a newer official document explicitly supersedes an older one.

1. **Yokohama road ledger / R-Mappy at approximately 1:500**
   - primary base for existing road edges, road boundaries and urban-planning decision lines.
2. **Current Yokohama project plan / latest project-plan revision**
   - primary source for the legal/project geometry of the planned roads.
3. **Current construction briefing material**
   - primary source for current construction state, intersection modification, traffic island, crossings and signal-installation intent.
4. **Earlier Yokohama project documents and newsletters**
   - used to understand design evolution, constraints and earlier signal studies.
5. **Yokohama i-Mappy / urban-planning data**
   - used to verify the urban-planning road corridor and decision lines.
6. **GSI maps / aerial photographs**
   - independent visual check of physical context and historical changes.
7. **OpenStreetMap**
   - corroborative geometry/topology source, especially useful for `tunnel`, `bridge`, `layer`, `construction` and network connectivity.
8. **Other public maps or user-provided screenshots**
   - visual orientation only; not committed, not traced and not used as the authoritative geometry source.

## Information classes

Every geometry or statement in generated outputs must be assigned one of these classes.

- **Observed** — directly supported by current road-ledger, official map or public geospatial data.
- **Official plan** — directly shown or stated in a Yokohama/authority planning or construction document.
- **Derived** — mechanically transformed from official/observed information, such as georeferenced or simplified linework.
- **Interpretation** — engineering interpretation that is consistent with evidence but not explicitly stated in a source.
- **Unknown** — not established; must remain unfilled rather than guessed.

A final explanatory SVG must not visually merge these categories without a legend or provenance note.

## Phase 0 — Source control

Before changing geometry:

- update `sources/source-register.md`;
- record source title, authority, date, URL, purpose and status;
- do not commit third-party PDF pages or Google Maps screenshots;
- record which source supports every new geometry layer;
- prefer stable landing pages when a direct PDF URL is likely to change.

**Gate 0:** no geometry work starts until the relevant authoritative sources are registered.

## Phase 1 — Establish the existing-condition base map

### 1.1 Road-ledger base

Use Yokohama road-ledger information as the primary base.

Capture or derive, without re-hosting restricted source imagery:

- road edges;
- road boundaries;
- service/side roads;
- underpass approaches;
- junction points;
- public reference/control points where available;
- road names / recognized routes where the source supports them.

### 1.2 Urban-planning decision lines

Use R-Mappy / i-Mappy to identify:

- Mitsukyo-Shimokusayanagi Line urban-planning decision line;
- the existing and planned corridor;
- relevant city-planning facility boundaries;
- any relationship to the first-phase land-readjustment boundary.

### 1.3 Independent checks

Compare the road-ledger geometry against:

- GSI map/aerial photography;
- OpenStreetMap;
- current construction status shown by Yokohama.

Differences must be logged rather than silently reconciled.

**Gate 1:** produce one clean existing-condition plan at one coordinate system/scale. No completion geometry yet.

## Phase 2 — Build the grade-separation model

Treat plan position and elevation as separate dimensions.

Assign every relevant segment an explicit level/state, for example:

- `L+1`: railway / elevated structure where supported;
- `L0`: surface intersection, side roads and Mitsukyo-Shimokusayanagi surface road;
- `L-1`: Route 45 / Nakahara Kaido underpass where supported.

Create:

1. a plan view;
2. a simplified longitudinal/section view;
3. an exploded-level view.

Do not use a line crossing in 2D as evidence of a junction.

**Gate 2:** every apparent crossing must be classified as same-level junction, grade-separated crossing, or unknown.

## Phase 3 — Give each road segment a stable ID and function

Create a road inventory before analysing traffic.

Example IDs (final names should follow the evidence):

- `R45-MAIN-*` — Nakahara Kaido / Prefectural Route 45 underpass mainline segments;
- `R45-SIDE-W-*` — west-side surface/service-road segments;
- `R45-SIDE-E-*` — east-side surface/service-road segments;
- `MSS-EXIST-*` — existing Mitsukyo-Shimokusayanagi road from Mitsukyo-station side;
- `MSS-NEW-*` — new/planned Mitsukyo-Shimokusayanagi segment;
- `LOCAL-*` — local streets;
- `RAIL-*` — Sotetsu railway geometry.

For each segment record:

- source;
- level;
- current/planned status;
- functional role;
- known directionality;
- confidence;
- unresolved questions.

**Gate 3:** no movement arrows or signal phases until the road inventory is complete.

## Phase 4 — Georeference the official future plan

Do not redraw the Yokohama completion image by eye.

### 4.1 Choose control points

Use multiple common features that are visible in both the existing-condition base and official plan, such as:

- fixed road intersections;
- road-boundary corners;
- underpass portals/approaches;
- railway alignment;
- existing road bends;
- durable structures or parcel/road-boundary features when clearly identifiable.

Avoid using a temporary construction object as a control point.

### 4.2 Transform and residual-check

Perform a 2D similarity/affine/projective transform as appropriate.

Record:

- control points;
- transform type;
- residual error per control point;
- total RMS error;
- rejected control points and reason.

The explanatory completion image may not be survey-accurate; if residuals are too large, use it only for topology/feature existence and use the legal project plan for geometry.

### 4.3 Trace with provenance

Trace separately:

- planned road center/edge geometry where justified;
- traffic island/canalisation;
- crosswalks;
- signal-control zone;
- any explicitly shown connecting road.

Each traced layer must carry a source/provenance ID.

**Gate 4:** no traffic interpretation until planned geometry aligns acceptably with the existing-condition base.

## Phase 5 — Reconstruct traffic movements one approach at a time

For every approach, make a separate movement sheet.

For each incoming direction answer:

1. where does the vehicle physically enter the surface intersection?
2. which outgoing segments are physically connected?
3. which movements are explicitly allowed/prohibited by the available plan?
4. which movements are unknown?
5. does the movement cross another vehicle or pedestrian path?
6. is the movement at `L0`, or is it actually separated at `L-1`/`L+1`?

Do not draw all arrows at once initially.

Suggested order:

1. Mitsukyo-station side approach;
2. new Mitsukyo-Shimokusayanagi approach;
3. Nakahara Kaido west-side surface approach;
4. Nakahara Kaido east-side surface approach;
5. local-road approaches;
6. pedestrian crossings.

**Gate 5:** each arrow must map to real, same-level connected road segments.

## Phase 6 — Add signal-control interpretation

Only after geometry and movements are stable:

- register the 2018 five-phase study as historical evidence;
- compare it with the final/planned 2026 physical geometry;
- identify which movement groups still make geometric sense;
- do not assume the 2018 sequence or timing is the final 2026 operation;
- do not invent exact signal-head positions or cycle timings without an official source.

Use National Police Agency signal-installation guidance and Kanagawa Police traffic-control procedures only as **methodology/context**, not as evidence of this intersection's final phasing.

**Gate 6:** label the result as either confirmed control, historical study, or unresolved control logic.

## Phase 7 — Engineering sanity checks

Check the reconstructed intersection against engineering concepts:

- road classification and design speed;
- design vehicle / turning feasibility;
- lane and shoulder/side-road roles;
- turning radii and channelisation;
- sight distance;
- longitudinal grade near the surface intersection;
- pedestrian crossing placement;
- conflict points;
- queue/storage space;
- compatibility between geometric design and traffic control.

These checks detect interpretation errors; they do not replace official design evidence.

## Phase 8 — QA and publication

### Required figures

Generate these separately:

1. `existing-plan` — existing road geometry only;
2. `existing-levels` — surface / underpass / railway exploded view;
3. `road-inventory` — labelled segment IDs;
4. `official-plan-georeference` — control points and transformed plan geometry;
5. `future-plan` — planned surface geometry only;
6. `movement-approach-*` — one sheet per approach;
7. `signal-study-2018` — historical study only;
8. `final-explanation` — only after all gates pass.

### Automated checks

Where possible, GitHub Actions should verify:

- generated SVG/PNG presence;
- no missing source IDs for traced layers;
- no same-level movement arrow that jumps between disconnected geometries;
- no accidental crossing-to-junction conversion across different levels;
- legible typography;
- source register links/identifiers present;
- outputs clearly mark `Observed`, `Official plan`, `Derived`, `Interpretation`, `Unknown`.

### Human/model review checklist

Before accepting a diagram:

- Can every drawn road be pointed to in an authoritative source?
- Can every vertical level be justified?
- Can every future line be traced back to the current project plan?
- Can every traffic arrow be followed continuously on the surface geometry?
- Are historical signal studies visibly separated from final-plan facts?
- Have we stopped rather than guessed wherever evidence is insufficient?

## Public-repository rules

This repository is public.

Do not commit:

- Google Maps screenshots or traced Google Maps geometry;
- user-provided map screenshots;
- personal information;
- credentials, cookies or API tokens;
- Yokohama PDF screenshots/pages as permanent source files;
- temporary inspection artifacts from source PDFs.

Prefer links, metadata, derived geometry with provenance, and outputs that comply with the applicable source terms.

## Definition of done

The investigation is complete only when:

1. existing geometry is based on Yokohama road-ledger/urban-planning data and independently checked;
2. grade-separated crossings are explicitly modelled;
3. the current project plan has been georeferenced or otherwise tied to the base geometry with documented control points;
4. planned surface geometry is traced with provenance;
5. each approach movement has been checked separately;
6. signal information is separated into confirmed facts vs historical study vs unknowns;
7. the final explanatory figure can be reconstructed from registered sources without relying on undocumented visual intuition.
