
WITH ranked_gfi AS (
    SELECT 
        g.*,
        gf.market_cap,
        NTILE(10) OVER (ORDER BY gf.market_cap DESC) AS percentile_decile
    FROM gfi g
    INNER JOIN gfi_fundamentals gf ON g.id = gf.gfi_id
    WHERE g.country_id = 227
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
    market_cap
FROM ranked_gfi
WHERE percentile_decile <= 2  -- Top 30% (deciles 1-3)
ORDER BY market_cap DESC;

# Alternative Using PERCENT_RANK (More Flexible)

WITH ranked_gfi AS (
    SELECT 
        g.*,
        gf.market_cap,
        PERCENT_RANK() OVER (ORDER BY gf.market_cap DESC) AS pct_rank
    FROM gfi g
    INNER JOIN gfi_fundamentals gf ON g.id = gf.gfi_id
    WHERE g.country_id = 227
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
    market_cap
FROM ranked_gfi
WHERE pct_rank <= 0.3  -- Top 30%
ORDER BY market_cap DESC;

# Solution Using NTILE (Most Precise)

WITH ranked_gfi AS (
    SELECT 
        g.*,
        gf.market_cap,
        NTILE(10) OVER (ORDER BY gf.market_cap DESC) AS percentile_decile
    FROM gfi g
    INNER JOIN gfi_fundamentals gf ON g.id = gf.gfi_id
    WHERE g.country_id = 227
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
    market_cap
FROM ranked_gfi
WHERE percentile_decile <= 3  -- Top 30% (deciles 1-3)
ORDER BY market_cap DESC;
