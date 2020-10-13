from datashop.imports import *
from datashop.datashop import * 

class Feature:
    
    def __init__(self,series,name):
        
        self.series = series
        self.name = name
        self.feature_type = 'default'
        self.report = pd.Series()
        self.desc = self.series.describe()
        
        self.null_count = self.series.isna().sum()
        self.null_percent = round((self.null_count/len(self.series))*100,2)
        
        self.types = self.series.dropna().apply(
            lambda x: type(x).__name__)
        self.type_counts = self.types.value_counts()
        
        self.val_counts = self.series.value_counts()
        self.cat_ratio = len(self.val_counts)/len(self.series)
        self.cat_threshold = 0.20           
            
        self.report['Length'] = len(self.series)
        self.report['Values'] = self.series.count()
        self.report['Missing']= str(self.null_count) +'({})%'.format(self.null_percent)
        self.report['Unique'] = len(self.val_counts)
        
        self.type_map = {
            'str':self.StringFeature,
            'int':self.NumericFeature,
            'float':self.NumericFeature,
            'datetime64':self.DateFeature,
            'datetime32':self.DateFeature,
            'category':self.Categorical
        }
        
        if len(self.type_counts) > 1:
            self.Categorical()
        elif isinstance(
            self.series.index,pd.core.indexes.datetimes.DatetimeIndex):
            self.DateFeature()
        elif len(self.type_counts.index) == 0:
            print("{} is empty".format(self.name))
        else:
            self.type_map[str(self.type_counts.index[0])]()
        
        
        if self.cat_ratio < self.cat_threshold:
            self.report['Possibly Categorical?'] = 'Yes'  
        else:
            self.report['Possibly Categorical?'] = 'No'  
            
    def NumericFeature(self):
        
        self.feature_type = 'numeric'
        self.report['Feature_Type'] = 'Numeric'
        self.report['Mean'] = self.series.mean()
        self.report['Median'] = self.series.median()
        
        self.plot_map = {
            'figure':{
                    'figsize':[12,12],
                    'grid_size':[12,12]
                    },
            'plots':[
                {
                'type':self.box_plot,
                'data':self.series,
                'location':[slice(None,2),slice(None)]
                },
                {
                'type':self.histo,
                'data':self.series,
                'location':[slice(2,9),slice(None)]
                }
                ]
        }
        
    def StringFeature(self):

        self.feature_type = 'string'
        self.report['Feature_Type'] = 'String'
        self.str_lengths = self.series.fillna(' ').apply(len)
        
        self.report['Mean Length'] = self.str_lengths.mean()
        self.report['Median Length'] = self.str_lengths.median()
        
        self.series.fillna(' ',inplace = True)
        self.chart_words = 25
        self.countvec = CountVectorizer(stop_words='english')
        self.wordcounts= self.countvec.fit_transform(self.series)
        self.word_totals = self.wordcounts.toarray().sum(axis=0)
        self.words = self.countvec.get_feature_names()
        self.count_dict = dict(zip(self.words,self.word_totals))
        self.count_series = pd.Series(self.count_dict)
        self.count_series.sort_values(ascending = False,inplace=True)
        
        self.plot_map = {
            'figure':{
                    'figsize':[16,12],
                    'grid_size':[12,12]
                    },
            'plots':[
                    {
                    'type':self.box_plot,
                    'data':self.str_lengths,
                    'location':[slice(None,2),slice(None)]
                    },
                    {
                    'type':self.histo,
                    'data':self.str_lengths,
                    'location':[slice(2,9),slice(None)]
                    },
                    {
                    'type':self.bar_plot,
                    'data':self.count_series.head(self.chart_words),
                    'location':[slice(9,None),slice(None)]
                    }
                    ]
                }
      
    def DateFeature(self):
        
        self.feature_type = 'date'

        self.series.sort_index(ascending=True,inplace=True)
        
        self.report["Earliest Point"] = self.series.index[0]
        self.report["Latest Point"] = self.series.index[-1]
        
        self.series.sort_index(ascending=True,inplace=True)
        
        self.plot_map = {
            'figure':{
                        'figsize':[16,6],
                        'grid_size':[16,6]
                        },
            'plots':[
                {
                'type':self.line_plot,
                'data':self.series,
                'location':[slice(None),slice(None)]
                }
                ]
            }
    
    def Categorical(self):

        self.feature_type = 'categorical'
        
        display(self.report)
        
        self.series = self.series.astype('category')
        
        self.plot_map = {
            'figure':{
                        'figsize':[12,.75*len(self.val_counts)],
                        'grid_size':[12,12]
                        },
            'plots':[
                {
                'type':self.box_plot,
                'data':self.series,
                'location':[slice(0,2),slice(None)]
                }
                ]
            }
        
    def bar_plot(self,series,grid_loc):
        
        self.bar_chart = self.fig.add_subplot(grid_loc)
        self.bar_chart.bar(
            list(series.index),
            series,
            width=0.7)
        self.bar_chart.tick_params(
                    axis='x', 
                    labelrotation=55,
                    length=10,
                    labelsize= 10
                    )
        
    def box_plot(self,series,grid_loc):
        
        self.box_axes = self.fig.add_subplot(grid_loc)
        self.box_axes.boxplot(series,vert=False)
        
    def line_plot(self,series,grid_loc):
        
        self.line_axes = self.fig.add_subplot(grid_loc)
        self.line_axes.plot(series)
    
    def histo(self,series,grid_loc):

        self.histo = self.fig.add_subplot(grid_loc)
        self.n = self.histo.hist(series,bins=100)[0]
        
        self.vert_marks = series.describe().loc[
            ['mean',
            '25%',
            '50%',
            '75%']
        ]
       
        self.histo.vlines(
            self.vert_marks,
            ymin=0,
            ymax=max(self.n) *1.2,
            linestyles='dashed')
        
        for index,value in self.vert_marks.items():
            
            self.histo.annotate(
                index,
                (value,max(self.n) *.9)
            )
            
    def show_report(self,show_charts = True):
        
        display(self.report)
        
        if show_charts:       
            self.plot_charts()
        
    def plot_charts(self): 

        self.fig = plt.figure(figsize=(*self.plot_map['figure']['figsize'],))

        self.grid = plt.GridSpec(
            *self.plot_map['figure']['grid_size'],
            wspace=0.6,
            hspace=1)

        for plot in self.plot_map['plots']:
            self.gridloc = plot['location']
            plot['type'](plot['data'],self.grid[self.gridloc[0],self.gridloc[1]])

    def cull_outliers(self,threshold=0.05,upper=True,lower=True,inplace = False):

        self.outliers_list = find_outliers(self.series,threshold,upper=upper,lower=lower)

        if inplace:
            self.series = self.series.drop(labels=self.outliers_list) 
        else:
            self.culled = self.series.drop(labels=self.outliers_list)

    def cull_report(self,base,upper=True,lower=True):
        '''Returns report frame describing row loss from base frame from 1 going to base threshold'''

        self.cull_report,self.cull_chart = cull_report(
            self.series,
            base,
            upper=upper,
            lower=lower,
            plot=True,
            show=True
        )

    def min_max_col(self):
        ''' Scales a given series/column values using min max scaling  '''
        self.mm_scaled = (self.series - min(self.series)) / (max(self.series) - min(self.series))



