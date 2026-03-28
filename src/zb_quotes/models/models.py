# This is the models file for the ZbQuotes database
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Numeric, DateTime, Date, MetaData, UniqueConstraint, Boolean

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


class Fit(Base):
    """     Financial instrument type     """
    __tablename__ = 'fit'

    id:          Mapped[int]        = mapped_column(primary_key=True)
    name:        Mapped[str]        = mapped_column(String(45))
    description: Mapped[str | None] = mapped_column(String(255))
    
    # parent to
    gfis: Mapped[list["Gfi"]] = relationship(back_populates='fit')

    def __repr__(self):
        return f"<Fit(id={self.id}, name='{self.name}')>"


class Sector(Base):
    """ Economic sector or industry classification """
    __tablename__ = 'sector'

    id:          Mapped[int]        = mapped_column(primary_key=True)
    name:        Mapped[str]        = mapped_column(String(45), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    # parent to
    gfis: Mapped[list["Gfi"]] = relationship(back_populates='sector')
    industries: Mapped[list["Industry"]] = relationship(back_populates='sector')

    def __repr__(self):
        return f"<Sector(id={self.id}, name='{self.name}')>"

class Industry(Base):
    """ Industry classification """
    __tablename__ = 'industry'

    id:          Mapped[int]        = mapped_column(primary_key=True)
    sector_id:   Mapped[int]        = mapped_column(ForeignKey('sector.id'))

    name:        Mapped[str]        = mapped_column(String(45), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    # parent to ------------------------------------------------------
    gfis: Mapped[list["Gfi"]] = relationship(back_populates='industry')
    
    # child of
    sector: Mapped["Sector"] = relationship(back_populates='industries')

    def __repr__(self):
        return f"<Industry(id={self.id}, name='{self.name}')>"


class Country(Base):
    """ Country or region classification """
    __tablename__ = 'country'

    id:          Mapped[int]        = mapped_column(primary_key=True)
    iso_code_2:  Mapped[str]        = mapped_column(String(2), unique=True)
    name:        Mapped[str]        = mapped_column(String(45), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))
    region:      Mapped[str | None] = mapped_column(String(45))
    subregion:   Mapped[str | None] = mapped_column(String(45))

    # parent to ------------------------------------------------------
    gfis: Mapped[list["Gfi"]] = relationship(back_populates='country')

    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.name}')>"


class Gfi(Base):
    """     Global financial instrument     """
    __tablename__ = 'gfi'

    id:          Mapped[int]        = mapped_column(primary_key=True)
    fit_id:      Mapped[int]        = mapped_column(ForeignKey('fit.id'))
    sector_id:   Mapped[int | None] = mapped_column(ForeignKey('sector.id'))
    industry_id: Mapped[int | None] = mapped_column(ForeignKey('industry.id'))
    country_id:  Mapped[int | None] = mapped_column(ForeignKey('country.id'))

    isin:        Mapped[str | None] = mapped_column(String(12))
    name:        Mapped[str]        = mapped_column(String(45), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))
    ticker_go:   Mapped[str | None] = mapped_column(String(45))
    ticker_bl:   Mapped[str | None] = mapped_column(String(45))
    ticker_yf:   Mapped[str | None] = mapped_column(String(45))
    

    # child of ------------------------------------------------------
    fit:      Mapped["Fit"]      = relationship(back_populates='gfis')
    sector:   Mapped["Sector"]   = relationship(back_populates='gfis')
    industry: Mapped["Industry"] = relationship(back_populates='gfis')
    country:  Mapped["Country"]  = relationship(back_populates='gfis')
    
    # parent to ------------------------------------------------------
    splits:             Mapped[list["Split"]]    = relationship(back_populates='gfi')
    dividends:          Mapped[list["Dividend"]] = relationship("Dividend", foreign_keys="[Dividend.gfi_id]",      back_populates='gfi')
    dividends_currency: Mapped[list["Dividend"]] = relationship("Dividend", foreign_keys="[Dividend.currency_id]", back_populates='currency')
    qfis:               Mapped[list["Qfi"]]      = relationship("Qfi", foreign_keys="[Qfi.gfi_id]",      back_populates="gfi")
    qfis_as_currency:   Mapped[list["Qfi"]]      = relationship("Qfi", foreign_keys="[Qfi.currency_id]", back_populates="currency_gfi")
    markets:            Mapped[list["Market"]]   = relationship(back_populates='currency')
    
    # parent to: one to one relationships
    currency_details: Mapped["CurrencyDetails"] = relationship(back_populates='gfi', uselist=False)
    fundamentals:     Mapped["GfiFundamentals"] = relationship(back_populates='gfi', uselist=False)
    
    def __repr__(self):
        return f"<Gfi(id={self.id}, name='{self.name}')>"



class GfiFundamentals(Base):
    """Periodically refreshed fundamentals from data vendors."""
    __tablename__ = 'gfi_fundamentals'

    id:                    Mapped[int]          = mapped_column(primary_key=True)
    gfi_id:                Mapped[int]          = mapped_column(ForeignKey('gfi.id'), unique=True)
    
    # Size / valuation
    shares_outstanding:    Mapped[int | None]     = mapped_column()
    last_price:            Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    market_cap:            Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    
    
    # Fundamentals
    pe:                    Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    pe_forward:            Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    eps:                   Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    eps_forward:           Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    book_value_per_share:  Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    p_bv:                  Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    total_revenue:         Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    beta:                  Mapped[Decimal | None] = mapped_column(Numeric( 8, 4))
    
    # Dividends
    dividend_yield:        Mapped[Decimal | None] = mapped_column(Numeric(8, 6))
    last_dividend_amount:  Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    last_dividend_date:    Mapped[date | None]    = mapped_column(Date)
    
    # Price range (summary, not daily)
    week_52_high:          Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    week_52_low:           Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    
    # Meta
    updated_at:            Mapped[datetime]       = mapped_column(DateTime)
    source_vendor:         Mapped[str | None]     = mapped_column(String(45))

    # child of (one-to-one)
    gfi: Mapped["Gfi"] = relationship(back_populates='fundamentals', uselist=False)



class Split(Base):
    """     Split     """
    __tablename__ = 'split'

    id:          Mapped[int]      = mapped_column(primary_key=True)
    gfi_id:      Mapped[int]      = mapped_column(ForeignKey('gfi.id'))
    split_date:  Mapped[datetime] = mapped_column(DateTime)
    ratio:       Mapped[Decimal]  = mapped_column(Numeric(10, 4, asdecimal=True))

    # child of
    gfi: Mapped["Gfi"] = relationship(back_populates='splits')



class CurrencyDetails(Base):
    """     Currency details     """
    __tablename__ = 'currency_details'

    id:          Mapped[int]    = mapped_column(primary_key=True)
    gfi_id:      Mapped[int]    = mapped_column(ForeignKey('gfi.id'))
    symbol:      Mapped[str]    = mapped_column(String(15))
    code:        Mapped[str]    = mapped_column(String(15))
    name:        Mapped[str]    = mapped_column(String(45))
    decimal_places: Mapped[int] = mapped_column()

    # child of (one to one relationship)
    gfi: Mapped["Gfi"] = relationship(back_populates='currency_details')


    def __repr__(self):
        return f"<Currency(id={self.id}, symbol='{self.symbol}', name='{self.name}')>"



class Dividend(Base):
    """     Dividend     """
    __tablename__ = 'dividend'

    id:            Mapped[int]      = mapped_column(primary_key=True)
    gfi_id:        Mapped[int]      = mapped_column(ForeignKey('gfi.id'))
    currency_id:   Mapped[int]      = mapped_column(ForeignKey('gfi.id'))
    dividend_date: Mapped[datetime] = mapped_column(DateTime)
    amount:        Mapped[Decimal]  = mapped_column(Numeric(10, 4, asdecimal=True))

    # child of ------------------------------------------------------
    gfi:      Mapped["Gfi"] = relationship(back_populates='dividends', foreign_keys=[gfi_id])
    currency: Mapped["Gfi"] = relationship(back_populates='dividends_currency', foreign_keys=[currency_id])



class Market(Base):
    """     Market where financial instruments are quoted     """
    __tablename__ = 'market'

    id:           Mapped[int]        = mapped_column(primary_key=True)
    currency_id:  Mapped[int]        = mapped_column(ForeignKey('gfi.id'))
    mic:          Mapped[str]        = mapped_column(String(4)) # four-character alphanumeric code defined by the ISO 10383 standard
    name:         Mapped[str]        = mapped_column(String(45))
    description:  Mapped[str | None] = mapped_column(String(225))
    abbreviation: Mapped[str]        = mapped_column(String(15))

    # child of ------------------------------------------------------
    currency: Mapped["Gfi"] = relationship(back_populates='markets')

    # parent of ------------------------------------------------------
    qfis: Mapped[list["Qfi"]] = relationship(back_populates='market')


    def __repr__(self):
        return f"<Market(id={self.id}, name='{self.name}', currency_id={self.currency_id})>"



class QuotedUnit(Base):
    __tablename__ = 'quoted_unit'

    id:           Mapped[int]        = mapped_column(primary_key=True)
    name:         Mapped[str]        = mapped_column(String(45))
    description:  Mapped[str | None] = mapped_column(String(225))
    symbol:       Mapped[str | None] = mapped_column(String(10))

    # parent to ------------------------------------------------------
    qfis: Mapped["Qfi"] = relationship(back_populates='quoted_unit')

    # self-referencing relationships for conversions ------------------------------------------------------
    conversions_from: Mapped[list["QuotedUnitConversion"]] = relationship(foreign_keys='QuotedUnitConversion.quoted_unit_from_id', back_populates='quoted_unit_from')
    conversions_to:   Mapped[list["QuotedUnitConversion"]] = relationship(foreign_keys='QuotedUnitConversion.quoted_unit_to_id',   back_populates='quoted_unit_to')

    def __repr__(self):
        return f"<QuotedUnit(id={self.id}, name='{self.name}', description='{self.description}')>"



class QuotedUnitConversion(Base):
    __tablename__ = 'quoted_unit_conversion'

    id:                  Mapped[int] = mapped_column(primary_key=True)
    quoted_unit_from_id: Mapped[int] = mapped_column(ForeignKey('quoted_unit.id'))
    quoted_unit_to_id:   Mapped[int] = mapped_column(ForeignKey('quoted_unit.id'))
    conversion_factor:   Mapped[Decimal] = mapped_column(Numeric(10, 4, asdecimal=True), nullable=False)

    # child of ------------------------------------------------------
    quoted_unit_from: Mapped["QuotedUnit"] = relationship(foreign_keys=[quoted_unit_from_id], back_populates='conversions_from')
    quoted_unit_to:   Mapped["QuotedUnit"] = relationship(foreign_keys=[quoted_unit_to_id], back_populates='conversions_to')

    def __repr__(self):
        return f"<QuotedUnitConversion(id={self.id}, quoted_unit_from_id={self.quoted_unit_from_id}, quoted_unit_to_id={self.quoted_unit_to_id}, conversion_factor={self.conversion_factor})>"



class Qfi(Base):
    __tablename__ = 'qfi'

    id:          Mapped[int] = mapped_column(primary_key=True)

    gfi_id:              Mapped[int] = mapped_column(ForeignKey('gfi.id'))
    market_id:           Mapped[int] = mapped_column(ForeignKey('market.id'))
    currency_id:         Mapped[int] = mapped_column(ForeignKey('gfi.id'))
    quoted_unit_id:      Mapped[int] = mapped_column(ForeignKey('quoted_unit.id'))

    name:                Mapped[str]        = mapped_column(String(45), unique=True)
    description:         Mapped[str | None] = mapped_column(String(225))
    quoted_amount:       Mapped[int]        = mapped_column()                       # amount of unit being quoted
    
    # child of -------------------
    gfi:          Mapped["Gfi"] = relationship("Gfi", foreign_keys=[gfi_id],      back_populates='qfis')
    currency_gfi: Mapped["Gfi"] = relationship("Gfi", foreign_keys=[currency_id], back_populates='qfis_as_currency')
    market:       Mapped["Market"]     = relationship(back_populates='qfis')
    quoted_unit:  Mapped["QuotedUnit"] = relationship(back_populates='qfis')

    # parent of -------------------
    vfis:  Mapped[list["Vfi"]]  = relationship(back_populates='qfi')
    pipss: Mapped[list["Pips"]] = relationship(back_populates='qfi')
    
    def __repr__(self):
        return f"<Qfi(id={self.id}, name='{self.name}', description='{self.description}', quoted_amount={self.quoted_amount})>"



class Pips(Base):
    __tablename__ = 'pips'

    id:              Mapped[int] = mapped_column(primary_key=True)
    qfi_id:          Mapped[int] = mapped_column(ForeignKey('qfi.id'))
    date_from:       Mapped[date] = mapped_column(Date)
    price_precision: Mapped[int] = mapped_column()                        # number of decimal places
    pips_value:      Mapped[Decimal] = mapped_column(Numeric(18, 8, asdecimal=True)) # value of one pip

    # child of ------------------------------------------------------
    qfi: Mapped["Qfi"] = relationship(back_populates='pipss')


    def __repr__(self):
        return f'Pips(qfi_id={self.qfi_id}, date_from={self.date_from}, price_precision={self.price_precision}, pips_value={self.pips_value})'



class Vendor(Base):
    __tablename__ = 'vendor'

    id:                  Mapped[int]        = mapped_column(primary_key=True)
    name:                Mapped[str]        = mapped_column(String(45))
    description:         Mapped[str | None] = mapped_column(String(225))
    allowed_time_series: Mapped[str]        = mapped_column(String(225))

    # parent to
    vfis: Mapped[list["Vfi"]] = relationship(back_populates='vendor')

    def __repr__(self):
        return f"<Vendor(id={self.id}, name='{self.name}', description='{self.description}')>"



class Vfi(Base):
    """     Vendor delivered Financial Instrument    """
    __tablename__ = 'vfi'

    id:            Mapped[int]        = mapped_column(primary_key=True)
    qfi_id:        Mapped[int]        = mapped_column(ForeignKey('qfi.id'))
    vendor_id:     Mapped[int]        = mapped_column(ForeignKey('vendor.id'))
    vendor_ticker: Mapped[str]        = mapped_column(String(45)) # ticker symbol
    name:          Mapped[str]        = mapped_column(String(45), unique=True)
    description:   Mapped[str | None] = mapped_column(String(225))

    # child of ------------------------------------------------------
    qfi:    Mapped["Qfi"]    = relationship(back_populates='vfis')
    vendor: Mapped["Vendor"] = relationship(back_populates='vfis')


    vfi_time_series:  Mapped[list["VfiTimeSeries"]] = relationship(back_populates='vfi')
    
    def __repr__(self):
        return f"<Vfi(id={self.id}, name='{self.name}', symbol='{self.symbol}', description='{self.description}')>"



class Timeframe(Base):
    __tablename__ = 'timeframe'

    id:      Mapped[int]        = mapped_column(primary_key=True)
    code:    Mapped[str]        = mapped_column(String(10), unique=True)           # 1m, 5m, 1h, 1d, 1w, 1M
    seconds: Mapped[int | None] = mapped_column()                        # None for 1w, 1M, …
    name:    Mapped[str]        = mapped_column(String(30), nullable=False)        # "1 Minute", "Daily", …
    
    is_intraday:    Mapped[bool] = mapped_column(default=False)          # more conservative default
    is_aggregatable:Mapped[bool] = mapped_column(default=True)

    # You may also consider adding:
    # typical_bars_per_day: Mapped[int | None]     # helps UI/validation
    # display_priority: Mapped[int]                # for sorting in dropdowns
    
    # parent to:
    vfi_time_series: Mapped[list["VfiTimeSeries"]] = relationship(back_populates='timeframe')


class VfiTimeSeries(Base):
    """
    Controls which time series are collected for a given Vfi,
    and tracks the state of each import.
    """
    __tablename__ = 'vfi_time_series'

    id:           Mapped[int] = mapped_column(primary_key=True)
    vfi_id:       Mapped[int] = mapped_column(ForeignKey('vfi.id'))
    timeframe_id: Mapped[int] = mapped_column(ForeignKey('timeframe.id'))
    
    # import control
    enabled:      Mapped[bool]       = mapped_column(Boolean, default=False)
    history_days: Mapped[int | None] = mapped_column()   # how far back to fetch

    # import state tracking
    last_imported_at:  Mapped[datetime | None] = mapped_column(DateTime)
    last_imported_from:Mapped[date     | None] = mapped_column(Date)
    last_imported_to:  Mapped[date     | None] = mapped_column(Date)

    __table_args__ = (
        UniqueConstraint('vfi_id', 'timeframe_id'),
    )

    # child of ------------------------------------------------------
    vfi:       Mapped["Vfi"]       = relationship(back_populates='vfi_time_series')
    timeframe: Mapped["Timeframe"] = relationship(back_populates='vfi_time_series')

    # parent to ------------------------------------------------------
    quote_1mins:    Mapped[list["Quote_1min"]]   = relationship(back_populates='vfi_time_series')
    quote_1hours:   Mapped[list["Quote_1hour"]]  = relationship(back_populates='vfi_time_series')
    quote_1days:    Mapped[list["Quote_1day"]]   = relationship(back_populates='vfi_time_series')
    quote_1weeks:   Mapped[list["Quote_1week"]]  = relationship(back_populates='vfi_time_series')
    quote_1months:  Mapped[list["Quote_1month"]] = relationship(back_populates='vfi_time_series')



# --- Mixins for cleaner code ---
class QuoteMixin:
    """Standard columns for all quote tables"""
    id:        Mapped[int]        = mapped_column(primary_key=True)
    open:      Mapped[float]      = mapped_column(Numeric(18, 8))
    high:      Mapped[float]      = mapped_column(Numeric(18, 8))
    low:       Mapped[float]      = mapped_column(Numeric(18, 8))
    close:     Mapped[float]      = mapped_column(Numeric(18, 8))
    volume:    Mapped[int | None] = mapped_column()
    
    @classmethod
    def __declare_last__(cls):
        # Ensures one quote per timestamp per VFI
        cls.__table__.append_constraint(
            UniqueConstraint('vfi_time_series_id', 'timestamp' if hasattr(cls, 'timestamp') else 'q_date')
            # UniqueConstraint('vfi_id', 'timestamp' if hasattr(cls, 'timestamp') else 'q_date')
        )


class Quote_1min(Base, QuoteMixin):
    __tablename__ = 'quote_1min'

    timestamp: Mapped[DateTime] = mapped_column(DateTime, index=True)
    # vfi_id:    Mapped[int]      = mapped_column(ForeignKey('vfi.id'))
    vfi_time_series_id: Mapped[int] = mapped_column(ForeignKey('vfi_time_series.id'))
    
    # child of ------------------------------------------------------
    vfi_time_series: Mapped["VfiTimeSeries"] = relationship(back_populates='quote_1mins')

    def __repr__(self):
        return f"<Quote_1min(id={self.id}, vfi_id={self.vfi_id}, timestamp={self.timestamp}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})>"



class Quote_1hour(Base, QuoteMixin):
    __tablename__ = 'quote_1hour'

    timestamp: Mapped[DateTime] = mapped_column(DateTime, index=True)
    # vfi_id: Mapped[int] = mapped_column(ForeignKey('vfi.id'))
    vfi_time_series_id: Mapped[int] = mapped_column(ForeignKey('vfi_time_series.id'))
    
    # child of ------------------------------------------------------
    vfi_time_series: Mapped["VfiTimeSeries"] = relationship(back_populates='quote_1hours')

    def __repr__(self):
        return f"<Quote_1hour(id={self.id}, vfi_id={self.vfi_id}, timestamp={self.timestamp}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})>"        



class Quote_1day(Base, QuoteMixin):
    __tablename__ = 'quote_1day'

    q_date: Mapped[Date] = mapped_column(Date, index=True)
    # vfi_id: Mapped[int]  = mapped_column(ForeignKey('vfi.id'))
    vfi_time_series_id: Mapped[int] = mapped_column(ForeignKey('vfi_time_series.id'))
    
    # child of ------------------------------------------------------
    vfi_time_series: Mapped["VfiTimeSeries"] = relationship(back_populates='quote_1days')

    def __repr__(self):
        return f"<Quote_1day(id={self.id}, vfi_id={self.vfi_id}, timestamp={self.q_date}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})>"        
    


class Quote_1week(Base, QuoteMixin):
    __tablename__ = 'quote_1week'

    q_date: Mapped[Date] = mapped_column(Date, index=True)
    # vfi_id: Mapped[int]  = mapped_column(ForeignKey('vfi.id'))
    vfi_time_series_id: Mapped[int] = mapped_column(ForeignKey('vfi_time_series.id'))
    
    # child of ------------------------------------------------------
    vfi_time_series: Mapped["VfiTimeSeries"] = relationship(back_populates='quote_1weeks')

    def __repr__(self):
        return f"<Quote_1week(id={self.id}, vfi_id={self.vfi_id}, q_date={self.q_date}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})>"        
    


class Quote_1month(Base, QuoteMixin):
    __tablename__ = 'quote_1month'

    q_date: Mapped[Date] = mapped_column(Date, index=True)
    # vfi_id: Mapped[int]  = mapped_column(ForeignKey('vfi.id'))
    vfi_time_series_id: Mapped[int] = mapped_column(ForeignKey('vfi_time_series.id'))
    
    # child of ------------------------------------------------------
    vfi_time_series: Mapped["VfiTimeSeries"] = relationship(back_populates='quote_1months')

    def __repr__(self):
        return f"<Quote_1month(id={self.id}, vfi_id={self.vfi_id}, q_date={self.q_date}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})>"        
    

