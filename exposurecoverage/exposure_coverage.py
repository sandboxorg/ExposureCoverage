#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

******************************************************
Exposure Coverage
******************************************************

"""
# Import standard Python packages
import copy
import json
import sys
import warnings
from os import listdir
from urllib2 import urlopen

import pandas as pd

warnings.filterwarnings('ignore')

__author__ = 'Shashank Kapadia'
__copyright__ = '2015 AIR Worldwide, Inc.. All rights reserved'
__version__ = '1.0'
__interpreter__ = 'Anaconda - Python 2.7.10 64 bit'
__maintainer__ = 'Shashank kapadia'
__email__ = 'skapadia@air-worldwide.com'
__status__ = 'Complete'


# noinspection PyBroadException,PyUnresolvedReferences,PyTypeChecker
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
        self.data = ''

    def summarize_file(self, file_path, file_type, data=None):

        if data is None:
            data = pd.DataFrame(pd.read_csv(file_path, sep=',', header=0))
        self.data = copy.deepcopy(data)
        self._getlatlong()

        summary_data = {'FileName': str(file_path.split('\\')[-1])}

        if file_type == 'location':
            columns = self.columns_location + self.columns_common
            self._get_inception_expiration()
            summary_data['InceptionExpirationDate'] = self.data['InceptionExpirationDate'].unique()
            summary_data['TimeElementValue'] = self._get_time_element_value()
            summary_data['MultiScenario'] = self._get_multiscenario()

        elif file_type == 'contract':
            columns = self.columns_contract + self.columns_common
        else:
            sys.exit()

        for clmn in columns:
            if clmn[1] == 'unique':
                summary_data['Unique' + clmn[0]] = self._getunique(clmn[0])
            elif clmn[1] == 'sum':
                summary_data['Sum' + clmn[0]] = self._getsum(clmn[0])

        if file_type == 'location':
            try:
                return summary_data, self.data[['Latitude', 'Longitude']]
            except:
                return summary_data, pd.DataFrame(columns=['Latitude', 'Longitude'])
        elif file_type == 'contract':
            return summary_data

    def run_coverage_dir(self):

        masterdata = [pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]

        for each_file in self.files:
            print(each_file)
            data = pd.DataFrame(pd.read_csv(each_file, sep=',', header=0))
            if ('ContractID' and 'LocationID') in data.columns:

                summary_data, latlong = self.summarize_file(file_path=each_file, data=data, file_type='location')
                summary_data = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in summary_data.iteritems()]))
                masterdata[0] = pd.concat([masterdata[0], summary_data], axis=0)
                masterdata[2] = pd.concat([masterdata[2], latlong], axis=0)

            elif 'ContractID' in data.columns:

                summary_data = self.summarize_file(file_path=each_file, data=data, file_type='contract')
                summary_data = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in summary_data.iteritems()]))
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
            return len(self.data[column_name].unique())
        except:
            return ''

    def _getsum(self, column_name):

        try:
            return self.data[column_name].sum()
        except:
            return ''

    def _get_time_element_value(self):
        try:
            return ((self.data['TimeElementValue'] / self.data['DaysCovered']) * 365.0).sum()
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


def getplace(lat, lon):
    url = "http://maps.googleapis.com/maps/api/geocode/json?"
    url += "latlng=%s,%s&sensor=false" % (lat, lon)
    v = urlopen(url).read()
    j = json.loads(v)
    print(j)
    components = j['results'][0]['address_components']
    print(components)
    country = town = None
    for c in components:
        if "country" in c['types']:
            country = c['long_name']
        if "postal_town" in c['types']:
            town = c['long_name']
    return town, country
