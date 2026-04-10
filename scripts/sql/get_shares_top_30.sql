
WITH ranked_stocks AS (
    SELECT 
        g.id,
        g.name,
        g.isin,
        g.ticker_go,
        g.ticker_bl,
        g.ticker_yf,
        g.country_id,
        c.name AS country_name,
        gf.market_cap,
        NTILE(10) OVER (ORDER BY gf.market_cap DESC) AS percentile_decile
    FROM gfi g
    INNER JOIN gfi_fundamentals gf ON g.id = gf.gfi_id
    LEFT JOIN country c ON g.country_id = c.id
    WHERE g.fit_id = 2  -- Stock - shares
        AND gf.market_cap IS NOT NULL
        AND gf.market_cap > 0
)
SELECT 
    id,
    name,
    isin,
    ticker_go,
    ticker_bl,
    ticker_yf,
    country_id,
    country_name,
    market_cap
FROM ranked_stocks
WHERE percentile_decile <= 1  -- Top 30% (deciles 1-3)
ORDER BY market_cap DESC;


################
WITH ranked_stocks AS (
    SELECT 
        g.id,
        g.name,
        g.isin,
        g.ticker_go,
        g.ticker_bl,
        g.ticker_yf,
        g.country_id,
        c.name AS country_name,
        gf.market_cap,
        PERCENT_RANK() OVER (ORDER BY gf.market_cap DESC) AS pct_rank
    FROM gfi g
    INNER JOIN gfi_fundamentals gf ON g.id = gf.gfi_id
    LEFT JOIN country c ON g.country_id = c.id
    WHERE g.fit_id = 2  -- Stock - shares
        AND gf.market_cap IS NOT NULL
        AND gf.market_cap > 0
)
SELECT 
    id,
    name,
    isin,
    ticker_go,
    ticker_bl,
    ticker_yf,
    country_id,
    country_name,
    market_cap
FROM ranked_stocks
WHERE pct_rank <= 0.1  -- Top 30%
ORDER BY market_cap DESC;