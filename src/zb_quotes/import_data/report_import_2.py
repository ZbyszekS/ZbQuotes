from dataclasses import dataclass, field

import datetime as dt
from collections import defaultdict
import logging
import json

from zb_quotes.import_data.yf_data import YfDownloadCondition

@dataclass
class ImportReport:
    start_time: dt.datetime = None
    end_time:   dt.datetime = None
    fetch_times: list[tuple[dt.datetime, dt.datetime]] = field(default_factory=list)
    # fetch_duration: dt.timedelta = dt.timedelta(0)
    quotes_count:    int = 0
    dividends_count: int = 0
    splits_count:    int = 0
    tck_2_vfits_id_2_update: dict[str, int] = field(default_factory=dict) # {ticker: vfits_id}
    tf_processed: list[int] = field(default_factory=list)
    process_dict: dict[int, dict[
        YfDownloadCondition, list[list[str]]
        ]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(list)))
    
    def add_quotes_count(self, count: int):
        self.quotes_count += count
    
    def add_dividends_count(self, count: int):
        self.dividends_count += count
    
    def add_splits_count(self, count: int):
        self.splits_count += count
    
    def print_report(self, logger: logging.Logger):
        fetch_duration = sum( (end - start for start, end in self.fetch_times), dt.timedelta(0) )
        logger.info('----------------------------------------')
        logger.info(f"Report from import quotes from yfinance")
        logger.info(f"Start time     : {self.start_time}, end time: {self.end_time}")
        logger.info(f"Duration       : {self.end_time - self.start_time}")
        logger.info(f"Fetch duration : {fetch_duration}")
        logger.info(f"Vfi time series to process: {len(self.tck_2_vfits_id_2_update)}")
        logger.info(f"Tickers to vfits_id: {self.tck_2_vfits_id_2_update}")
        logger.info('--------- processing info --------------')
        # logger.info(f"Process dict   : {json.dumps(self.process_dict, indent=2)}")
        for tf_id, conditions in self.process_dict.items():
            logger.info(f"Time frame {tf_id}:")
            for cond, tickers in conditions.items():
                logger.info(f"  Condition {str(cond)}")
                for ticker_batch in tickers:
                    logger.info(f"    Batch: {ticker_batch}")
        logger.info('--------- summary info --------------')
        logger.info(f"Quotes count   : {self.quotes_count}")
        logger.info(f"Dividends count: {self.dividends_count}")
        logger.info(f"Splits count   : {self.splits_count}")
        logger.info(f"Fetch times    : {self.fetch_times}")
        logger.info('---------- end of report ---------------')