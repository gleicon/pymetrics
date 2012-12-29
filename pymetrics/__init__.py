#encoding: utf-8
import redis
import time, os
from pds_redis import Enum

class BaseMetrics(object):
    def __init__(self, appname, name, redis = None, timeout = None):
        
        self._appname = appname
        self._timeout = timeout

        _klass = self.__class__.__name__.lower()
        self._instances_per_metric_index = "retrics:index:%s:%s" % (appname,
                _klass)

        self._name= "%s:%d" % (name, os.getpid())
         
        if redis is None:
            p = redis.ConnectionPool(host='localhost', port=6379, db=0)
            self._redis = redis.Redis(connection_pool = p)
        else:
            self._redis = redis

        self._redis.zadd(self._instances_per_metric_index, self._name, 1.0)
        
    def remove(self):
        self.clear()
        self._redis.zrem(self._instances_per_metric_index, self._name)

    def clear(self):
        pass

class RetricsGauge(BaseMetrics):
    """
    A gauge is an instantaneous measurement of a value. For example, we may
    want to measure the number of pending jobs in a queue
    """
    def set(self, value):
        self._redis.set("retrics:gauge:%s:%s" % (self._appname, self._name),
                value)
    
    def get(self):
        return int(self._redis.get("retrics:gauge:%s:%s" % (self._appname,
            self._name)))
    
    def clear(self):
        self._redis.delete("retrics:gauge:%s:%s" % (self._appname,
            self._name))

class RetricsCounter(BaseMetrics):
    """
    A counter is just a gauge for an AtomicLong instance. You can increment
    or decrement its value. For example, we may want a more efficient way of
    measuring the pending job in a queue
    """
    def incr(self, val = 1):
        self._redis.incr("retrics:counter:%s:%s" % (self._appname, self._name), val)
    
    def decr(self, val = 1):
        self._redis.decr("retrics:counter:%s:%s" % (self._appname, self._name), val)
    
    def reset(self):
        self._redis.set("retrics:counter:%s:%s" % (self._appname, self._name), 0)
    
    def clear(self):
        self._redis.delete("retrics:counter:%s:%s" % (self._appname, self._name))
    
    def get_value(self):
        r = self._redis.get("retrics:counter:%s:%s" % (self._appname,
            self._name))
        if r is None:
            return 0
        else:
            return int(r)

class RetricsMeter(BaseMetrics):
    """
    A meter measures the rate of events over time (e.g., “requests per
    second”). In addition to the mean rate, meters also track 1-, 5-, and
    15-minute moving averages.
    """
    def __init__(self, appname, name, redis, timeout):
        super(RetricsMeter, self).__init__(appname, name, redis, timeout)
        self._last_t = time.time()
        self.reset()

    def _ns(self, key):
        """
        takes care of namespace
        """
        return "retrics:meter:%s:%s:%s"% (self._appname, self._name, key)

    def start(self):
        self._last_t = time.time()

    def reset(self):
        self._last_t = time.time()
        zeroes = [0 for x in xrange(60)]
        self._redis.lpush(self._ns('seconds'), *zeroes)
        self._redis.lpush(self._ns('l5min'), *zeroes[0:4])
        self._redis.lpush(self._ns('l15min'), *zeroes[0:14])
        self._redis.set(self._ns('curr_second'), 0)
        self._redis.set(self._ns('1minute'), 0)
        self._redis.set(self._ns('5minute'), 0)
        self._redis.set(self._ns('15minute'), 0)

    def _update(self, ts):
        if int(self._last_t) == int(ts):
            self._redis.incr(self._ns('curr_second'))
        else:
            self._last_t = ts

            v = int(self._redis.get(self._ns('curr_second')))
            self._redis.set(self._ns('curr_second'), 1)

            self._redis.lpush(self._ns('seconds'), v)
            self._redis.ltrim(self._ns('seconds'), 0, 60)
            l = self._redis.lrange(self._ns('seconds'), 0, 60)
            one_min = reduce(lambda x,y: int(x) + int(y), l)/60

            self._redis.set(self._ns('1minute'), one_min)
            self._redis.lpush(self._ns('l5min'), one_min)
            self._redis.lpush(self._ns('l15min'), one_min)
            self._redis.ltrim(self._ns('l5min'), 0, 5)
            self._redis.ltrim(self._ns('l15min'), 0, 15)

            l5 = self._redis.lrange(self._ns('l5min'), 0, 60)
            l15 = self._redis.lrange(self._ns('l15min'), 0, 60)

            five_min = reduce(lambda x,y: int(x) + int(y), l5)/5
            self._redis.set(self._ns('5minute'), five_min)

            fifteen_min = reduce(lambda x,y: int(x) + int(y), l15)/15
            self._redis.set(self._ns('15minute'), fifteen_min)

    def get_value(self):
        one = self._redis.get(self._ns('1minute'))
        five = self._redis.get(self._ns('5minute'))
        fifteen = self._redis.get(self._ns('15minute'))
        return [self._last_t, one, five, fifteen]

    def mark(self):
        self._update(time.time())
    
    def clear(self):
        self._redis.delete(self._ns("1minute"))
        self._redis.delete(self._ns("5minute"))
        self._redis.delete(self._ns("15minute"))
        self._redis.delete(self._ns("seconds"))
        self._redis.delete(self._ns("curr_second"))
        self._redis.delete(self._ns("l1min"))
        self._redis.delete(self._ns("l5min"))
        self._redis.delete(self._ns("l15min"))

class RetricsHistogram(BaseMetrics):
    """
    A histogram measures the statistical distribution of values in a stream
    of data. In addition to minimum, maximum, mean, etc., it also measures
    median, 75th, 90th, 95th, 98th, 99th, and 99.9th percentiles.
    """
    def __init__(self, appname, name, redis, timeout):
        super(RetricsHistogram, self).__init__(appname, name, redis, timeout)
        self._list_name = "retrics:histogram:%s:%s" % (self._appname, self._name)
        self._e = Enum(self._load_list())

    def update(self, val):
        assert(type(val) is int or type(val) is float)
        self._redis.lpush(self._list_name, val)
        self._e.reload(self._load_list())

    def percentile(self, p):
        """
        Percentile of the Histogram list
        """
        assert(type(p) is float)
        return self._e.percentile(p)
    
    def standard_deviation(self):
        """
        standard deviation of the Histogram list
        """
        return self._e.standard_deviation()

    def median(self):
        """
        Median (50% Percentile) of the Histogram list
        """
        return self._e.median()
    
    def mean(self):
        """
        Mean of the Histogram list
        """
        return self._e.mean()

    def _load_list(self):
        l =  self._redis.lrange(self._list_name, 0, -1)
        l = map(lambda x: float(x), l) #oh god why
        return l
   
    def reset(self):
        self._redis.delete(self._list_name)
        self._e = Enum(self._load_list())

    def clear(self):
        self._redis.delete(self._list_name)
        self._e = Enum([])

class RetricsTimer(BaseMetrics):
    """
    A timer measures both the rate that a particular piece of code is called and
    the distribution of its duration.
    """
    def start(self):
        self._redis.set("retrics:timer:%s:%s:start" % (self._appname,
            self._name), int(time.time()))

    def stop(self):
        self._redis.set("retrics:timer:%s:%s:stop" % (self._appname,
            self._name), int(time.time()))

    def get_value(self):
        p = "retrics:timer:%s:%s" % (self._appname, self._name)
        start, stop = self._redis.mget(["%s:start" % p, "%s:stop" % p])
        return int(stop) - int(start)

    def reset(self):
        p = "retrics:timer:%s:%s" % (self._appname, self._name)
        self._redis.mset({"%s:start" % p: 0, "stop:%s" % p: 0})

    def clear(self):
        p = "retrics:timer:%s:%s" % (self._appname, self._name)
        self._redis.delete("%s:start" % p, "%s:stop" % p)

class RetricsFactory():
    """
    Retrics - Redis based metrics library
    Inspired by coda hale's Metrics

    Create a metrics factory for your application
    rf = RetricsFactory("my_application")
    
    Optionally you can pass a global timeout in seconds to keep the database
    clean. No writes to a given metrics ensure its data will be cleaned up

    rf = RetricsFactory("my_application", 3600)


    Instrument your code:
        c = rf.new_counter("requests")
        c.incr()
        c.decr()

    Unregister and clean up all data with:
        rf.unregister(c)

    Check the number of instances per metric (if any)

    print rf.list_instances_per_metric('gauge')
    
    """
    def __init__(self, appname = None, timeout = None):
       
        self._appname = appname
        self._timeout = timeout
        p = redis.ConnectionPool(host='localhost', port=6379, db=0)
        self._redis = redis.Redis(connection_pool = p)
    
    def _metric_name(self, metric_name):
        _klass = "retrics%s" % metric_name.lower()
        return "retrics:index:%s:%s" % (self._appname,_klass)

    def list_instances_per_metric(self, metric_name):
        _klass = "retrics%s" % metric_name.lower()
        _instances_per_metric_index = "retrics:index:%s:%s" % (self._appname,
                _klass.lower())
        return self._redis.zrange(_instances_per_metric_index, 0, -1)
    
    def unregister_instance(self, kl):
        """
            Expect the metric object itself to clean everything up.
        """
        kl.remove()
        self._clear_instance(kl.__class__.__name__.lower(), kl._name)

    def _clear_instance(self, metric_name, instance_name):
        _instances_per_metric_index = "retrics:index:%s:%s" % (self._appname, metric_name)
        self._redis.zrem(_instances_per_metric_index, instance_name)

    def new_gauge(self, name):
        return RetricsGauge(self._appname, name, self._redis, self._timeout)

    def new_counter(self, name):
        return RetricsCounter(self._appname, name, self._redis, self._timeout)

    def new_meter(self, name):
        return RetricsMeter(self._appname, name, self._redis, self._timeout)

    def new_histogram(self, name):
        return RetricsHistogram(self._appname, name, self._redis, self._timeout)

    def new_timer(self, name):
        return RetricsTimer(self._appname, name, self._redis, self._timeout)

    def new_healthcheck(self, name):
        pass

