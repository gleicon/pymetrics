#PyMetrics

Redis backed metrics library - tries to implement the most of the famous Metrics library.

# Examples:

    import metrics
    import time

    rf = metrics.RetricsFactory("metrics_test")

    # incremental/decr counter counter
    counter = rf.new_counter("a_counter")
    counter.reset()
    for a in xrange(10):
        counter.incr()
    print counter.get_value() # must be 10

    # a gauge, which indicate an absolute value
    gauge = rf.new_gauge("a_gauge")
    gauge.set(10)
    print gauge.get()

    # a meter vith 1, 5 and 15 mins avg
    meters = rf.new_meter("a_meter")
    # ... do something ...
    meters.mark()
    # do other things, etc, better check metrics_test.py for a working example
    meters.get_value()

    # returns last timestamp, 1 min, 5 min, 15 min

    # a timer, which marks the begin and end of a task
    timer = rf.new_timer("a_timer")
    timer.start()
    time.sleep(5)
    timer.stop()
    print timer.get_value()

# TODO

Needs to receive a Redis conn string, let the meter have the automatic timestamp
Should use riemann optionally
Meters needs a mean value
Implement Histogram

