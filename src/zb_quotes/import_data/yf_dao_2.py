# Module for fetching quote data from Yahoo Finance using yfinance
#
import pandas as pd
import yfinance as yf
from .yf_data import DownloadInput


class YfDao2:
    def __init__(self):
        pass
    
    ####################################################
    # INTERFACE
    ####################################################
    
    def download_quotes(self, input: DownloadInput) -> pd.DataFrame:
        pass


    
    ####################################################
    # IMPLEMENTATION
    ####################################################

    def _download_quotes(self, input: DownloadInput) -> pd.DataFrame:
        """
            Downloads quotes from Yahoo Finance using yfinance.
            
            Args:
                input: 
                    - condition: DownloadCondition object with download parameters
                    - tickers:   List of tickers to download
                
            Returns:
                DataFrame with downloaded quotes
        """
        if input.condition.period:
            quotes = yf.download( # download for period back
                interval=    input.condition.interval,                

                period=      input.condition.period,

                tickers=     input.tickers, 
                
                auto_adjust= input.condition.auto_adjust, 
                actions=     input.condition.actions,
                repair=      input.condition.repair,
                group_by=    input.condition.group_by)

        elif input.condition.start and input.condition.end:
            quotes = yf.download( # download for start and end dates
                interval=   input.condition.interval,
                
                start=      input.condition.start, 
                end=        input.condition.end,

                tickers=    input.tickers, 
                
                auto_adjust=input.condition.auto_adjust, 
                actions=    input.condition.actions,
                repair=     input.condition.repair,
                group_by=   input.condition.group_by,

                )
        return quotes
        
    


