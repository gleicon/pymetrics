import pymetrics
import unittest
class TestCounter(unittest.TestCase):
    def setUp(self):
        self.rf = pymetrics.RetricsFactory("metrics_test")                                   
    def test_counter(self):
        counter = self.rf.new_counter("a_counter") 
        counter.reset() 
        for a in xrange(10):
            counter.incr()
        self.assertEqual(counter.get_value(), 10)

if __name__ == '__main__':
    unittest.main()
