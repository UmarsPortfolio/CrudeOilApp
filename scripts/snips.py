      self.cull_series = pd.Series()

        self.base = int(base_threshold * 100)
    
        for x in range (1,self.base,1):
            
            self.current = round(float(x/100),2)
            self.cull_outliers(threshold = self.current)
            self.cull_loss = (len(self.series) -len(self.culled))/len(self.series)
            self.cull_series[str(self.current)] = self.cull_loss
        
        self.cull_fig,self.cull_ax = plt.subplots(figsize=(16,6))
        self.cull_ax.bar(self.cull_series.index,self.cull_series)
        self.cull_ax.tick_params(
                    axis='x', 
                    labelrotation=55,
                    length=10,
                    labelsize= 10
                    )


                    ##################################################################
self.series_map = {
            self.feature.name:self.originals,
            'scaled':self.scaled,
            'delta':self.deltas,
            'rolling':self.rolling
        }    

        ##########################
         self.features[self.feature.name] = self.feature
        for col in self.feature.series_frame.columns:
            self.feat_type = col.split('_')[0]
            self.ingest_frame = self.series_map[self.feat_type]
            self.ingest_frame = pd.merge_asof(
                self.series_map[self.feat_type],
                self.feature.series_frame[col],
                right_index=True,
                left_index=True
                )