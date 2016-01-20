#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

******************************************************
Test Plan summary report
******************************************************

"""

# Import standard Python packages
import time
# import plotly.plotly as py
# py.sign_in("skapadia", "dw1pq71zma")
import sys
import logging
import getopt
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# Import internal packages
from database.main import *
from exposurecoverage.exposure_coverage import *

warnings.filterwarnings('ignore')

OPTLIST, ARGS = getopt.getopt(sys.argv[1:], [''], ['outfile='])

OUTFILE = None
for o, a in OPTLIST:
    if o == "--outfile":
        OUTFILE = a
    print ("Outfile: " + OUTFILE)

OUTFILE = 'C:\Users\i56228\Documents\Python\Git\ExposureCoverage\sample.csv'
if OUTFILE is None:
    print ('Outfile is not passed')
    sys.exit()

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

HANDLER_INFO = logging.FileHandler(OUTFILE[:-4] + '-info.log')
HANDLER_INFO.setLevel(logging.INFO)
LOGGER.addHandler(HANDLER_INFO)

__author__ = 'Shashank Kapadia'
__copyright__ = '2015 AIR Worldwide, Inc.. All rights reserved'
__version__ = '1.0'
__interpreter__ = 'Anaconda - Python 2.7.10 64 bit'
__maintainer__ = 'Shashank kapadia'
__email__ = 'skapadia@air-worldwide.com'
__status__ = 'Complete'

# noinspection PyBroadException
try:
    test_plan = sys.argv[1]
except:
    LOGGER.error('Please verify the inputs')
    sys.exit()

if __name__ == "__main__":

    start = time.time()
    server = 'QAAUTODEV2'
    database = 'ExecutionCoverage'
    # noinspection PyBroadException
    try:
        db = Database(server)
    except:
        LOGGER.info('Unable to establish connection with the server')
        sys.exit()

    # noinspection PyBroadException
    try:
        dir_path = db.get_inputfile_folder(database, test_plan)
    except:
        LOGGER.info('Error while fetching input directory')
        sys.exit()

    # noinspection PyBroadException
    try:
        for i in range(len(dir_path)):
            path = dir_path.iloc[i, 0].split('"')[1]
            exp = ExposureCoverage(path)
            data = exp.run_coverage_dir()
    except:
        LOGGER.info('Core Algorithm failed')
        sys.exit()

    # noinspection PyBroadException
    try:
        map_figure = Basemap(projection='gall',
                             resolution='l',
                             area_thresh=100000.0,
                             )
        map_figure.bluemarble()
        # noinspection PyUnboundLocalVariable
        x, y = map_figure(data[2]['Longitude'].values, data[2]['Latitude'].values)
        map_figure.plot(x, y, 'r+', markersize=6)
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        plt.savefig('sample.png', bbox_inches='tight', pad_inches=0)
    except:
        LOGGER.info('Unable to generate the figure')
        sys.exit()

    # noinspection PyBroadException,PyBroadException,PyBroadException
    try:
        exposure_details = pd.DataFrame()
        exposure_details['Total Contract Files'] = [len(data[1]['FileName'])]
        exposure_details['Total Location Files'] = [len(data[0]['FileName'])]
        exposure_details['Total Locations'] = [data[0]['UniqueLocationID'].sum()]
        exposure_details['Total Replacement Value (Bldg)'] = \
            [data[0]['SumBuildingValue'].convert_objects(convert_numeric=True).sum()]
        exposure_details['Total Replacement Value (Other)'] = \
            [data[0]['SumOtherValue'].convert_objects(convert_numeric=True).sum()]
        exposure_details['Multi Scenario'] = zip(data[0]['MultiScenario'].unique())
        exposure_details = exposure_details.transpose()
        exposure_details.columns = ['Values']
        exposure_details_html = exposure_details.to_html(justify='left'). \
            replace('<table border="1" class="dataframe">', '<table class="table table-striped">')
    except:
        LOGGER.info('Unable to create Exposure summary')
        sys.exit()

    # noinspection PyBroadException
    try:
        execution = db.get_testplan_summary(database, test_plan)
    except:
        LOGGER.info('Error fetching Test plan summary')
        sys.exit()

    # noinspection PyBroadException
    try:
        execution_steps = pd.DataFrame()
        execution_steps['Steps'] = execution['Step'].unique()

        execution_options = pd.DataFrame()
        event_set = []
        for i in range(len(execution)):
            # noinspection PyBroadException
            try:
                event_set.append((execution['Options'][i].split(':')[1].split(',')[0].
                                  replace(' [', '').replace(']', '')))
            except:
                pass
        execution_options['Event Sets'] = list(set(event_set))

        execution_steps_html = execution_steps.to_html(justify='left'). \
            replace('<table border="1" class="dataframe">', '<table class="table table-striped">')
        execution_options_html = execution_options.to_html(justify='left'). \
            replace('<table border="1" class="dataframe">', '<table class="table table-striped">')
    except:
        LOGGER.info('Unable to create test plan summary')
        sys.exit()

    string_html = '''
    <html>
    <head>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">
        <style>body{ margin:0 100; background:whitesmoke; }</style>
    </head>
    <body>
        <h1>''' + test_plan + ''' Test Plan Summary</h1>

        <!-- *** Section 1 *** --->
        <h2>Section 1: Exposure Summary</h2>
        <center><img src="sample.png" alt="Exposure Geography"  align="middle"></center>
        <p>Geographic dispersions of locations used in the Test plan</p>
        <h3>Reference table: Contract and Location file summary</h3>
        ''' + exposure_details_html + '''
        <!-- *** Section 2 *** --->
        <h2>Section 2: Execution Summary</h2>
        <h3>Reference table: Unique Steps used in the execution</h3>
        ''' + execution_steps_html + '''
        <h3>Reference table: Event sets covered in the test plan</h3>
        ''' + execution_options_html + '''
    </body>
    </html>'''
    f = open('report.html', 'w')
    f.write(string_html)
    f.close()

    LOGGER.info('----------------------------------------------------------------------------------')
    LOGGER.info('                                Completed Successfully                            ')
    LOGGER.info('----------------------------------------------------------------------------------')

    LOGGER.info('********** Process Complete Time: ' + str(time.time() - start) + ' Seconds **********')
