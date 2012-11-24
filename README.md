# PyMetrics

    Redis backed metrics library - implements the most of the famous Metrics library.

# Classes

    RetricsGauge(BaseMetrics) - Single value gauge
    RetricsCounter(BaseMetrics) - Simple counter with incr and decr methods
    RetricsMeter(BaseMetrics) - Time series data, with 1, 5 and 15 minutes avg
    RetricsHistogram(BaseMetrics) - Histogram with percentile, mean, median and std deviation methods 
    RetricsTimer(BaseMetrics) - Timer (wallclock)
    RetricsFactory - Metrics factory 


# Examples:
     
    from pymetrics import RetricsFactory
    
    rf = RetricsFactory('application_name')                                                       
    c = rf.new_counter('requests')                                              
    c.incr()                                                                    
    c.decr()
    

    For more examples, check the tests/ directory    
    Use python -m unittest discover tests/unit to run all tests
   

# TODO
    Should use riemann optionally

