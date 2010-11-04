from numpy import *
from numpy.random import lognormal
from random import *
import time

Sigma1 = 0.27043285     
RiskMap = { 'none' : 0.001, 'low' : Sigma1, 'medium' : 2*Sigma1, 'high' : 3*Sigma1, 'very high' : 4*Sigma1 }
BaseFactors = { 50 : 1, 60 : 1.07091495269662, 70 : 1.15236358602526, 80 : 1.25558553883723, 90 : 1.41421363539235 }
RiskExponent = { 'none' : 0, 'low' : 1, 'medium' : 2, 'high' : 3, 'very high' : 4 }

class Task:
    def __init__(self, estimate, type, risk):
        self.estimate = estimate
        self.type = type
        self.sigma = RiskMap[risk]            
        
        if type == 'mode':
            self.p50 = estimate * math.exp(self.sigma*self.sigma)
        elif type == 'mean':
            self.p50 = estimate / math.exp(self.sigma*self.sigma/2)
        elif type == 'p50':
            self.p50 = estimate
        elif type == 'p60': 
            self.p50 = self.CalcMedian(estimate, 60, risk) 
        elif type == 'p70': 
            self.p50 = self.CalcMedian(estimate, 70, risk) 
        elif type == 'p80': 
            self.p50 = self.CalcMedian(estimate, 80, risk)   
        elif type == 'p90':    
            self.p50 = self.CalcMedian(estimate, 90, risk)
        else:
            raise 'unknown estimate type'
            
    def CalcMedian(self, estimate, confidence, risk):
        return estimate/(BaseFactors[confidence] ** RiskExponent[risk])        
        
    def Time(self): 
        return self.p50 * lognormal(0,self.sigma)
     
def RunMonteCarlo(trials, tasks):
    t = time.time()
    times = ([])
    n = 0
    
    if trials > 100000:
        print "RunMonteCarlo: too many trials", trials
        trials = 10000
        
    if trials < 1:
        trials = 10000
        
    for x in xrange(trials):
        total = 0
        for task in tasks:
            total += task.Time()
        times = append(times,total)
    elapsed = time.time() - t
    times = sort(times)
    N = len(times)
    cumprob = [[times[t*N/100], t] for t in range(100)]
    sigma = log(times).std()
    mode = times[N/2] * exp(-sigma*sigma)

    nominal = sum([t.estimate for t in tasks])
    pnom = 0.0
    for x in xrange(trials):
        if times[x] > nominal:
            pnom = 1. - (1. * x/trials)
            break

    results = dict(simtime=elapsed, trials=trials, cumprob=cumprob, mean=times.mean(), mode=mode, std=times.std(), risk=sigma, nominal=nominal, pnom=pnom);
    return results
