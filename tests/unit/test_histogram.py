import sys, os                                                                                                                                                                  
sys.path.append(os.path.join(sys.path[0], '../..'))

import pymetrics
import unittest
import math

class TestHistogram(unittest.TestCase):
    def setUp(self):
        self.rf = pymetrics.RetricsFactory("metrics_test") 
        self.histogram = self.rf.new_histogram("a_histogram")
        self.histogram.update(10)
        self.histogram.update(1)
        self.histogram.update(50)
        self.histogram.update(5)
        self.histogram.update(28)
        self.histogram.update(12)

    def test_histogram_percentile(self):
        self.assertEqual(round(self.histogram.percentile(99.0), 2), 48.9)
    
    def test_histogram_mean(self):
        self.assertEqual(self.histogram.mean(), 17.666666666666668)
    
    def test_histogram_median(self):
        self.assertEqual(self.histogram.median(), 11.0)

    def test_histogram_std_dev(self):
        self.assertEqual(math.floor(self.histogram.standard_deviation()), 16.0)
    
    def tearDown(self):
        self.rf.unregister_instance(self.histogram)

if __name__ == '__main__':
    unittest.main()
