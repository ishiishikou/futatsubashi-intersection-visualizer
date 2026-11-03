"""Integrity checks are separate from reconstruction acceptance."""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    def reject(value):
        raise ValueError(f'non-finite JSON: {value}')
    return json.loads(Path(path).read_text(), parse_constant=reject)

def validate(evidence, state, osm):
    errors = []
    sources = {s['id']: s for s in evidence['sources']}
    if len(sources) != len(evidence['sources']):
        errors.append('duplicate source ID')
    for claim in evidence['claims']:
        if claim['classification'] not in {'Observed','Official plan','Derived','Interpretation','Unknown'}:
            errors.append('unknown classification')
        if not claim['limits'] or not claim['references']:
            errors.append('claim lacks limits or references')
        for ref in claim['references']:
            if ref['source'] not in sources or not ref['locator']:
                errors.append('unregistered reference')
    gates = state['gates']
    if [g['id'] for g in gates] != list(range(9)):
        errors.append('gate sequence incomplete')
    for i,g in enumerate(gates):
        if g['status'] not in {'passed','blocked','not_run'}:
            errors.append('invalid gate status')
        if g['status'] == 'passed':
            if not g['evidence']:
                errors.append('passed gate lacks evidence')
            if any(p['status'] != 'passed' for p in gates[:i]):
                errors.append('passed gate skips predecessor')
    complete = all(g['status'] == 'passed' for g in gates)
    if state['reconstruction_complete'] != complete:
        errors.append('completion flag disagrees with gates')
    geo = state['georeference']
    if gates[4]['status'] == 'passed':
        if len(geo['control_points']) < 3 or not geo['independent_check_points'] or not geo['transform']:
            errors.append('georeference lacks measured controls or independent checks')
        for key in ['rms_m','maximum_residual_m','acceptance_threshold_m']:
            v=geo[key]
            if not isinstance(v,(int,float)) or not math.isfinite(v) or v < 0:
                errors.append('georeference lacks measured residual/threshold')
    elif geo['rms_m'] is not None or geo['transform'] is not None:
        errors.append('unaccepted transform presented as measured result')
    for fig in state['figures']:
        if fig['geometry'] and any(g['status'] != 'passed' for g in gates[:fig.get('required_gate', 8)+1]):
            errors.append('geometry publication blocked by gates')
    node_ids = {n['id'] for n in osm['nodes']}
    for w in osm['ways']:
        if not set(w['nodes']) <= node_ids:
            errors.append('OSM way has missing node')
        if any(k in w for k in ['user','uid','changeset']):
            errors.append('OSM contributor account metadata')
    return errors

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--require-complete',action='store_true');ap.add_argument('--check-generated',action='store_true');args=ap.parse_args()
    evidence=read(ROOT/'data/evidence.json');state=read(ROOT/'data/gates.json');osm=read(ROOT/'data/osm-corroboration.json')
    errors=validate(evidence,state,osm)
    if args.check_generated:
        import xml.etree.ElementTree as ET
        for f in state['figures']:
            p=ROOT/'docs/generated'/f"{f['id']}.svg"
            if not p.exists():errors.append(f'missing {p.name}');continue
            root=ET.parse(p).getroot()
            if root.get('data-status') != f['status']:errors.append('SVG status mismatch')
            if not f['geometry'] and any(e.tag.rsplit('}',1)[-1] in {'path','line','polyline','polygon','image'} for e in root.iter()):
                errors.append('unexpected geometry in audit notice')
    if errors:
        print('\n'.join(errors));return 1
    print('Integrity: PASS; reconstruction: '+('COMPLETE' if state['reconstruction_complete'] else 'BLOCKED at Gate 1'))
    return 2 if args.require_complete and not state['reconstruction_complete'] else 0

if __name__=='__main__':raise SystemExit(main())
