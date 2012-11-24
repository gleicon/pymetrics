# derived from https://github.com/gleicon/py_descriptive_statistics

import math

class Enum(object):
    def __init__(self, l=[]):
        self.l = l
    
    def mean(self):
        return self.sum()/self.number()

    def median(self):
        return self.percentile(50.0)

    def number(self):
        return float(len(self.l))

    def percentile(self, p):
        s = sorted(self.l)
        p = float(p)
        if p == 100.0: return float(s[-1])
        rank = p / 100.0 * (self.number() - 1) 
        lrank = int(math.floor(rank))
        d = rank - lrank
        lower = float(s[lrank])
        upper = float(s[lrank + 1])
        r = lower + (upper - lower) * d
        return r

    def standard_deviation(self):
        return math.sqrt(self.variance())

    def sum(self):
        return sum(self.l)

    def variance(self):
        m = self.mean()
        p1 = map(lambda x: (m - x) ** 2 , self.l)
        r = sum(p1) / self.number()
        return r

    def reload(self, l):
        self.l = l
