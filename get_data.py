from datashop import *
from scripts import *
import requests
import sqlite3
import pprint as pp
import pdb
from statsmodels.tsa.seasonal import seasonal_decompose
import plotly.offline as pyo
import plotly.graph_objs as go

dep = Depot()

daily_price = EIA_Series('Daily Price','PET.RWTC.D')
dep.ingest(daily_price)

desc = ''
daily_production = EIA_Series('Weekly Stocks','PET.WTTSTUS1.W')
dep.ingest(daily_production)

desc = 'US imports of crude oil, monthly'

monthly_imports = EIA_Series('Monthly Imports','PET.MCRIMUS1.M',desc,date_format='%Y%m' )
dep.ingest(monthly_imports)


