from datashop.imports import *


class Refinery():
    '''Fits and keeps track of the performance of multiple pipelines '''

    def __init__(self,X,y):
        self.run_id = 1
        self.models={}
        self.report = pd.DataFrame(
            columns=['description','f1_score','accuracy']
            )
        
        self.load_data(X,y)
    
    def load_data(self,X,y):
        self.X = X
        self.y = y

    def ingest(self,pipeline,info = None):
        self.info = info
        self.pipeline = pipeline
        self.models[self.run_id] = Batch(
                                    self.X,
                                    self.y,
                                    pipeline,
                                    info)
        
        self.report = self.report.append(
            self.models[self.run_id].row_dict,
            ignore_index=True)

        self.run_id += 1

        display(self.report)

        
class Batch():
    '''Runs and evaluates performance of given pipeline '''

    def __init__(self,X,y,pipeline,info = None):

        self.X = X
        self.y = y
        self.pipeline = pipeline
        self.info =info 

        self.scoring = {
            'accuracy' : make_scorer(
                metrics.accuracy_score),  
            'f1_score' : make_scorer(
                metrics.f1_score, average = 'weighted')}


        self.class_dict = cross_validate(
            self.pipeline,self.X,self.y,scoring=self.scoring,cv=6)
        
        self.row_dict ={
            'Model':type(self.pipeline[1]).__name__,
            'Vectorizer':type(self.pipeline[0]).__name__,
            'accuracy':self.class_dict['test_accuracy'].mean(),
            'f1_score':self.class_dict['test_f1_score'].mean()
        }

        if self.info:
            self.row_dict.update(self.info)