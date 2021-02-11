import pytest

import app.stats_helpers as sh


class TestStatsHelpers:

    def test_calc_hits(self):
        """
        Tests that calculation of hits is correct
        """

        assert sh.calcHits(1, 2, 3, 4) == 10
        assert sh.calcHits(0, 0, 0, 0) == 0


    def test_calc_at_bats(self):
        """
        Tests that calculation of at bats is correct
        """
        
        assert sh.calcAtBats(1, 2, 3) == 6
        assert sh.calcAtBats(0, 0, 0) == 0

    
    def test_calc_obp(self):
        """
        Tests that calculation of on base percentage is correct
        """

        assert sh.calcOBP(5, 10, 2, 1) == 0.615
        assert sh.calcOBP(5, 20, 1, 1) == 0.318
        assert sh.calcOBP(0, 0, 0, 0) == 'Undefined'


    def test_calc_avg(self):
        """
        Tests that calculation of batting average is correct
        """

        assert sh.calcAVG(5, 10) == 0.5
        assert sh.calcAVG(3, 9) == 0.333
        assert sh.calcAVG(0, 0) == 'Undefined'


    def test_calc_slg(self):
        """
        Tests that calculation of slugging percentage is correct
        """
        
        assert sh.calcSLG(1, 2, 3, 4, 10) == 3
        assert sh.calcSLG(1, 2, 3, 4, 0) == 'Undefined'
        assert sh.calcSLG(1, 1, 1, 1, 4) == 2.5


    def test_calc_ops(self):
        """
        Tests that calculation of OPS is correct
        """
        
        assert sh.calcOPS(0.5, 3) == 3.5
        assert sh.calcOPS('Undefined', 3) == 'Undefined'
        assert sh.calcOPS(3, 'Undefined') == 'Undefined'
        assert sh.calcOPS(0, 0) == 'Undefined'


    def test_calc_era(self):
        """
        Tests that calculation of earned run average is correct
        """
        
        assert sh.calcERA(4, 6) == 2
        assert sh.calcERA(0, 0) == 'Undefined'
        assert sh.calcERA(3, 3) == 3


    def test_calc_ip(self):
        """
        Tests that calculation of innings pitched is correct
        """
        
        assert sh.calcInningsPitched(9) == 3
        assert sh.calcInningsPitched(0) == 0
        assert sh.calcInningsPitched(34) == 11.33
