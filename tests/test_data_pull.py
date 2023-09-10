import pytest
import data_pull
import numpy as np
import re
import pandas as pd

class TestClass:
    portfolio_1 = {'VTI':1}
    portfolio_2 = {'VTI':1, 'EDV':1}
    portfolio_3 = {'VTI':10, 'EDV':5}

    def test_drop_trailing_period(self):
        assert data_pull.drop_trailing_period('Cisco.') == 'Cisco'
        assert data_pull.drop_trailing_period('.') == ''
        assert data_pull.drop_trailing_period('Cisco') == 'Cisco'
        assert data_pull.drop_trailing_period('cisco.') == 'cisco'
        assert data_pull.drop_trailing_period('Jd. inc.') == 'Jd. inc'

    def test_get_title(self):
        assert data_pull.get_title('<span class="truncated_text_single" title="Meta Platforms Inc">Meta Platforms ..</span>') == 'Meta Platforms Inc'
        assert data_pull.get_title('<span class="truncated_text_single" title="Cisco Systems Inc">Cisco Systems I..</span>') == 'Cisco Systems Inc'
        assert data_pull.get_title('<span class="truncated_text_single" title="Applied Materials Inc">Applied Materia..</span>') == 'Applied Materials Inc'
        assert data_pull.get_title('<span class="truncated_text_single" title="Walgreens Boots Alliance Inc">Walgreens Boots..</span>') == 'Walgreens Boots Alliance Inc'
        assert data_pull.get_title('Zscaler Inc') == 'Zscaler Inc'
        assert data_pull.get_title('JD.com Inc ADR') == 'JD.com Inc ADR'
        assert data_pull.get_title('Atlassian Corp') == 'Atlassian Corp'
        assert data_pull.get_title('Fastenal Co') == 'Fastenal Co'
        assert data_pull.get_title('<span class="truncated_text_single" title="GE HealthCare Technologies Inc">GE HealthCare T..</span>') == 'GE HealthCare Technologies Inc'
        assert data_pull.get_title('<span class="truncated_text_single" title="Cisco Systems Inc./Delaware">Cisco Systems I..</span>') == 'Cisco Systems Inc'
        assert data_pull.get_title('<span class="truncated_text_single" title="Seagate Technology Holdings plc">Seagate Technol..</span>') == 'Seagate Technology Holdings plc'
        assert data_pull.get_title('<span class="truncated_text_single" title="Ichor Holdings Ltd.">Ichor Holdings ..</span>') == 'Ichor Holdings Ltd'
        assert data_pull.get_title('8x8 Inc.') == '8x8 Inc'

    def test_weight_to_float(self):
        assert data_pull.weight_to_float(None) == 0
        assert data_pull.weight_to_float('NaN') == 0
        assert data_pull.weight_to_float('NA') == 0
        assert data_pull.weight_to_float(1.0) == 1.0
        assert data_pull.weight_to_float(1) == 1
        assert data_pull.weight_to_float(2.09) == 2.09
        assert type(data_pull.weight_to_float(None)) == float
        assert type(data_pull.weight_to_float('NaN')) == float
        assert type(data_pull.weight_to_float('NA')) == float
        assert type(data_pull.weight_to_float(1.0)) == float
        assert type(data_pull.weight_to_float(1)) == float
        assert type(data_pull.weight_to_float(2.09)) == float

    def test_get_security_data(self):
        qqq_data = data_pull.get_security_data('QQQ')
        vgt_data = data_pull.get_security_data('VGT')
        edv_data = data_pull.get_security_data('EDV')
        assert type(qqq_data) == str
        assert type(vgt_data) == str
        assert type(edv_data) == str
        assert 'QQQ' in qqq_data
        assert 'VGT' in vgt_data
        assert 'EDV' in edv_data
        assert len(qqq_data) >= 100000
        assert len(vgt_data) >= 100000
        assert len(edv_data) >= 50000

    def test_scrape_security_data(self):
        qqq_data = data_pull.scrape_security_data(['QQQ']) 
        assert qqq_data.shape[0] >= 100
        assert qqq_data.shape[1] == 3

    def test_get_current_prices(self):
        single_df = data_pull.get_current_prices(['VGT'])
        multi_df = data_pull.get_current_prices(['QQQ','VGT','EDV'])
        assert type(single_df) == pd.Series
        assert type(multi_df) == pd.Series
        assert single_df.shape[0] == 1
        assert multi_df.shape[0] == 3
        assert type(single_df[0]) == np.float64
        assert type(multi_df[0]) == np.float64
        assert list(single_df.index) == ['VGT']
        assert set(multi_df.index) == set(['QQQ','VGT','EDV'])
     

    def test_get_prop_value(self):
        price_a = pd.Series({'VTI':100})
        price_b = pd.Series({'VTI':100, 'EDV':50})
        price_c = pd.Series({'EDV':50, 'VTI':100})
        prop_1 = data_pull.get_prop_value(self.portfolio_1, price_a)
        prop_2 = data_pull.get_prop_value(self.portfolio_2, price_b)
        prop_3 = data_pull.get_prop_value(self.portfolio_3, price_b)
        prop_4 = data_pull.get_prop_value(self.portfolio_3, price_c)
        assert type(prop_1) == pd.Series
        assert type(prop_2) == pd.Series
        assert type(prop_3) == pd.Series
        assert type(prop_4) == pd.Series
        assert prop_1.shape[0] == 1
        assert prop_2.shape[0] == 2
        assert prop_3.shape[0] == 2
        assert prop_4.shape[0] == 2
        assert type(prop_1[0]) == np.float64
        assert type(prop_2[0]) == np.float64
        assert type(prop_3[0]) == np.float64
        assert type(prop_4[0]) == np.float64
        assert set(prop_1.index) == set(['VTI'])
        assert set(prop_2.index) == set(['VTI','EDV'])
        assert set(prop_3.index) == set(['VTI','EDV'])
        assert set(prop_4.index) == set(['VTI','EDV'])
        test_1 = pd.Series([1.0], index = ['VTI'])
        test_2 = pd.Series([0.666666666, 0.333333333], index = ['VTI','EDV'])
        test_3 = pd.Series([0.8, 0.2], index = ['VTI','EDV'])
        test_4 = pd.Series([0.2, 0.8], index = ['EDV','VTI'])
        pd.testing.assert_series_equal(prop_1, test_1)
        pd.testing.assert_series_equal(prop_2, test_2)
        pd.testing.assert_series_equal(prop_3, test_3)
        pd.testing.assert_series_equal(prop_4, test_4)

    #def test_get_prop_of_each_etf(self):
    #    assert 

    #def test_get_constituent_weights(self):
    #    assert 
