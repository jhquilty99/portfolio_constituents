import pytest
import etf_constituents

class TestClass:
    portfolio_1 = {'VTI':1}
    portfolio_2 = {'VTI':1, 'EDV':1}
    portfolio_3 = {'VTI':10, 'EDV':5}
    #def test_get_title(self):
    #    assert etf_constituents.get_title()

    def test_weight_to_float(self):
        assert etf_constituents.weight_to_float(None) == 0
        assert etf_constituents.weight_to_float('NaN') == 0
        assert etf_constituents.weight_to_float(1.0) == 1.0
        assert etf_constituents.weight_to_float(1) == 1
        assert etf_constituents.weight_to_float(2.09) == 2.09
        assert type(etf_constituents.weight_to_float(None)) == float
        assert type(etf_constituents.weight_to_float('NaN')) == float
        assert type(etf_constituents.weight_to_float(1.0)) == float
        assert type(etf_constituents.weight_to_float(1)) == float
        assert type(etf_constituents.weight_to_float(2.09)) == float

    #def test_scrape_security_data(self):
    #    assert 

    #def test_get_prop_of_each_etf(self):
    #    assert 

    #def test_get_constituent_weights(self):
    #    assert 
