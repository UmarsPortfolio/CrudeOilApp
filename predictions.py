from datashop import *
from data_functions import *

import pprint as pp

#import chart_studio.plotly as py

import plotly.offline as pyo
import plotly.graph_objs as go
#from pmdarima.arima import auto_arima

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

from statsmodels.tsa.filters.hp_filter import hpfilter
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import adfuller,kpss,coint,bds,q_stat,grangercausalitytests,levinson_durbin
from statsmodels.tools.eval_measures import rmse
from statsmodels.tsa.statespace.tools import diff
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima_model import ARMA,ARMAResults,ARIMA,ARIMAResults

eia_dict = {        
        'DailyPrice':['DailyPrice','PET.RWTC.D','241335','%Y%m%d'],
        'WeeklyStocks':['WeeklyStocks','PET.WTTSTUS1.W','235081','%Y%m%d'],
        'ProductSupplied':['ProductSupplied', 'PET.WRPUPUS2.W','401676','%Y%m%d']
    }

dprice = eia_dict['DailyPrice']

price = EIA_Series(
    dprice[1], 
    name = dprice[0],
    date_format=dprice[3],
    scale=True,
    end='20201214'
    )

depot = Depot()

for key,val in eia_dict.items():
    feature = EIA_Series(
        val[1],
        name=val[0],
        date_format=val[3],
        scale=True
    )

    depot.ingest(feature)

df_dow = pd.read_csv('dowlatest.csv')

df_dow['Date'] = df_dow['Date']

df_dow['Date']=pd.to_datetime(
            df_dow['Date'],
            format = "%Y-%m-%d"
        )

scaler = MinMaxScaler()
df_dow['DOW_closing'] = scaler.fit_transform(df_dow[['Close']])

df_dow.set_index(df_dow['Date'],drop=True,inplace=True)        
df_dow.sort_index(ascending=True,inplace=True)  
df_dow = df_dow.asfreq(freq='D').fillna(method='ffill')

frame = depot.scaled.dropna()   #.loc[:'20200101']

frame = pd.merge_asof(
                frame,
                df_dow['DOW_closing'],
                right_index=True,
                left_index=True
                )

train_end = '20200701'
test_start = '20200702'
test_end = frame.index.max()

train = frame.loc[:train_end]
test = frame.loc[test_start:test_end]

exogs = ['scaled_WeeklyStocks','scaled_ProductSupplied','DOW_closing']

first_model = SARIMAX(
    train['scaled_DailyPrice'],
    exog=train[exogs],
    order=(2,1,2)
    ).fit()

predictions = first_model.predict(
    start=test_start,
    end=test_end ,
    exog = test[exogs],
    dynamic=False,typ='levels')

df_predicted = predictions.to_frame()
df_predicted.index.names = ['Date']
df_predicted.columns = ['Predicted']

import sqlite3
conn = sqlite3.connect(working_dir + '/data/energydash.db')


df_predicted.to_sql('Prediction',conn,if_exists='replace')

import sqlite3
conn = sqlite3.connect(working_dir + '/data/energydash.db')

df = pd.read_sql('SELECT * FROM Prediction LIMIT 10',con=conn)
