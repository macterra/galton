import unittest
import galton
import random
import math

class TestMonteCarlo(unittest.TestCase):

    def setUp(self):
        self.risks = galton.RiskMap.keys()
        
    def assertCloseEnough(self, a, b):
        x = abs(math.log10(a/b))
        #print a, b, x
        self.assert_(x < 0.02, "x = %d" % (x))
                
    def simTest(self, type, getResult):
        for i in range(10):
            x = random.random() * 100
            risk = random.choice(self.risks)
            results = galton.RunMonteCarlo(10000, [galton.Task(x, type, risk)])
            y = getResult(results)
            #print i, type, "=", x, y, risk
            self.assertCloseEnough(x, y)
            self.assertCloseEnough(results['risk'], galton.RiskMap[risk])
        
    def test_mode(self):
        self.simTest('mode', lambda res: res['mode'])
        
    def test_median(self):
        self.simTest('p50', lambda res: res['cumprob'][50][0])
        
    def test_p60(self):
        self.simTest('p60', lambda res: res['cumprob'][60][0])
        
    def test_p70(self):
        self.simTest('p70', lambda res: res['cumprob'][70][0])
        
    def test_p80(self):
        self.simTest('p80', lambda res: res['cumprob'][80][0])
        
    def test_p90(self):
        self.simTest('p90', lambda res: res['cumprob'][90][0])
               
    def test_mean1(self):
        self.simTest('mean', lambda res: res['mean'])
        
    def test_mean2(self):
        for i in range(10):
            estimates = [random.random() * 100 for t in range(20)]
            tasks = [galton.Task(e, 'mean', random.choice(self.risks)) for e in estimates]
            results = galton.RunMonteCarlo(10000, tasks)
            #print "meanTest", sum(estimates), results['mean']
            self.assertCloseEnough(sum(estimates), results['mean'])
            
if __name__ == '__main__':
    unittest.main()

