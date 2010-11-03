import unittest
import galton
import random
import math

class TestMonteCarlo(unittest.TestCase):

    def setUp(self):
        self.risks = ['none', 'low', 'medium', 'high', 'very high']
        self.types = ['mode', 'mean', 'p50', 'p60', 'p70', 'p80', 'p90']
        
    def assertCloseEnough(self, a, b):
        x = abs(math.log10(a/b))
        self.assert_(x < 0.02, "x = %d" % (x))
        
    def confidenceTest(self, type, confidence):
        for i in range(10):
            x = random.randint(1,100)
            risk = random.choice(self.risks)
            results = galton.RunMonteCarlo(10000, [galton.Task(x, type, risk)])
            p = results['cumprob'][confidence][0]
            #print i, type, "=", x, p, risk
            self.assertCloseEnough(x, p)
            self.assertCloseEnough(results['risk'], galton.RiskMap[risk])
            
    def test_p50(self):
        self.confidenceTest('p50', 50)
        
    def test_p60(self):
        self.confidenceTest('p60', 60)
        
    def test_p70(self):
        self.confidenceTest('p70', 70)
        
    def test_p80(self):
        self.confidenceTest('p80', 80)
        
    def test_p90(self):
        self.confidenceTest('p90', 90)
        
    def averageTest(self, type):
        for i in range(10):
            x = random.randint(1,100)
            risk = random.choice(self.risks)
            results = galton.RunMonteCarlo(10000, [galton.Task(x, type, risk)])
            avg = results[type]
            self.assertCloseEnough(x, avg)
            self.assertCloseEnough(results['risk'], galton.RiskMap[risk])
            
    def test_mean(self):
        self.averageTest('mean')
        
    def test_mode(self):
        self.averageTest('mode')
            
if __name__ == '__main__':
    unittest.main()

