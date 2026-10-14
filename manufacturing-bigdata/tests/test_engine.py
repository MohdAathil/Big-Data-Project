import unittest
from manufacturing.engine import moving_average,event_adjustment,requirement,build_schedule,MACHINES,PRODUCTS
class EngineTests(unittest.TestCase):
 def test_moving_average(self): self.assertAlmostEqual(moving_average([1,2,3],2),2.5)
 def test_requirement_accounts_for_safety_stock(self): self.assertEqual(requirement(100,{'current_stock':70,'reserved_quantity':0,'incoming_quantity':0,'safety_stock':20}),50)
 def test_event_adjustment_bounded_and_deterministic(self): self.assertAlmostEqual(event_adjustment({'demand_direction':'positive','severity':'high','relevance_score':.9,'confidence':.8}),.0576); self.assertEqual(event_adjustment({'demand_direction':'neutral'}),0)
 def test_failure_machine_never_scheduled(self):
  req=[{'product_id':'P001','quantity':100}]; jobs=build_schedule(req,failures=['M001','M002','M004']); self.assertTrue(all(j['machine_id']!='M001' and j['machine_id']!='M002' and j['machine_id']!='M004' for j in jobs))
 def test_only_compatible_machine_scheduled(self):
  jobs=build_schedule([{'product_id':'P003','quantity':30}]); self.assertTrue(all(j['product_id'] in next(m for m in MACHINES if m['machine_id']==j['machine_id'])['supported_products'] for j in jobs))
if __name__=='__main__': unittest.main()
