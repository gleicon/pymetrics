# PyMetrics

    Redis backed metrics library - implements the most of the famous Metrics library.

# Classes

    RetricsGauge(BaseMetrics) - Single value gauge
    RetricsCounter(BaseMetrics) - Simple counter with incr and decr methods
    RetricsMeter(BaseMetrics) - Time series data, with 1, 5 and 15 minutes avg
    RetricsHistogram(BaseMetrics) - Histogram with percentile, mean, median and std deviation methods 
    RetricsTimer(BaseMetrics) - Timer (wallclock)

    The main class to loof after is RetricsFactory - Metrics factory 

# Hierarchy

    Basically we register an application and its metrics instances in the following order:
        Application -> Metrics -> Instances of metrics

    The important thing to monitor is that each metric will have an internal name based on the application + metric name + pid.
    By looking at the way the name is composed it's easy to interchange data between processes.

# Examples:
     
    from pymetrics import RetricsFactory
    
    rf = RetricsFactory('application_name')                                                       
    c = rf.new_counter('requests')                                              
    c.incr()                                                                    
    c.decr()
    
    To list all instances for a given metric:

    rf.list_instances_per_metric('gauge') 
    
    rf.unregister_instance(c)

    Unregister metrics instances is not mandatory as each new metric will not use the same internal name.

    For more examples, check the tests/ directory    
    Use python -m unittest discover tests/unit to run all tests
   

# TODO
    Should use riemann optionally
    Should integrate with dashify 
    Should be ported to ruby 
