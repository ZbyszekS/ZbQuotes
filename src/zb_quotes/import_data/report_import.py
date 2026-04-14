# This module contains dataclasses for reporting import process
#

from dataclasses import dataclass, field
import datetime as dt


@dataclass
class Timing:
    _beg_time: dt.datetime
    _end_time: dt.datetime = None
    _duration: int = None
    
    @property
    def end_time(self) -> dt.datetime:
        return self._end_time
    
    @end_time.setter
    def end_time(self, value: dt.datetime):
        self._end_time = value
        if self._end_time and self._beg_time:
            self._duration = int((self._end_time - self._beg_time).total_seconds())
    
    @property
    def duration(self) -> int:
        return self._duration

@dataclass
class Counter4Tf:
    _1m:  int
    _1h:  int
    _1d:  int
    _1w:  int
    _1mo: int


@dataclass
class NonFetchedCause:
    no_new_data: int
    error:       int

@dataclass
class VfiTsFetch:
    on_input:          int
    on_input_by_tf:    Counter4Tf
    fetched:           int
    nonfetched:        int
    non_fetched_by_cause: NonFetchedCause
    fetch_error:       list[str]

    

@dataclass
class ImportReport:
    timing: Timing     = field(default_factory=lambda: Timing(_beg_time=dt.datetime.now()))
    vfits:  VfiTsFetch = field(default_factory=lambda: VfiTsFetch(
        on_input      =0,
        on_input_by_tf=Counter4Tf(_1m=0, _1h=0, _1d=0, _1w=0, _1mo=0),
        fetched       =0,
        nonfetched    =0,
        non_fetched_by_cause=NonFetchedCause(no_new_data=0, error=0),
        fetch_error   =[]
    ))
    chunks_nb:   int = 0
    chunk_size:  int = 0
    quotes_nb:   int = 0
    dividends_nb:int = 0
    splits_nb:   int = 0
    

