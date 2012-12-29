import sys, os

sys.path.append("..") 
sys.path.append(os.path.join(sys.path[0], '..'))

import pymetrics
import time, random

rf = pymetrics.RetricsFactory("metrics_test")

def test_meter(meters):
    last_t = time.time()
    c = j = 0
    while(j < 10):
        c = c +1
        if c == random.random() % 10:
            c = 0
            time.sleep(random.random() % 0.01)
        else:
            time.sleep(random.random() % 0.1)
        meters.mark()
        last_t, one_min, five_min, fifteen_min = meters.get_value() 
        print "\nlast_t: %f" % last_t
        print "avg 1 min: %s" % one_min
        print "avg 5 min: %s" % five_min
        print "avg 15 min: %s" % fifteen_min
        j = j + 1

print 'Counter test'
counter = rf.new_counter("a_counter")
counter.reset()
for a in xrange(10):
    counter.incr()
assert(counter.get_value() == 10)
print counter.get_value()

print 'Gauge test'
gauge = rf.new_gauge("a_gauge")
gauge.set(10)
assert(gauge.get() == 10)
print gauge.get()

print 'Timer test'
timer = rf.new_timer("a_timer")
timer.start()
time.sleep(5)
timer.stop()
print timer.get_value()
assert(timer.get_value() == 5)

print 'Histogram test'
histogram = rf.new_histogram("a_histogram")
histogram.update(10)
histogram.update(1)
histogram.update(50)
histogram.update(5)
histogram.update(28)
histogram.update(12)

print histogram.percentile(99.0)
print histogram.mean()
print histogram.median()
print histogram.standard_deviation()

print 'Meter test'
meters = rf.new_meter("a_meter")
test_meter(meters)

print 'Listing instances per metric for timer'
print rf.list_instances_per_metric('timer')

print 'Listing instances per metric for histogram'
print rf.list_instances_per_metric('histogram')

print 'Listing instances per metric for histogram'
print rf.list_instances_per_metric('histogram')

print 'Unregistering all metrics (clears up all data)'
rf.unregister_instance(counter)
rf.unregister_instance(gauge)
rf.unregister_instance(timer)
rf.unregister_instance(meters)
rf.unregister_instance(histogram)

print 'Listing instances per metric for histogram'
print rf.list_instances_per_metric('histogram')


