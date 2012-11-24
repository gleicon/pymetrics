import unittest
class TestHistogram(unittest.TestCase):
    def setUp(self):
        self.rf = pymetrics.RetricsFactory("metrics_test") 
        self.histogram = re.new_histogram("a_histogram")
        self.histogram.update(10)
        self.histogram.update(1)
        self.histogram.update(50)
        self.histogram.update(5)
        self.histogram.update(28)
        self.histogram.update(12)

    def test_histogram_percentile(self):
        self.assertEqual(self.histogram.percentile(99.0), 50.0)
    
    def test_histogram_mean(self):
        self.assertEqual(self.histogram.mean(), 17.6666666667)
    
    def test_histogram_median(self):
        self.assertEqual(self.histogram.median(), 11.0)

    def test_histogram_std_dev(self):
        self.assertEqual(self.histogram.standard_deviation(), 16.7398393727)

if __name__ == '__main__':
    unittest.main()
