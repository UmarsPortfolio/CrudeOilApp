import requests
import json
from datashop import * 

class EIA_Series:
    
    eia_api_url= 'http://api.eia.gov/series/?api_key=651b30b69f4f47a13a2912d673f7da93&series_id='
    
    
    def __init__(
        self,
        name,
        id,
        desc = None,
        date_format='%Y%m%d'
    ):
        self.name = name
        self.id = id
        self.desc = desc
        self.date_format = date_format
        
        self.request = requests.get(self.eia_api_url+self.id)
        self.series_dict = json.loads(self.request.text)
        self.make_df()
        
    def show_response(self):
        
        pp.pprint(self.series_dict)
          
        
    def make_df(self,data_col='data',date_col='Date'):
        
        self.data_col = data_col
        self.date_col = date_col
        
        self.series_list=self.series_dict['series'][0][data_col]
        
        self.series_frame = pd.DataFrame(self.series_list)
        self.series_frame.columns=[self.date_col,self.name]     
        
        self.series_frame[self.date_col]=pd.to_datetime(
            self.series_frame[self.date_col],
            format = self.date_format
        )
        
        self.series_frame.set_index(
            self.date_col,drop=True,inplace=True)
            
        self.series_frame.sort_index(ascending=True,inplace=True)

        self.series = self.series_frame.iloc[:,0]

        self.series_frame['scaled_'+self.name] = min_max_col(self.series)
        self.series_frame['delta_'+self.name] = self.series_frame[self.name].diff()
        self.series_frame['rolling_'+self.name] = self.series_frame[self.name].rolling(window=50).mean()

        

    def chart(self):
        self.fig,self.ax = plt.subplots(figsize=(10,6))
        self.ax.plot(self.series_frame)
    def report(self):
        print(
        "Earliest Point: {} \n".format(self.data.iloc[0].name),
        "Latest Point: {} \n".format(self.data.iloc[-1].name),
        ""
        )


class Depot:

    def __init__(self):

        self.features = {} 

    def ingest(self,feature):

        self.feature = feature

        if len(self.features) == 0:
            self.originals = self.feature.series_frame[self.feature.name]
            self.scaled = self.feature.series_frame['scaled_'+ self.feature.name]
            self.deltas = self.feature.series_frame['delta_'+ self.feature.name]
            self.rolling = self.feature.series_frame['rolling_'+ self.feature.name]

        else:
            self.originals = pd.merge_asof(
                self.originals,
                self.feature.series_frame[self.feature.name],
                right_index=True,
                left_index=True
                )

            self.scaled = pd.merge_asof(
                self.scaled,
                self.feature.series_frame['scaled_'+ self.feature.name],
                right_index=True,
                left_index=True
                )

            self.deltas = pd.merge_asof(
                self.deltas,
                self.feature.series_frame['delta_'+ self.feature.name],
                right_index=True,
                left_index=True
                )

            self.rolling = pd.merge_asof(
                self.rolling,
                self.feature.series_frame['rolling_'+ self.feature.name],
                right_index=True,
                left_index=True
                )

        self.features[self.feature.name] = self.feature

       
       
            
       
           





