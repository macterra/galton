import unittest
import galton
import random
import math

class TestMonteCarlo(unittest.TestCase):

    def setUp(self):
        pass
        
    def assertCloseEnough(self, a, b):
        x = abs(math.log10(a/b))
        self.assert_(x < 0.01)
        
    def test_median(self):
        for i in range(10):
            x = random.randint(1,100)
            results = galton.RunMonteCarlo(10000, [galton.Task(x, 'p50', 'medium')])
            p50 = results['cumprob'][50][0]
            print i, "p50=", x, p50
            self.assertCloseEnough(x, p50)
        
if __name__ == '__main__':
    unittest.main()