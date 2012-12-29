import sys, os                                                                                                                                                                  
sys.path.append(os.path.join(sys.path[0], '../..'))

import pymetrics
import unittest
class TestCounter(unittest.TestCase):
    def setUp(self):
        self.rf = pymetrics.RetricsFactory("metrics_test")                                   
        self.counter = self.rf.new_counter("a_counter") 

    def test_counter(self):
        self.counter.reset() 
        for a in xrange(10):
            self.counter.incr()
        self.assertEqual(self.counter.get_value(), 10)

    def tearDown(self):
        self.rf.unregister_instance(self.counter)

if __name__ == '__main__':
    unittest.main()
