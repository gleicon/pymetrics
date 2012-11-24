import pymetrics
import unittest
import time

class TestTimer(unittest.TestCase):
    def setUp(self):
        self.rf = pymetrics.RetricsFactory("metrics_test")                                   
    def test_timer(self):
        timer = self.rf.new_timer("a_timer") 
        timer.start() 
        time.sleep(5)
        timer.stop()
        self.assertEqual(timer.get_value(), 5)

if __name__ == '__main__':
    unittest.main()
