import unittest,copy,os
from unittest.mock import patch
from pathlib import Path
import export_math_instance as e
SOURCE = os.environ.get('TORCHLETTE_TEST_VF')
RAW = Path(SOURCE).read_bytes() if SOURCE else None
class Stop(Exception):pass
@unittest.skipUnless(SOURCE, 'Set TORCHLETTE_TEST_VF to a complete canonical source font')
class Guards(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.f=e.load(RAW)
 def test_positive_normalized_850(self):
  def stub(font,pins,**kw):
   loc=e.AxisLimits(pins).limitAxesAndPopulateDefaults(font).normalize(font)
   self.assertEqual(loc['wght'].default,.875)
   self.assertEqual(font['avar'].segments['ital'],self.f['avar'].segments['ital']);raise Stop
  with patch.object(e,'instantiateVariableFont',stub),self.assertRaises(Stop):e.aligned_instantiate(self.f,{'wght':850},self.f,{'wght':850,'ital':0})
 def test_range_pin_rejected(self):
  with self.assertRaises(ValueError):e.aligned_instantiate(self.f,{'wght':(800,850)},self.f,{'wght':850,'ital':0})
 def test_source_pin_mismatch(self):
  with self.assertRaises(ValueError):e.aligned_instantiate(self.f,{'wght':800},self.f,{'wght':850,'ital':0})
 def test_avar2_rejected(self):
  f=copy.deepcopy(self.f);f['avar'].majorVersion=2
  with self.assertRaises(ValueError):e.aligned_instantiate(f,{'wght':850},f,{'wght':850,'ital':0})
 def test_wrong_original_weight_map(self):
  f=copy.deepcopy(self.f);f['avar'].segments['wght'][.5]=.4
  with self.assertRaises(ValueError):e.aligned_instantiate(f,{'wght':850},f,{'wght':850,'ital':0})
 def test_changed_surviving_map(self):
  f=copy.deepcopy(self.f);f['avar'].segments['ital'][.25]=.125
  with self.assertRaises(ValueError):e.aligned_instantiate(f,{'wght':850},self.f,{'wght':850,'ital':0})
 def test_changed_range(self):
  f=copy.deepcopy(self.f);f['fvar'].axes[0].maxValue=950
  with self.assertRaises(ValueError):e.aligned_instantiate(f,{'wght':850},self.f,{'wght':850,'ital':0})
 def test_wrong_harfbuzz_rejected_before_export(self):
  with patch.object(e.hb, 'version_string', return_value='14.0.0'),self.assertRaises(ValueError):e.Exporter(RAW,e.digest(RAW))
 def test_source_hash_rejected(self):
  with self.assertRaises(ValueError):e.Exporter(RAW,'0'*64)
if __name__=='__main__':unittest.main()
