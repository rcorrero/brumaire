

class Bot:
    def __init__(self, datastream,
                       model,
                       output,
                       last_update=None # Datetime of latest data
                 ):
        self.datastream = datastream
        self.model = model
        self.output = output
        self.last_update = last_update
        
    def start_stream(self, **kwargs):
        self.datastream.start_stream(**kwargs)


    def close_stream(self, **kwargs):
        self.datastream.close_stream(**kwargs)


    def get_data(self, **kwargs):
        return self.datastream.get_data(**kwargs)


    def train_model(self, X=None, y=None, **kwargs):
        self.model.fit(X, y, **kwargs)


    def get_prediction(self, X, **kwargs):
        try:
            return self.model.predict(X, **kwargs)

        except:
            print('Model is not fitted yet')


    def start_output(self, **kwargs):
        self.output.start_output(**kwargs)


    def close_output(self, **kwargs):
        self.output.close_output(**kwargs)


    def make_output(self, preds, **kwargs):
        self.output.make_output(preds, **kwargs)
            
     
