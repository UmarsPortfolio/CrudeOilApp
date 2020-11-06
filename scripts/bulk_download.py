from data.data_functions import *
import math
import datetime as dt
import sqlite3
import pandas as pd

from datashop import *

start_date = '2001-01'

end_date = '2020-10'


# EIA_Bulk


eia_dict = {
    'PET.WTTSTUS1.W':['WeeklyStocks','235081','%Y%m%d'],
    'PET.RWTC.D':['DailyPrice','241335','%Y%m%d'],
    'PET.WRPUPUS2.W':['ProductSupplied','401676','%Y%m%d'],
    'PET.E_ERTRRO_XR0_NUS_C.M':['MonthlyRigCount','296749','%Y%m']
}

for key,val in eia_dict.items():

    e_ser = EIA_Series(val[0],key,date_format = val[2])

    bulk_ser = e_ser.series[start_date:end_date]

    bulk_ser.to_sql(val[0],conn,if_exists='replace')  
