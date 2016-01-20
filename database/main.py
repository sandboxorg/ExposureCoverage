# Import standard Python packages
import pip

# Import external Python libraries
# noinspection PyBroadException
try:
    import pandas as pd
except:
    pip.main(['install', 'pandas'])
    import pandas as pd
# noinspection PyBroadException
try:
    import pyodbc
except:
    pip.main(['install', 'pyodbc'])
    import pyodbc


# noinspection PyPep8
class Database:
    def __init__(self, server):
        # Initializing the connection and cursor
        self.connection = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server)
        self.cursor = self.connection.cursor()

    def get_inputfile_folder(self, database, test_plan):
        script = 'SELECT DISTINCT a.Step ' \
                 'FROM [' + database + '].[dbo].[tTestCaseOption] a ' \
                                       'JOIN [' + database + '].[dbo].[tTestPlan] b ON a.TestPlanID = b.TestPlanID ' \
                                                             'WHERE b.TestPlan = ' + "'" + str(
            test_plan) + "'" + ' AND a.Step like ' + "'%the input file%'"

        return pd.read_sql(script, self.connection)

    def get_testplan_summary(self, database, test_plan):
        script = 'SELECT DISTINCT a.Step, a.Options ' \
                 'FROM [' + database + '].[dbo].[tTestCaseOption] a ' \
                                       'JOIN [' + database + '].[dbo].[tTestPlan] b on a.TestPlanID = b.TestPLanID ' \
                                                             'WHERE b.TestPlan like ' + "'" + str(test_plan) + "'" + \
                 ' AND a.step not like ' + "'I import%'" + ' ' \
                                                           'AND a.step not like ' + "'%view exists%'" + ' ' \
                                                                                                        'AND a.step not like ' + "'%completes%'" + ' ' \
                                                                                                                                                   'AND a.step not like ' + "'the input%'" + ' ' \
                                                                                                                                                                                             'AND a.step not like ' + "'the project%'" + ' ' \
                                                                                                                                                                                                                                         'AND a.step not like ' + "'%database%'"

        return pd.read_sql(script, self.connection)
