import sys, os                                                                                                                                                                  
sys.path.append(os.path.join(sys.path[0], '../..'))

import pymetrics
import unittest
class TestGauge(unittest.TestCase):
    def setUp(self):
        self.rf = pymetrics.RetricsFactory("metrics_test")                                   
        self.gauge = self.rf.new_gauge("a_gauge") 

    def test_counter(self):
        self.gauge.set(10)
        self.assertEqual(self.gauge.get(), 10)

    def tearDown(self):
        self.rf.unregister_instance(self.gauge)

if __name__ == '__main__':
    unittest.main()
