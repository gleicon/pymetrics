import metrics
import time, random

rf = metrics.RetricsFactory("metrics_test")

def test_meter(rf):
    meters = rf.new_meter("a_meter")
    last_t = time.time()
    c = 0
    while(True):
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

counter = rf.new_counter("a_counter")
counter.reset()
for a in xrange(10):
    counter.incr()
assert(counter.get_value() == 10)
print counter.get_value()

gauge = rf.new_gauge("a_gauge")
gauge.set(10)
assert(gauge.get() == 10)
print gauge.get()

timer = rf.new_timer("a_timer")
timer.start()
time.sleep(5)
timer.stop()
print timer.get_value()
assert(timer.get_value() == 5)

test_meter(rf)

