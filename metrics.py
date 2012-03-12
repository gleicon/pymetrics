#encoding: utf-8
import redis
import time

class BaseMetrics(object):
    def __init__(self, appname, name):
        self._name = name
        self._appname = appname
        p = redis.ConnectionPool(host='localhost', port=6379, db=0)
        self._redis = redis.Redis(connection_pool = p)

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
    
    def get_value(self):
        return int(self._redis.get("retrics:counter:%s:%s" % (self._appname,
            self._name)))

class RetricsMeter(BaseMetrics):
    """
    A meter measures the rate of events over time (e.g., “requests per
    second”). In addition to the mean rate, meters also track 1-, 5-, and
    15-minute moving averages.
    """
    def __init__(self, appname, name):
        super(RetricsMeter, self).__init__(appname, name)
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

class RetricsHistogram(BaseMetrics):
    """
    A histogram measures the statistical distribution of values in a stream
    of data. In addition to minimum, maximum, mean, etc., it also measures
    median, 75th, 90th, 95th, 98th, 99th, and 99.9th percentiles.
    """
    def update():
        pass

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

class RetricsFactory():
    """
    Retrics - Redis based metrics library
    Inspired by coda hale's Metrics

    Create a metrics factory for your application
    rf = RetricsFactory()
    
    Instrument your code:
    c = rf.new_counter("requests")
    c.incr()
    c.decr()
    """
    def __init__(self, appname = None):
        self._appname = appname

    def new_gauge(self, name):
        return RetricsGauge(self._appname, name)

    def new_counter(self, name):
        return RetricsCounter(self._appname, name)

    def new_meter(self, name):
        return RetricsMeter(self._appname, name)

    def new_histogram(self, name):
        return RetricsHistogram(self._appname, name)

    def new_timer(self, name):
        return RetricsTimer(self._appname, name)

    def new_healthcheck(self, name):
        pass

