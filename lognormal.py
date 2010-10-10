from random import *
from numpy import *
import math, csv

class Task:
    def __init__(self, mode, sigma):
        self.mode = mode
        self.sigma = sigma
        self.p50 = mode * math.exp(sigma*sigma)

    def Time(self): 
        return self.p50 * lognormvariate(0,self.sigma)

def ReadTaskFile(filename):
    infile = csv.reader(open(filename))

    tasks = []
    risks = { 'none':0, 'low':0.25, 'medium':0.5, 'high':0.75 }

    for row in infile:
        est, risk = row
        tasks.append(Task(float(est),risks[risk]))
    return tasks

def Analyze(arr, printStats=False, histo=False, top=0, N=50):
    foo = sort(arr)
    bar = log(arr)
    count = len(arr)
    
    avg = bar.mean()
    stdev = bar.std()
    medn = math.exp(avg)
    mode = math.exp(avg-stdev*stdev)
    mean = math.exp(avg+stdev*stdev/2)
    
    n = len(foo)
    p10 = foo[n*1/10]
    p50 = foo[n*5/10]
    p90 = foo[n*9/10]

    if printStats:
        print "mode,   ", mode
        print "median, ", medn
        print "mean,   ", mean
        print "sigma,  ", stdev
    
        print "p10,    ", p10
        print "p50,    ", p50
        print "p90,    ", p90
    
        print "mean,   ", foo.mean()
        print "sigma,  ", foo.std()
    
    results = dict(tmode=mode, tmedian=medn, tmean=mean, tsigma=stdev)
    results.update(dict(p10=p10, p50=p50, p90=p90))
    results.update(dict(mean=foo.mean(), sigma=foo.std()))
    
    results['percentile'] = [foo[n*x/100] for x in range(100)]
    
    if histo:
        maxval = max(arr)
        magnitude = math.pow(10.0,math.floor(math.log10(maxval)))
        if top == 0:
            top = magnitude*math.ceil(maxval/magnitude)
        totals,bins = histogram(arr,bins=N,range=(0.0,top))
        cum = 0
        cumprob = [()]
        for i in range(N):
            cum += totals[i]
            prob = 100.0*cum/count
            cumprob.append(prob)
            print "%8.1f, %8d, %8d, %8.2f" % (bins[i], totals[i], cum, 100.0*cum/count)
        #results['histogram'] = zip(bins,totals)
        #results['cumprob'] = zip(bins,cumprob)
        
    return results

