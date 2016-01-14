#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

******************************************************
Exposure Coverage
******************************************************

"""
# Import standard Python packages
import warnings
from os import listdir

import pandas as pd
import copy

warnings.filterwarnings('ignore')

__author__ = 'Shashank Kapadia'
__copyright__ = '2015 AIR Worldwide, Inc.. All rights reserved'
__version__ = '1.0'
__interpreter__ = 'Anaconda - Python 2.7.10 64 bit'
__maintainer__ = 'Shashank kapadia'
__email__ = 'skapadia@air-worldwide.com'
__status__ = 'Complete'

class ExposureCoverage:

    columns_location = [('LocationID', 'unique'), ('LocationGroups', 'unique'),
                        ('InceptionExpirationDate', 'unique'), ('CountryISO', 'unique'), ('LatLong', 'unique'),
                        ('BuildingValue', 'sum'), ('OtherValue', 'sum'), ('ContentsValue', 'sum'),
                        ('RiskCount', 'unique'), ('Premium', 'unique'),
                        ('ConstructionCodeType', 'unique'), ('OccupancyCode', 'unique'),
                        ('LocPerils', 'unique'), ('LocLimitType', 'unique'), ('LimitBldg', 'sum'),
                        ('LimitOther', 'sum'), ('LimitContent', 'sum'), ('LimitTime', 'sum'),
                        ('Participation1', 'unique'), ('Participation2', 'unique'), ('DeductType', 'unique'),
                        ('DeductBldg', 'sum'), ('DeductOther', 'sum'), ('DeductContent', 'sum'),
                        ('DeductTime', 'sum'), ('SubLimitArea', 'unique')]
    columns_contract = [('Status', 'unique'), ('Perils', 'unique'), ('LOB', 'unique'), ('LayerPerils', 'unique'),
                        ('LimitType', 'unique'), ('Limit1', 'sum'), ('LimitA', 'sum'), ('LimitB', 'sum'),
                        ('LimitC', 'sum'), ('LimitD', 'sum'), ('Limit2', 'sum'), ('DedAmt1', 'sum'),
                        ('DedAmt2', 'sum'), ('AttachmentAmt', 'sum'), ('DedType', 'unique'),
                        ('SublimitPerils', 'unique'), ('SublimitArea', 'unique'), ('SubLimitLimitType', 'unique'),
                        ('SublimitDedType', 'unique'), ('SubLimitOcc', 'sum'), ('SublimitPart', 'sum'),
                        ('SublimitLimitA', 'sum'), ('SublimitLimitB', 'sum'), ('SublimitLimitC', 'sum'),
                        ('SublimitLimitD', 'sum'), ('SublimiAttachA', 'sum'), ('SublimiAttachB', 'sum'),
                        ('SublimiAttachC', 'sum'), ('SublimiAttachD', 'sum'), ('SublimitDedAmt1', 'sum'),
                        ('SublimitDedAmt2', 'sum')]
    columns_common = [('ContractID', 'unique'), ('Currency', 'unique')]

    def __init__(self, dir_path):

        self.path = dir_path
        self.files = [str(self.path + '\\' + filename)
                      for filename in listdir(self.path) if filename.endswith('.csv')]

    def summarize_file(self, file, type, data=None):

        if data is None:
            data = pd.DataFrame(pd.read_csv(file, sep=',', header=0))
        self.data = copy.deepcopy(data)
        self._getlatlong()

        summary_data = {}

        summary_data['FileName'] = str(file.split('\\')[-1])
        if type == 'location':
            columns = self.columns_location + self.columns_common
            self._get_inception_expiration()
            summary_data['InceptionExpirationDate'] = self.data['InceptionExpirationDate'].unique()
            summary_data['TimeElementValue'] = self._get_time_element_value()
            summary_data['MultiScenario'] = self._get_multiscenario()

        elif type == 'contract':
            columns = self.columns_contract + self.columns_common

        for clmn in columns:
            if clmn[1] == 'unique':
                summary_data[clmn[0]] = self._getunique(clmn[0])
            elif clmn[1] == 'sum':
                summary_data[clmn[0]] = self._getsum(clmn[0])
        if type == 'location':
            return summary_data, self.data[['Latitude', 'Longitude']]
        elif type == 'contract':
            return summary_data

    def run_coverage_dir(self):

        masterdata = [pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]

        for file in self.files:
            print(file)
            data = pd.DataFrame(pd.read_csv(file, sep=',', header=0))
            if ('ContractID' and 'LocationID') in data.columns:

                summary_data, latlong = self.summarize_file(file=file, data=data, type='location')
                try:
                    summary_data = pd.DataFrame.from_dict(summary_data)
                except:
                    summary_data = pd.DataFrame.from_dict(summary_data, orient='index').transpose()
                masterdata[0] = pd.concat([masterdata[0], summary_data], axis=0)
                masterdata[2] = pd.concat([masterdata[2], latlong], axis=0)

            elif ('ContractID') in data.columns:
                summary_data = self.summarize_file(file=file, data=data, type='contract')
                try:
                    summary_data = pd.DataFrame.from_dict(summary_data)
                except:
                    summary_data = pd.DataFrame.from_dict(summary_data, orient='index').transpose()
                masterdata[1] = pd.concat([masterdata[1], summary_data], axis=0)


        return masterdata

    def _getlatlong(self):

        try:
            self.data['LatLong'] = zip(self.data.Latitude, self.data.Longitude)
        except:
            self.data['LatLong'] = ''

    def _get_inception_expiration(self):

        try:
            self.data['InceptionExpirationDate'] = (zip(self.data.InceptionDate, self.data.ExpirationDate))
        except:
            self.data['InceptionExpirationDate'] = 'Incorrect Column headers'

    def _getunique(self, column_name):

        try:
            return self.data[column_name].unique()
        except:
            return ''

    def _getsum(self, column_name):

        try:
            return self.data[column_name].sum()
        except:
            return ''

    def _get_time_element_value(self):
        try:
            return ((self.data['TimeElementValue'] /
                                                 self.data['DaysCovered']) * 365.0).sum()
        except:
            return ''

    def _get_multiscenario(self):

        try:
            if self.data.iloc[:, 126:(126 + 70)].dropna().empty:
                return 'NO'
            else:
                return 'YES'
        except:
            return 'NO'