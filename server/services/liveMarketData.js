const LIVE_DATA_PROVIDER = (process.env.LIVE_DATA_PROVIDER || "").toLowerCase()
const LIVE_MARKET_SYMBOL = process.env.LIVE_MARKET_SYMBOL || "^NSEI"

async function fetchYahooMarketData(symbol) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?range=1d&interval=1m`

  const response = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0",
      "Accept": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error(`Yahoo Finance request failed: ${response.status}`)
  }

  const payload = await response.json()
  const result = payload?.chart?.result?.[0]
  const meta = result?.meta || {}
  const timestamp = result?.timestamp?.at(-1)
  const close = result?.indicators?.quote?.[0]?.close?.at(-1)

  return {
    source: "yahoo_finance",
    symbol,
    spot: close ?? meta.regularMarketPrice ?? null,
    price: close ?? meta.regularMarketPrice ?? null,
    updatedAt: timestamp ? new Date(timestamp * 1000).toISOString() : new Date().toISOString(),
    raw: payload,
  }
}

async function fetchLiveMarketSnapshot() {
  const provider = LIVE_DATA_PROVIDER

  if (!provider) {
    return null
  }

  try {
    if (provider === "yahoo") {
      return await fetchYahooMarketData(LIVE_MARKET_SYMBOL)
    }

    if (provider === "nse") {
      const url = `https://www.nseindia.com/api/quote-equity?symbol=${encodeURIComponent(LIVE_MARKET_SYMBOL)}`
      const response = await fetch(url, {
        headers: {
          "User-Agent": "Mozilla/5.0",
          "Accept": "application/json",
          "Accept-Language": "en-US,en;q=0.9",
          "Referer": "https://www.nseindia.com/",
          "Origin": "https://www.nseindia.com",
        },
      })

      if (!response.ok) {
        throw new Error(`NSE request failed: ${response.status}`)
      }

      const payload = await response.json()
      return {
        source: "nse",
        symbol: LIVE_MARKET_SYMBOL,
        spot: payload?.priceInfo?.lastPrice ?? null,
        price: payload?.priceInfo?.lastPrice ?? null,
        updatedAt: new Date().toISOString(),
        raw: payload,
      }
    }
  } catch (error) {
    console.warn("Live market data fetch failed:", error.message)
    return null
  }

  return null
}

module.exports = {
  fetchLiveMarketSnapshot,
}
