import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_evidence import ROOT,read,validate

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.e=read(ROOT/'data/evidence.json');self.g=read(ROOT/'data/gates.json');self.o=read(ROOT/'data/osm-corroboration.json')
    def test_recorded_partial_state_is_consistent(self):
        self.assertEqual(validate(self.e,self.g,self.o),[])
    def test_cannot_skip_blocked_gate(self):
        self.g['gates'][5].update(status='passed',evidence=['pretend'])
        self.assertIn('passed gate skips predecessor',validate(self.e,self.g,self.o))
    def test_cannot_publish_geometry_before_acceptance(self):
        self.g['figures'][0]['geometry']=True
        self.assertIn('geometry publication blocked by gates',validate(self.e,self.g,self.o))
    def test_cannot_use_zero_as_unmeasured_residual(self):
        self.g['georeference']['rms_m']=0
        self.assertTrue(validate(self.e,self.g,self.o))
    def test_claim_must_resolve_to_registered_source(self):
        self.e['claims'][0]['references'][0]['source']='missing'
        self.assertIn('unregistered reference',validate(self.e,self.g,self.o))
    def test_underpass_has_no_surface_or_rail_junction(self):
        ways={w['id']:w for w in self.o['ways']}
        for a in [124814741,124814742]:
            for b in [161192972,854966477,169791880,60051873,238305283]:
                self.assertFalse(set(ways[a]['nodes']) & set(ways[b]['nodes']))
    def test_design_study_schematic_is_not_reconstruction(self):
        figs={f['id']:f for f in self.g['figures']}
        for fid in ['design-levels-schematic','design-topology-schematic']:
            self.assertIn(fid,figs)
            self.assertTrue(figs[fid].get('schematic'))
            self.assertFalse(figs[fid]['geometry'])
            self.assertEqual(figs[fid]['status'],'design-study')
        self.assertEqual(validate(self.e,self.g,self.o),[])
        self.assertFalse(self.g['reconstruction_complete'])
    def test_schematic_must_carry_design_study_status(self):
        for f in self.g['figures']:
            if f.get('schematic'):
                f['status']='partial'
        self.assertIn('schematic figure must carry design-study status',validate(self.e,self.g,self.o))
    def test_pedestrian_tunnel_and_stairs_are_separate_connected_objects(self):
        ways={w['id']:w for w in self.o['ways']}
        for a,b in [(809626360,809626361),(809626361,809626362)]:
            self.assertTrue(set(ways[a]['nodes']) & set(ways[b]['nodes']))
        self.assertEqual(ways[809626362]['tags']['highway'],'steps')

if __name__=='__main__':unittest.main()
