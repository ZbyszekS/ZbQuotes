from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Date
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass



class Fit(Base):
    """     Financial instrument type     """
    __tablename__ = 'fit'

    id          = Column(Integer,     primary_key=True)
    name        = Column(String(45),  nullable=False)
    description = Column(String(255), nullable=True)

    # parent to
    gfis = relationship('Gfi', back_populates='fit')


    def __repr__(self):
        return f"<Fit(id={self.id}, name='{self.name}')>"



class Gfi(Base):
    """     Global financial instrument     """
    __tablename__ = 'gfi'

    id          = Column(Integer,     primary_key=True)
    name        = Column(String(45),  nullable=False)
    description = Column(String(255), nullable=True)

    # child of
    fit = relationship('Fit', back_populates='gfis')

    # parent to
    splits = relationship('Split', back_populates='gfi')
    dividends = relationship('Dividend', back_populates='gfi')

    
    def __repr__(self):
        return f"<Gfi(id={self.id}, name='{self.name}')>"


class Split(Base):
    """     Split     """
    __tablename__ = 'split'

    id          = Column(Integer, primary_key=True)
    gfi_id      = Column(Integer, ForeignKey('gfi.id'))
    split_date  = Column(String(45), nullable=False)
    ratio       = Column(Numeric(10, 4, asdecimal=True), nullable=False)

    # child of
    gfi = relationship('Gfi', back_populates='splits')



class Currency(Base):
    """     Currency     """
    __tablename__ = 'currency'

    id             = Column(Integer,    primary_key=True)
    gfi_id         = Column(Integer,    ForeignKey('gfi.id'))
    symbol         = Column(String(15), nullable=False)
    name           = Column(String(45), nullable=False)
    Numeric_places = Column(Integer)


    # child of (one to one relationship)
    gfi = relationship('Gfi', back_populates='currencies')

    # parent to
    markets = relationship('Market', back_populates='currency')
    ifns    = relationship('Ifn', back_populates='currency')
    dividends = relationship('Dividend', back_populates='currency')

    def __repr__(self):
        return f"<Currency(id={self.id}, symbol='{self.symbol}', name='{self.name}')>"



class Dividend(Base):
    """     Dividend     """
    __tablename__ = 'dividend'

    id            = Column(Integer, primary_key=True)
    gfi_id        = Column(Integer, ForeignKey('gfi.id'))
    currency_id   = Column(Integer, ForeignKey('currency.id'))
    dividend_date = Column(Numeric(10, 4, asdecimal=True), nullable=False)
    amount        = Column(Numeric(10, 4, asdecimal=True), nullable=False)

    # child of
    gfi      = relationship('Gfi', back_populates='dividends')
    currency = relationship('Currency', back_populates='dividends')



class Market(Base):
    """     Market where financial instruments are quoted     """
    __tablename__ = 'market'

    id          = Column(Integer,     primary_key=True)
    name        = Column(String(45),  nullable=False)
    description = Column(String(225), nullable=True)
    abbreviation= Column(String(15))
    currency_id = Column(Integer,     ForeignKey('currency.id'))

    # child of
    currency = relationship('Currency', back_populates='markets')

    # parent of
    ifns = relationship('Ifn', back_populates='market')


    def __repr__(self):
        return f"<Market(id={self.id}, name='{self.name}', currency_id={self.currency_id})>"



class QuotedUnit(Base):
    __tablename__ = 'quoted_unit'

    id                  = Column(Integer, primary_key=True)
    name                = Column(String(45))
    description         = Column(String(225))

    # parent to
    qfis = relationship('Qfi', back_populates='quoted_unit')

    # self-referencing relationships for conversions
    conversions_from = relationship('QutedUnitConversion', foreign_keys='QutedUnitConversion.quoted_unit_from_id', back_populates='quoted_unit_from')
    conversions_to   = relationship('QutedUnitConversion', foreign_keys='QutedUnitConversion.quoted_unit_to_id', back_populates='quoted_unit_to')

    def __repr__(self):
        return f"<QuotedUnit(id={self.id}, name='{self.name}', description='{self.description}')>"



class QutedUnitConversion(Base):
    __tablename__ = 'quoted_unit_conversion'

    id                  = Column(Integer, primary_key=True)
    quoted_unit_from_id = Column(Integer, ForeignKey('quoted_unit.id'))
    quoted_unit_to_id   = Column(Integer, ForeignKey('quoted_unit.id'))
    conversion_factor   = Column(Numeric(10, 4, asdecimal=True), nullable=False)

    # child of
    quoted_unit_from = relationship('QuotedUnit', foreign_keys=[quoted_unit_from_id], back_populates='conversions_from')
    quoted_unit_to   = relationship('QuotedUnit', foreign_keys=[quoted_unit_to_id], back_populates='conversions_to')

    def __repr__(self):
        return f"<QutedUnitConversion(id={self.id}, quoted_unit_from_id={self.quoted_unit_from_id}, quoted_unit_to_id={self.quoted_unit_to_id}, conversion_factor={self.conversion_factor})>"



class Qfi(Base):
    __tablename__ = 'qfi'

    id          = Column(Integer, primary_key=True)

    gfi_id              = Column(Integer, ForeignKey('gfi.id'))
    market_id           = Column(Integer, ForeignKey('market.id'))
    currency_id         = Column(Integer, ForeignKey('currency.id'))
    quoted_unit_id      = Column(Integer, ForeignKey('quoted_unit.id'))

    name                = Column(String(45),  nullable=False)
    description         = Column(String(225), nullable=True)
    quoted_amount       = Column(Integer)                       # amount of unit being quoted
    
    # child of
    gfi       =   relationship('Gfi',        back_populates='qfis')
    market    =   relationship('Market',     back_populates='qfis')
    currency  =   relationship('Currency',   back_populates='qfis')
    quoted_unit = relationship('QuotedUnit', back_populates='qfis')

    # parent of
    ifvs = relationship('Ifv',  back_populates='qfi')
    pips = relationship('Pips', back_populates='qfi')
    
    def __repr__(self):
        return f"<Qfi(id={self.id}, name='{self.name}', description='{self.description}', quoted_amount={self.quoted_amount})>"



class Pips(Base):
    __tablename__ = 'pips'

    id = Column(Integer, primary_key=True)
    qfi_id          = Column(Integer, ForeignKey('qfi.id'))
    date_from       = Column(Date)
    price_precision = Column(Integer)                        # number of decimal places
    pips_value      = Column(Numeric(18, 8, asdecimal=True)) # value of one pip

    # is child of
    qfi = relationship('Qfi', back_populates='pips')


    def __repr__(self):
        return f'Pips(qfi_id={self.qfi_id}, date_from={self.date_from}, price_precision={self.price_precision}, pips_value={self.pips_value})'



class Vendor(Base):
    __tablename__ = 'vendor'

    id                  = Column(Integer, primary_key=True)
    name                = Column(String(45))
    description         = Column(String(225))
    allowed_time_series = Column(String(225))


    # parent to
    vfi = relationship('Vfi', back_populates='vendor')

    def __repr__(self):
        return f"<Vendor(id={self.id}, name='{self.name}', description='{self.description}')>"



class Vfi(Base):
    """     Vendor delivered Financial Instrument    """
    __tablename__ = 'vfi'

    id = Column(Integer, primary_key=True)

    qfi_id         = Column(Integer, ForeignKey('qfi.id'))
    vendor_id = Column(Integer, ForeignKey('vendor.id'))

    name             = Column(String(45))
    symbol           = Column(String(45)) # ticker symbol
    description      = Column(String(225))
    

    # child of
    qfi    = relationship('Qfi',    back_populates='vfi')
    vendor = relationship('Vendor', back_populates='vfi')

    # parent of
    vfi_tss = relationship('VfiTs', back_populates='vfi')

    def __repr__(self):
        return f"<Vfi(id={self.id}, name='{self.name}', symbol='{self.symbol}', description='{self.description}')>"



class Quote_1min(Base):
    __tablename__ = 'quote_1min'

    id        = Column(Integer, primary_key=True)
    vfi_id    = Column(Integer, ForeignKey('vfi.id'))
    timestamp = Column(DateTime)
    open      = Column(Numeric(18, 8, asdecimal=True))
    high      = Column(Numeric(18, 8, asdecimal=True))
    low       = Column(Numeric(18, 8, asdecimal=True))
    close     = Column(Numeric(18, 8, asdecimal=True))
    volume    = Column(Integer)

    # is child of
    vfi = relationship('Vfi', back_populates='quote_1min')

    def __repr__(self):
        return f"<Quote_1min(id={self.id}, vfi_id={self.vfi_id}, timestamp={self.timestamp}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})>"



class Quote_1hour(Base):
    __tablename__ = 'quote_1hour'

    id        = Column(Integer, primary_key=True)
    vfi_id    = Column(Integer, ForeignKey('vfi.id'))
    timestamp = Column(DateTime)
    open      = Column(Numeric(18, 8, asdecimal=True))
    high      = Column(Numeric(18, 8, asdecimal=True))
    low       = Column(Numeric(18, 8, asdecimal=True))
    close     = Column(Numeric(18, 8, asdecimal=True))
    volume    = Column(Integer)

    # is child of
    vfi = relationship('Vfi', back_populates='quote_1hour')

    def __repr__(self):
        return f"<Quote_1hour(id={self.id}, vfi_id={self.vfi_id}, timestamp={self.timestamp}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})>"        



class Quote_1day(Base):
    __tablename__ = 'quote_1day'

    id        = Column(Integer, primary_key=True)
    vfi_id    = Column(Integer, ForeignKey('vfi.id'))
    timestamp = Column(DateTime)
    open      = Column(Numeric(18, 8, asdecimal=True))
    high      = Column(Numeric(18, 8, asdecimal=True))
    low       = Column(Numeric(18, 8, asdecimal=True))
    close     = Column(Numeric(18, 8, asdecimal=True))
    volume    = Column(Integer)

    # is child of
    vfi = relationship('Vfi', back_populates='quote_1day')

    def __repr__(self):
        return f"<Quote_1day(id={self.id}, vfi_id={self.vfi_id}, timestamp={self.timestamp}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})>"        



class Quote_1week(Base):
    __tablename__ = 'quote_1week'

    id        = Column(Integer, primary_key=True)
    vfi_id    = Column(Integer, ForeignKey('vfi.id'))
    timestamp = Column(DateTime)
    open      = Column(Numeric(18, 8, asdecimal=True))
    high      = Column(Numeric(18, 8, asdecimal=True))
    low       = Column(Numeric(18, 8, asdecimal=True))
    close     = Column(Numeric(18, 8, asdecimal=True))
    volume    = Column(Integer)

    # is child of
    vfi = relationship('Vfi', back_populates='quote_1week')

    def __repr__(self):
        return f"<Quote_1week(id={self.id}, vfi_id={self.vfi_id}, timestamp={self.timestamp}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})>"        


class Quote_1month(Base):
    __tablename__ = 'quote_1month'

    id        = Column(Integer, primary_key=True)
    vfi_id    = Column(Integer, ForeignKey('vfi.id'))
    timestamp = Column(DateTime)
    open      = Column(Numeric(18, 8, asdecimal=True))
    high      = Column(Numeric(18, 8, asdecimal=True))
    low       = Column(Numeric(18, 8, asdecimal=True))
    close     = Column(Numeric(18, 8, asdecimal=True))
    volume    = Column(Integer)

    # is child of
    vfi = relationship('Vfi', back_populates='quote_1month')

    def __repr__(self):
        return f"<Quote_1month(id={self.id}, vfi_id={self.vfi_id}, timestamp={self.timestamp}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})>"        


