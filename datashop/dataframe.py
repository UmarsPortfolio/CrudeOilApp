from datashop.imports import *
from datashop.feature import *

class Dataset():

    def __init__(self,dataframe):

        self.dataframe = dataframe

        self.features = {}

        self.categoricals= []
        self.numericals = []
        self.strings = []  
        self.default = []  
        self.timeseries = []       

        self.feature_types  = {
            'string':self.strings,
            'numeric':self.numericals,
            'categorical':self.categoricals,
            'default': self.default,
            'date':self.timeseries
        }

        for col in self.dataframe.columns:
            self.feat = Feature(self.dataframe[col],col)
            self.features[col] = self.feat
            self.feature_types[self.feat.feature_type].append(col)
        
        self.report()
    def __getitem__(self,sliced):
        return self.features[sliced]

    def report(self,n_highest_counts = 10):
        self.df_report = report(self.dataframe,n_highest_counts = 10)
    
    def dict_trim(self,culling_dict, lesser = False):
        self.dataframe = dict_trim(self.dataframe,culling_dict, lesser=lesser)

    def thresh_trim(self,columns = None, threshold = 0.05, upper=True,lower=True):

        self.trim_columns = columns 

        if self.trim_columns is None:
            self.trim_columns = self.numericals

        self.dataframe  = thresh_trim(
            self.dataframe,
            threshold,
            columns = self.trim_columns,
            upper=upper,
            lower=lower)

    def thresh_report (self,base_threshold = 0.20,columns = None):
        pass

    def logarize(self,columns):
        self.dataframe = logarize(self.dataframe,columns)

  

    


    
    





    


