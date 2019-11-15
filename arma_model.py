import pandas as pd
import statsmodels.api as sm
import tweepy

from alpha_vantage.alpha_vantage.timeseries import TimeSeries


class AVDataStream:
    '''A base class to implement data input 
    functions from AlphaVantage.

    Parameters
    ----------
    stream : TimeSeries object
        Object from which data is derived
    '''
    def __init__(self, api_key, stream=TimeSeries, **kwargs):
        self.api_key = api_key
        self.stream = stream
        
        self.kwargs = kwargs

    
    def start_stream(self, **kwargs):
        self.stream = self.stream(key=self.api_key, output_format='pandas') 


    def close_stream(self, **kwargs):
        pass


    def get_data(self, **kwargs):
        '''Retrieves timeseries data from stream.
        
        Parameters
        ----------
        get_fun: method
            TimeSeries method. This method is passed
            kwargs.
        '''
        try:
            data, meta_data = self.stream.get_intraday(symbol='VXX', interval='1min', outputsize='full')
            
        except TypeError:
            print('Stream has not been started yet.')

        # Drop rows containing zeros
        data = data.loc[(data!=0).any(1)]

        # Reverse data
        data = data.iloc[::-1]
            
        return (data, meta_data)


class StatsModel:
    '''A class to implement statsmodels
    time series model functionality.

    Parameters
    ----------
    model : statsmodels class
        Model to be fit
    '''
    def __init__(self, model=sm.tsa.ARMA,
                 n_examples=None,
                 opt_order=None,
                 **kwargs):
        self.model = model
        self.n_examples = n_examples    # Number of examples in X
        self.opt_order = opt_order      # Optmimum (p, q) selected
        
        self.kwargs = kwargs

        
    def fit(self, X, y=None, **kwargs):
        '''Finds the order of an ARMA process
        and fits the ARMA model on the data.

        Parameters
        ----------
        X : Pandas dataframe 
            Training data
        '''
        # Get number of training examples
        self.n_examples = X.shape[0]
        
        # Get IC values for ARMA models
        #orders = sm.tsa.stattools.arma_order_select_ic(X,
        #                                               max_ar=4,
        #                                               max_ma=2,
        #                                               ic='bic'
        #                                               )

        # Select the optimal order
        #self.opt_order = orders.bic_min_order

        self.opt_order = (1,1)
        try: 
            self.model = self.model(X, self.opt_order, **kwargs).fit(disp=False)

        except:
            self.model = sm.tsa.ARMA(X, self.opt_order, **kwargs).fit(disp=False)
        
    def predict(self, X, n_ahead=5, **kwargs):
        ''' Generate n_ahead prediction of target using fitted
        ARMA model.

        Parameters
        ----------
        n_ahead : int
            Index of prediction target period minus the last
            training example.
        
        Returns
        -------
        array containing the predicted values
        '''
        if self.n_examples is None:
            raise Exception('Model has not been fitted yet.')

        preds, stderr, ci = self.model.forecast(n_ahead)

        return (preds, stderr, ci, self.opt_order)

        
class TwitterOutput:
    def __init__(self,
                 consumer_key,
                 consumer_secret,
                 access_key,
                 access_secret,
                 auth=None,
                 api=None,
                 **kwargs):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_key
        self.access_secret = access_secret
        
        self.auth = auth
        self.api = api

        self.kwargs = kwargs


    def start_output(self, **kwargs):
        auth = tweepy.OAuthHandler(self.consumer_key,
                                   self.consumer_secret
                                   )

        auth.set_access_token(self.access_token,
                              self.access_secret
                              )
        
        self.auth = auth
        
        self.api = tweepy.API(auth)

        self.api.verify_credentials()
            

    def close_output(self, **kwargs):
        pass


    def make_output(self, preds, target_time, current_vwap, stderr,
                    ci, opt_order):
        prediction = preds[4].round(4)
        
        confint = ci[4].round(4)
        
        # Create output string
        output_0 = 'Current price of VXX: ' + str(current_vwap) + '.'

        output_1 = ' Estimated price of VXX at ' + str(target_time)[:-10]

        output_2 = ' US/Eastern is: ' + str(prediction)

        output_3 = ' with 95% confidence interval of: ' + str(confint)

        output_4 = '. Calculated using ARMA model with (p,q) parameters: ' + str(opt_order)

        output = output_0 + output_1 + output_2 + output_3 + output_4

        print(output)
        
        self.api.update_status(status=output)


def main(bot, target_time):
    # Get new data
    data, meta_data = bot.get_data()

    # Get close values:
    close = data['4. close']

    current_vwap = close.iloc[-1]
    
    # Check for update
    if meta_data['3. Last Refreshed'] != bot.last_update:
        # Fit the model
        bot.train_model(close)
        
        # generate predictions
        preds, stderr, ci, opt_order = bot.get_prediction(close)

        bot.make_output(preds, target_time=target_time, current_vwap=current_vwap, stderr=stderr, ci=ci,opt_order=opt_order)

        bot.last_update = meta_data['3. Last Refreshed']

        
