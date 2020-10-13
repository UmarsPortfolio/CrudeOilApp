class TopicModel:
    ''' Fits and evaluates LDA or NMF topic model. 

        Streamlines Topic Modeling Workflow by vectorizing the corpus,
        fitting a model and assessing how closely calculated components
        align with existing labels. 

        Arguments:
        text_col -- (str) name of the column containing text corpus
        labels_col -- (str) name of column with the labels 
        model_type -- (str) 'lda' or 'nmf'
        n_topics -- (int) the number of model components to create
        stop_words -- (str or list) the stop words to exclude
        dataframe -- (pandas dataframe) Guess. 

        Methods:
        Upon initialization, the first three methods are called in
        reverse sequence. These are the core methods of the class. 

        fit_mod -- instantiates either a CountVectorizer object and 
            a LDA object, or a TfidfVectorizer object and an NMF object
            based on model_type value passed in at instantiation, with 
            n_topics number of components. The text is vectorized and 
            passed into the model. Component numebrs for each document
            are added back to the dataframe. 

        mod_reporting -- Calculates the distribution of original labels
            in the set of documents that are assigned each given model
            component number. 
            Also gathers the highest occuring label for the component,
            as long as this was not the highest occuring label for a 
            previously evaluated component, into a dictionary. This
            is used in the next method to assigne a label to a component. 

        map_topics --
            assigns a label to a component based on the dictionary 
            caculated from the previous method. Also calculates a column
            that checks if the original label matches the label assigned
            by the model and the mapping. 

        dist_charts -- 
            returns a figure with subplots each showing the distribution
            of original labels for a given component

        acc_report -- 
            calculates the rate at which the original label matches the 
            label assigned by the map_topics method for each label, as
            well as the overall match rate. '''

    rand_state = 42
    import math
 
    def __init__(
        self,
        text_col,
        labels_col,
        model_type = None ,
        n_topics =None, 
        stop_words= None,
        dataframe = None,
        description = None,
        ):
 
        self.data = dataframe
        self.n_topics = n_topics
        self.stop_words = stop_words
        self.text_col = text_col
        self.labels_col = labels_col
        self.model_type = model_type
 
        self.map_topics()
        self.report_row = {
            'Description':description,
            'Model Type':self.model_type,
            'Stop Words':self.stop_words,
            'Accuracy':self.acc_score,
        }

    
    def fit_mod(self):
 
        if self.model_type == 'lda':
            self.vect_object = CountVectorizer(
                stop_words=self.stop_words,ngram_range=(1,1))
            self.mod_object = LatentDirichletAllocation(
                n_components=self.n_topics,
                random_state=self.rand_state)
        elif self.model_type == 'nmf':
            self.vect_object = TfidfVectorizer(
                stop_words=self.stop_words,
                ngram_range=(1,1))
            self.mod_object = NMF(
                n_components=self.n_topics,
                random_state=self.rand_state)
        else:
            raise Exception('must specify model type as lda or nmf')
 
        self.vectors = self.vect_object.fit_transform(self.data[self.text_col])
        self.mod_object.fit(self.vectors)
 
    
        self.topic_matrix = self.mod_object.transform(self.vectors)
        self.data.loc[:,'mod_number'] = self.topic_matrix.argmax(axis=1)
 
    def mod_reporting(self):
        self.fit_mod()
        self.mod_nums = list(self.data['mod_number'].value_counts().index)
 
        self.mod_series = {}
        self.topic_map = {}
 
        for numb in self.mod_nums:
            # Slice all rows with this mod topic number. Get original label colum
            self.sr_labels = self.data[self.data['mod_number'] == int(numb)][self.labels_col]
 
            # Assign value counts of orignal labels for this  
            self.mod_series[numb] = self.sr_labels.value_counts()
            self.labels_ordered = list(self.sr_labels.value_counts().index)
                                
            i = 0
            while self.labels_ordered[i] in self.topic_map.values():
                i += 1
                if i >= len(self.labels_ordered):
                    break
            else:
                self.topic_map[numb] = self.labels_ordered[i]
 
        self.mod_report = pd.concat(self.mod_series,axis=1).fillna(0)
 
    def map_topics(self):
        self.mod_reporting()
        self.data.loc[:,'mod_label'] = self.data['mod_number'].replace(self.topic_map)
        self.data.loc[:,'mod_match'] = self.data[self.labels_col] == self.data['mod_label']
        self.acc_score = sum(self.data.loc[:,'mod_match'])/len(self.data)
 
    def dist_charts(self):
        self.chart_num = len(self.mod_nums)
 
        if self.chart_num % 5 == 0:
            self.row_num = int(self.chart_num/5)
        else:
            self.row_num = int(math.ceil(self.chart_num/5))
 
        self.lda_fig,self.ax = plt.subplots(
            nrows=self.row_num,
            ncols=5,
            figsize = (40,7*self.row_num))
        
        self.lda_fig.canvas.draw()
 
        for col,ax in zip(list(self.mod_report.columns),self.ax.flatten()):
            ax.bar(
                self.mod_report.index,
                self.mod_report[col]
            )
 
            ax.tick_params(
                axis='x', 
                labelsize=12,
                labelrotation=45,
                length=0
                )
            
            ax.set_title(
                label='LDA Number: ' + str(col),
                loc='right',fontdict={
                    'color':'#434343',
                    'fontsize':18,
                    },
                    y=0.7
                    )
 
            self.lda_fig.canvas.draw()
            self.xlabels_new = [label.get_text().replace(' ', '\n') for label in ax.get_xticklabels()]
            ax.set_xticklabels(self.xlabels_new)
 
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
 
        self.lda_fig.tight_layout()
        self.lda_fig.show()
 
    def acc_report(self):
 
            self.acc_dict = {}
            self.df_groupby = self.data.groupby(self.labels_col)
 
            for name,group in self.df_groupby:
 
                self.labels = group[self.labels_col]
                self.predicts = group['mod_label']
 
                self.acc_dict[name]= sum(self.labels == self.predicts)/len(self.labels)
                
            
            self.acc_series = pd.Series(self.acc_dict)
            self.acc_series['OVERALL'] = self.acc_score
            self.acc_series.sort_values(inplace=True)
            self.acc_series.plot(figsize=(12,12),kind='barh',xlim= (0,1))

