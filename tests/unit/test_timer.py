import sys, os                                                                                                                                                                  
sys.path.append(os.path.join(sys.path[0], '../..'))

import pymetrics
import unittest
import time

class TestTimer(unittest.TestCase):
    def setUp(self):
        self.rf = pymetrics.RetricsFactory("metrics_test")                                   
        self.timer = self.rf.new_timer("a_timer") 

    def test_timer(self):
        self.timer.start() 
        time.sleep(5)
        self.timer.stop()
        self.assertEqual(self.timer.get_value(), 5)

    def tearDown(self):
        self.rf.unregister_instance(self.timer)

if __name__ == '__main__':
    unittest.main()
