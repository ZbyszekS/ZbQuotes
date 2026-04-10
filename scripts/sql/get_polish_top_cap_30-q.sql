Write SQL select statement choosing form Gfi table records for instruments which:
country_id = 227
they are in top 30% in context of capitalization for given country
--
-- File generated with SQLiteStudio v3.4.21 on Wed Apr 8 20:27:51 2026
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: alembic_version
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR (32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (
        version_num
    )
);


-- Table: country
CREATE TABLE IF NOT EXISTS country (
    id          INTEGER       NOT NULL,
    iso_code_2  VARCHAR (2)   NOT NULL,
    name        VARCHAR (45)  NOT NULL,
    description VARCHAR (255),
    region      VARCHAR (45),
    subregion   VARCHAR (45),
    CONSTRAINT pk_country PRIMARY KEY (
        id
    ),
    CONSTRAINT uq_country_iso_code_2 UNIQUE (
        iso_code_2
    ),
    CONSTRAINT uq_country_name UNIQUE (
        name
    )
);


-- Table: currency_details
CREATE TABLE IF NOT EXISTS currency_details (
    id             INTEGER      NOT NULL,
    gfi_id         INTEGER      NOT NULL,
    symbol         VARCHAR (15) NOT NULL,
    code           VARCHAR (15) NOT NULL,
    name           VARCHAR (45) NOT NULL,
    decimal_places INTEGER      NOT NULL,
    CONSTRAINT pk_currency_details PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_currency_details_gfi_id_gfi FOREIGN KEY (
        gfi_id
    )
    REFERENCES gfi (id) 
);


-- Table: dividend
CREATE TABLE IF NOT EXISTS dividend (
    id            INTEGER         NOT NULL,
    gfi_id        INTEGER         NOT NULL,
    currency_id   INTEGER         NOT NULL,
    dividend_date DATETIME        NOT NULL,
    amount        NUMERIC (10, 4) NOT NULL,
    CONSTRAINT pk_dividend PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_dividend_currency_id_gfi FOREIGN KEY (
        currency_id
    )
    REFERENCES gfi (id),
    CONSTRAINT fk_dividend_gfi_id_gfi FOREIGN KEY (
        gfi_id
    )
    REFERENCES gfi (id),
    CONSTRAINT uq_dividend_entry UNIQUE (
        gfi_id,
        dividend_date,
        amount
    )
);


-- Table: fit
CREATE TABLE IF NOT EXISTS fit (
    id          INTEGER       NOT NULL,
    name        VARCHAR (45)  NOT NULL,
    description VARCHAR (255),
    CONSTRAINT pk_fit PRIMARY KEY (
        id
    )
);


-- Table: gfi
CREATE TABLE IF NOT EXISTS gfi (
    id          INTEGER       NOT NULL,
    fit_id      INTEGER       NOT NULL,
    sector_id   INTEGER,
    industry_id INTEGER,
    country_id  INTEGER,
    isin        VARCHAR (12),
    name        VARCHAR (45)  NOT NULL,
    description VARCHAR (255),
    ticker_go   VARCHAR (45),
    ticker_bl   VARCHAR (45),
    ticker_yf   VARCHAR (45),
    CONSTRAINT pk_gfi PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_gfi_country_id_country FOREIGN KEY (
        country_id
    )
    REFERENCES country (id),
    CONSTRAINT fk_gfi_fit_id_fit FOREIGN KEY (
        fit_id
    )
    REFERENCES fit (id),
    CONSTRAINT fk_gfi_industry_id_industry FOREIGN KEY (
        industry_id
    )
    REFERENCES industry (id),
    CONSTRAINT fk_gfi_sector_id_sector FOREIGN KEY (
        sector_id
    )
    REFERENCES sector (id),
    CONSTRAINT uq_gfi_name UNIQUE (
        name
    )
);


-- Table: gfi_fundamentals
CREATE TABLE IF NOT EXISTS gfi_fundamentals (
    id                   INTEGER         NOT NULL,
    gfi_id               INTEGER         NOT NULL,
    shares_outstanding   INTEGER,
    last_price           NUMERIC (18, 4),
    market_cap           NUMERIC (18, 4),
    pe                   NUMERIC (10, 4),
    pe_forward           NUMERIC (10, 4),
    eps                  NUMERIC (10, 4),
    eps_forward          NUMERIC (10, 4),
    book_value_per_share NUMERIC (10, 4),
    p_bv                 NUMERIC (10, 4),
    total_revenue        NUMERIC (18, 4),
    beta                 NUMERIC (8, 4),
    dividend_yield       NUMERIC (8, 6),
    last_dividend_amount NUMERIC (10, 4),
    last_dividend_date   DATE,
    week_52_high         NUMERIC (18, 4),
    week_52_low          NUMERIC (18, 4),
    updated_at           DATETIME        NOT NULL,
    source_vendor        VARCHAR (45),
    CONSTRAINT pk_gfi_fundamentals PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_gfi_fundamentals_gfi_id_gfi FOREIGN KEY (
        gfi_id
    )
    REFERENCES gfi (id),
    CONSTRAINT uq_gfi_fundamentals_gfi_id UNIQUE (
        gfi_id
    )
);


-- Table: industry
CREATE TABLE IF NOT EXISTS industry (
    id          INTEGER       NOT NULL,
    sector_id   INTEGER       NOT NULL,
    name        VARCHAR (45)  NOT NULL,
    description VARCHAR (255),
    CONSTRAINT pk_industry PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_industry_sector_id_sector FOREIGN KEY (
        sector_id
    )
    REFERENCES sector (id),
    CONSTRAINT uq_industry_name UNIQUE (
        name
    )
);


-- Table: market
CREATE TABLE IF NOT EXISTS market (
    id           INTEGER       NOT NULL,
    currency_id  INTEGER       NOT NULL,
    mic          VARCHAR (4)   NOT NULL,
    name         VARCHAR (45)  NOT NULL,
    description  VARCHAR (225),
    abbreviation VARCHAR (15)  NOT NULL,
    CONSTRAINT pk_market PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_market_currency_id_gfi FOREIGN KEY (
        currency_id
    )
    REFERENCES gfi (id) 
);


-- Table: pips
CREATE TABLE IF NOT EXISTS pips (
    id              INTEGER         NOT NULL,
    qfi_id          INTEGER         NOT NULL,
    date_from       DATE            NOT NULL,
    price_precision INTEGER         NOT NULL,
    pips_value      NUMERIC (18, 8) NOT NULL,
    CONSTRAINT pk_pips PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_pips_qfi_id_qfi FOREIGN KEY (
        qfi_id
    )
    REFERENCES qfi (id) 
);


-- Table: qfi
CREATE TABLE IF NOT EXISTS qfi (
    id             INTEGER       NOT NULL,
    gfi_id         INTEGER       NOT NULL,
    market_id      INTEGER       NOT NULL,
    currency_id    INTEGER       NOT NULL,
    quoted_unit_id INTEGER       NOT NULL,
    name           VARCHAR (45)  NOT NULL,
    description    VARCHAR (225),
    quoted_amount  INTEGER       NOT NULL,
    CONSTRAINT pk_qfi PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_qfi_currency_id_gfi FOREIGN KEY (
        currency_id
    )
    REFERENCES gfi (id),
    CONSTRAINT fk_qfi_gfi_id_gfi FOREIGN KEY (
        gfi_id
    )
    REFERENCES gfi (id),
    CONSTRAINT fk_qfi_market_id_market FOREIGN KEY (
        market_id
    )
    REFERENCES market (id),
    CONSTRAINT fk_qfi_quoted_unit_id_quoted_unit FOREIGN KEY (
        quoted_unit_id
    )
    REFERENCES quoted_unit (id),
    CONSTRAINT uq_qfi_name UNIQUE (
        name
    )
);


-- Table: quote_1day
CREATE TABLE IF NOT EXISTS quote_1day (
    q_date             DATE            NOT NULL,
    vfi_time_series_id INTEGER         NOT NULL,
    id                 INTEGER         NOT NULL,
    open               NUMERIC (18, 8) NOT NULL,
    high               NUMERIC (18, 8) NOT NULL,
    low                NUMERIC (18, 8) NOT NULL,
    close              NUMERIC (18, 8) NOT NULL,
    volume             INTEGER,
    adj_close          NUMERIC (18, 8),
    CONSTRAINT pk_quote_1day PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_quote_1day_vfi_time_series_id_vfi_time_series FOREIGN KEY (
        vfi_time_series_id
    )
    REFERENCES vfi_time_series (id),
    CONSTRAINT uq_quote_1day_vfi_ts_date UNIQUE (
        vfi_time_series_id,
        q_date
    )
);


-- Table: quote_1hour
CREATE TABLE IF NOT EXISTS quote_1hour (
    timestamp          DATETIME        NOT NULL,
    vfi_time_series_id INTEGER         NOT NULL,
    id                 INTEGER         NOT NULL,
    open               NUMERIC (18, 8) NOT NULL,
    high               NUMERIC (18, 8) NOT NULL,
    low                NUMERIC (18, 8) NOT NULL,
    close              NUMERIC (18, 8) NOT NULL,
    volume             INTEGER,
    adj_close          NUMERIC (18, 8),
    CONSTRAINT pk_quote_1hour PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_quote_1hour_vfi_time_series_id_vfi_time_series FOREIGN KEY (
        vfi_time_series_id
    )
    REFERENCES vfi_time_series (id),
    CONSTRAINT uq_quote_1hour_vfi_ts_timestamp UNIQUE (
        vfi_time_series_id,
        timestamp
    )
);


-- Table: quote_1min
CREATE TABLE IF NOT EXISTS quote_1min (
    timestamp          DATETIME        NOT NULL,
    vfi_time_series_id INTEGER         NOT NULL,
    id                 INTEGER         NOT NULL,
    open               NUMERIC (18, 8) NOT NULL,
    high               NUMERIC (18, 8) NOT NULL,
    low                NUMERIC (18, 8) NOT NULL,
    close              NUMERIC (18, 8) NOT NULL,
    volume             INTEGER,
    adj_close          NUMERIC (18, 8),
    CONSTRAINT pk_quote_1min PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_quote_1min_vfi_time_series_id_vfi_time_series FOREIGN KEY (
        vfi_time_series_id
    )
    REFERENCES vfi_time_series (id),
    CONSTRAINT uq_quote_1min_vfi_ts_timestamp UNIQUE (
        vfi_time_series_id,
        timestamp
    )
);


-- Table: quote_1month
CREATE TABLE IF NOT EXISTS quote_1month (
    q_date             DATE            NOT NULL,
    vfi_time_series_id INTEGER         NOT NULL,
    id                 INTEGER         NOT NULL,
    open               NUMERIC (18, 8) NOT NULL,
    high               NUMERIC (18, 8) NOT NULL,
    low                NUMERIC (18, 8) NOT NULL,
    close              NUMERIC (18, 8) NOT NULL,
    volume             INTEGER,
    adj_close          NUMERIC (18, 8),
    CONSTRAINT pk_quote_1month PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_quote_1month_vfi_time_series_id_vfi_time_series FOREIGN KEY (
        vfi_time_series_id
    )
    REFERENCES vfi_time_series (id),
    CONSTRAINT uq_quote_1month_vfi_ts_date UNIQUE (
        vfi_time_series_id,
        q_date
    )
);


-- Table: quote_1week
CREATE TABLE IF NOT EXISTS quote_1week (
    q_date             DATE            NOT NULL,
    vfi_time_series_id INTEGER         NOT NULL,
    id                 INTEGER         NOT NULL,
    open               NUMERIC (18, 8) NOT NULL,
    high               NUMERIC (18, 8) NOT NULL,
    low                NUMERIC (18, 8) NOT NULL,
    close              NUMERIC (18, 8) NOT NULL,
    volume             INTEGER,
    adj_close          NUMERIC (18, 8),
    CONSTRAINT pk_quote_1week PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_quote_1week_vfi_time_series_id_vfi_time_series FOREIGN KEY (
        vfi_time_series_id
    )
    REFERENCES vfi_time_series (id),
    CONSTRAINT uq_quote_1week_vfi_ts_date UNIQUE (
        vfi_time_series_id,
        q_date
    )
);


-- Table: quoted_unit
CREATE TABLE IF NOT EXISTS quoted_unit (
    id          INTEGER       NOT NULL,
    name        VARCHAR (45)  NOT NULL,
    description VARCHAR (225),
    symbol      VARCHAR (10),
    CONSTRAINT pk_quoted_unit PRIMARY KEY (
        id
    )
);


-- Table: quoted_unit_conversion
CREATE TABLE IF NOT EXISTS quoted_unit_conversion (
    id                  INTEGER         NOT NULL,
    quoted_unit_from_id INTEGER         NOT NULL,
    quoted_unit_to_id   INTEGER         NOT NULL,
    conversion_factor   NUMERIC (10, 4) NOT NULL,
    CONSTRAINT pk_quoted_unit_conversion PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_quoted_unit_conversion_quoted_unit_from_id_quoted_unit FOREIGN KEY (
        quoted_unit_from_id
    )
    REFERENCES quoted_unit (id),
    CONSTRAINT fk_quoted_unit_conversion_quoted_unit_to_id_quoted_unit FOREIGN KEY (
        quoted_unit_to_id
    )
    REFERENCES quoted_unit (id) 
);


-- Table: sector
CREATE TABLE IF NOT EXISTS sector (
    id          INTEGER       NOT NULL,
    name        VARCHAR (45)  NOT NULL,
    description VARCHAR (255),
    CONSTRAINT pk_sector PRIMARY KEY (
        id
    ),
    CONSTRAINT uq_sector_name UNIQUE (
        name
    )
);


-- Table: split
CREATE TABLE IF NOT EXISTS split (
    id         INTEGER         NOT NULL,
    gfi_id     INTEGER         NOT NULL,
    split_date DATETIME        NOT NULL,
    ratio      NUMERIC (10, 4) NOT NULL,
    CONSTRAINT pk_split PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_split_gfi_id_gfi FOREIGN KEY (
        gfi_id
    )
    REFERENCES gfi (id),
    CONSTRAINT uq_split_entry UNIQUE (
        gfi_id,
        split_date,
        ratio
    )
);


-- Table: timeframe
CREATE TABLE IF NOT EXISTS timeframe (
    id              INTEGER      NOT NULL,
    code            VARCHAR (10) NOT NULL,
    seconds         INTEGER,
    name            VARCHAR (30) NOT NULL,
    is_intraday     BOOLEAN      NOT NULL,
    is_aggregatable BOOLEAN      NOT NULL,
    CONSTRAINT pk_timeframe PRIMARY KEY (
        id
    ),
    CONSTRAINT uq_timeframe_code UNIQUE (
        code
    )
);


-- Table: vendor
CREATE TABLE IF NOT EXISTS vendor (
    id                  INTEGER       NOT NULL,
    name                VARCHAR (45)  NOT NULL,
    description         VARCHAR (225),
    allowed_time_series VARCHAR (225) NOT NULL,
    CONSTRAINT pk_vendor PRIMARY KEY (
        id
    )
);


-- Table: vfi
CREATE TABLE IF NOT EXISTS vfi (
    id            INTEGER       NOT NULL,
    qfi_id        INTEGER       NOT NULL,
    vendor_id     INTEGER       NOT NULL,
    vendor_ticker VARCHAR (45)  NOT NULL,
    name          VARCHAR (45)  NOT NULL,
    description   VARCHAR (225),
    CONSTRAINT pk_vfi PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_vfi_qfi_id_qfi FOREIGN KEY (
        qfi_id
    )
    REFERENCES qfi (id),
    CONSTRAINT fk_vfi_vendor_id_vendor FOREIGN KEY (
        vendor_id
    )
    REFERENCES vendor (id),
    CONSTRAINT uq_vfi_name UNIQUE (
        name
    )
);


-- Table: vfi_time_series
CREATE TABLE IF NOT EXISTS vfi_time_series (
    id                 INTEGER  NOT NULL,
    vfi_id             INTEGER  NOT NULL,
    timeframe_id       INTEGER  NOT NULL,
    enabled            BOOLEAN  NOT NULL,
    history_days       INTEGER,
    last_imported_at   DATETIME,
    last_imported_from DATE,
    last_imported_to   DATE,
    CONSTRAINT pk_vfi_time_series PRIMARY KEY (
        id
    ),
    CONSTRAINT fk_vfi_time_series_timeframe_id_timeframe FOREIGN KEY (
        timeframe_id
    )
    REFERENCES timeframe (id),
    CONSTRAINT fk_vfi_time_series_vfi_id_vfi FOREIGN KEY (
        vfi_id
    )
    REFERENCES vfi (id),
    CONSTRAINT uq_vfi_time_series_vfi_id UNIQUE (
        vfi_id,
        timeframe_id
    )
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;