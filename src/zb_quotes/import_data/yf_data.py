# Data classes for yfinance

from dataclasses import dataclass, field


###############################################################
#                    supporting classes
###############################################################
@dataclass(frozen=True)
class YfDownloadCondition:
    interval: str      = "1d"
    
    period: str | None = None
    
    start: str | None  = None
    end: str | None    = None

    auto_adjust: bool  = False
    actions: bool      = True
    repair: bool       = False
    group_by: str      = "ticker"
    
    def __str__(self) -> str:
        """Return human-readable string representation"""
        parts = []
        if self.period:
            parts.append(f"period={self.period}")
        if self.start:
            parts.append(f"start={self.start}")
        if self.end:
            parts.append(f"end={self.end}")
        
        base = f"YfDownloadCondition(interval={self.interval}"
        return f"{base}({', '.join(parts)})" if parts else base
    
    def __repr__(self) -> str:
        """Return detailed string representation for debugging"""
        return (f"YfDownloadCondition(interval={self.interval!r}, "
                f"period={self.period!r}, "
                f"start={self.start!r}, "
                f"end={self.end!r}, "
                f"auto_adjust={self.auto_adjust!r}, "
                f"actions={self.actions!r}, "
                f"repair={self.repair!r}, "
                f"group_by={self.group_by!r})")

###############################################################
#                    MAIN CLASS
###############################################################
@dataclass
class YfDownloadInput:
    condition: YfDownloadCondition = field(default_factory=YfDownloadCondition)
    tickers:   list[str]           = field(default_factory=list)

    
