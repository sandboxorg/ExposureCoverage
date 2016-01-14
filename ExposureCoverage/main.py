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

warnings.filterwarnings('ignore')


class ExposureCoverage:
    def __init__(self, dir_path):

        self.path = dir_path
        self.files = [str(self.path + '\\' + filename)
                      for filename in listdir(self.path) if filename.endswith('.csv')]

    def run(self):

        masterdata_loc = pd.DataFrame()
        masterdata_con = pd.DataFrame()
        latlong = pd.DataFrame()
        count_loc = 0
        count_con = 0
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

        for file in self.files:
            print(file)
            data = pd.DataFrame(pd.read_csv(file, sep=',', header=0))
            if ('ContractID' and 'LocationID') in data.columns:
                try:
                    data['LatLong'] = zip(data.Latitude, data.Longitude)
                except:
                    data['LatLong'] = zip(0.0, 0.0)
                try:
                    data['InceptionExpirationDate'] = (zip(data.InceptionDate, data.ExpirationDate))
                except:
                    data['InceptionExpirationDate'] = 'Incorrect Column headers'

                masterdata_loc.loc[count_loc, 'FileName'] = (file.split('\\')[-1])
                for column in columns_location + columns_common:
                    try:
                        if column[1] == 'unique':
                            masterdata_loc.loc[count_loc, column[0]] = data[column[0]].unique()
                        elif column[1] == 'sum':
                            masterdata_loc.loc[count_loc, column[0]] = data[column[0]].sum()
                    except:
                        masterdata_loc.loc[count_loc, column[0]] = ''
                try:
                    masterdata_loc.loc[count_loc, 'SumTimeElementValue'] = (
                        (data['TimeElementValue'] / data['DaysCovered']) * 365.0).sum()
                except:
                    masterdata_loc.loc[count_loc, 'SumTimeElementValue'] = ''
                try:
                    if data.iloc[:, 126:(126 + 70)].dropna().empty:
                        masterdata_loc.loc[count_loc, 'MultiTermScenario'] = 'NO'
                    else:
                        masterdata_loc.loc[count_loc, 'MultiTermScenario'] = 'YES'
                except:
                    masterdata_loc.loc[count_loc, 'MultiTermScenario'] = 'NO'
                count_loc += 1
                latlong = pd.concat([latlong, data[['Latitude', 'Longitude']]], axis=0)

            elif 'ContractID' in data.columns:

                masterdata_con.loc[count_con, 'FileName'] = (file.split('\\')[-1])
                for column in columns_contract + columns_common:
                    try:
                        if column[1] == 'unique':
                            masterdata_con.loc[count_con, column[0]] = data[column[0]].unique()
                        elif column[1] == 'sum':
                            masterdata_con.loc[count_con, column[0]] = data[column[0]].sum()
                    except:
                        masterdata_con.loc[count_con, column[0]] = ''
                count_con += 1

        return masterdata_loc, masterdata_con, latlong
