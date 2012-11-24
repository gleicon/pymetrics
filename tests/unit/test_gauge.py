import unittest
class TestGauge(unittest.TestCase):
    def setUp(self):
        self.rf = pymetrics.RetricsFactory("metrics_test")                                   
    def test_counter(self):
        gauge = self.rf.new_counter("a_gauge") 
        gauge.set(10)
        self.assertEqual(gauge.get, 10)

if __name__ == '__main__':
    unittest.main()
