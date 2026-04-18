const express = require("express")
const router = express.Router()
const { getCollection, getDB, isMongoAvailable } = require("../config/mongo")
const { loadLocalOptionsData } = require("../services/localOptionsData")

function groupByStrike(records) {
  const grouped = new Map()

  records.forEach(record => {
    const strike = Number(record.strike)
    const oiCE = Number(record.oi_CE || 0)
    const oiPE = Number(record.oi_PE || 0)

    if (!Number.isFinite(strike)) return

    const current = grouped.get(strike) || { _id: strike, total_oi: 0, ceOI: 0, peOI: 0 }
    current.total_oi += oiCE + oiPE
    current.ceOI += oiCE
    current.peOI += oiPE
    grouped.set(strike, current)
  })

  return Array.from(grouped.values())
}

function getFallbackGroups() {
  return groupByStrike(loadLocalOptionsData())
}

function buildFallbackSummary() {
  const groups = getFallbackGroups().sort((a, b) => b.total_oi - a.total_oi)
  const topOI = groups.slice(0, 10).map(({ _id, total_oi }) => ({ _id, total_oi }))
  const unusualOI = groups.slice(0, 5).map(({ _id, total_oi }) => ({ strike: _id, total_oi }))

  const totals = groups.reduce((acc, item) => {
    acc.callOI += item.ceOI
    acc.putOI += item.peOI
    return acc
  }, { callOI: 0, putOI: 0 })

  const pcr = totals.callOI === 0 ? 0 : totals.putOI / totals.callOI
  const sentiment = pcr < 0.8 ? "Bullish" : pcr > 1.2 ? "Bearish" : "Neutral"

  let minPain = Infinity
  let maxPainStrike = null
  groups.forEach(s => {
    let pain = 0
    groups.forEach(opt => {
      if (s._id > opt._id) pain += (s._id - opt._id) * (opt.ceOI || 0)
      if (s._id < opt._id) pain += (opt._id - s._id) * (opt.peOI || 0)
    })
    if (pain < minPain) {
      minPain = pain
      maxPainStrike = s._id
    }
  })

  return {
    source: "local_csv_fallback",
    pcr,
    maxPainStrike,
    callOI: totals.callOI,
    putOI: totals.putOI,
    sentiment,
    topOI,
    unusualOI,
    updatedAt: new Date().toISOString(),
  }
}

async function getLatestSnapshot() {
  return getDB()
    .collection("analytics_snapshots")
    .find({})
    .sort({ snapshot_time: -1 })
    .limit(1)
    .next()
}

async function getLatestMarketSummary() {
  return getDB()
    .collection("latest_market_summary")
    .findOne({ summary_key: "global" })
}

async function getLatestAnomalySignals(limit = 5) {
  return getDB()
    .collection("anomaly_signals")
    .find({}, { projection: { _id: 0, strike: 1, total_oi: 1, anomaly_score: 1, snapshot_time: 1 } })
    .sort({ snapshot_time: -1 })
    .limit(limit)
    .toArray()
}

router.get("/summary", async (req, res) => {
  try {
    if (isMongoAvailable()) {
      const summary = await getLatestMarketSummary() || await getLatestSnapshot()
      const anomalies = await getLatestAnomalySignals(5)

      if (summary) {
        return res.json({
          source: summary.summary_key === "global" ? "latest_market_summary" : "analytics_snapshots",
          pcr: summary.pcr || 0,
          maxPainStrike: summary.max_pain_strike ?? null,
          callOI: summary.call_oi || 0,
          putOI: summary.put_oi || 0,
          sentiment: summary.sentiment || "",
          topOI: (summary.top_oi_strikes || []).map(item => ({
            _id: item.strike,
            total_oi: item.total_oi,
          })),
          unusualOI: anomalies.map(({ strike, total_oi, anomaly_score }) => ({
            strike,
            total_oi,
            anomaly_score,
          })),
          updatedAt: summary.updated_at || summary.snapshot_time || null,
        })
      }
    }

    return res.json(buildFallbackSummary())
  } catch (e) { console.error(e); res.status(500).json({ error: "Server error" }) }
})

// TOP OI STRIKES
router.get("/top-oi", async (req, res) => {
  try {
    if (isMongoAvailable()) {
      const snapshot = await getLatestMarketSummary() || await getLatestSnapshot()
      if (snapshot?.top_oi_strikes?.length) {
        return res.json(
          snapshot.top_oi_strikes.map(item => ({
            _id: item.strike,
            total_oi: item.total_oi,
          }))
        )
      }
    }

    if (!isMongoAvailable()) {
      const data = getFallbackGroups()
        .sort((a, b) => b.total_oi - a.total_oi)
        .slice(0, 10)
        .map(({ _id, total_oi }) => ({ _id, total_oi }))
      return res.json(data)
    }

    const collection = getCollection()
    const data = await collection.aggregate([
      { $group: { _id: "$strike", total_oi: { $sum: { $add: [{ $ifNull: ["$oi_CE", 0] }, { $ifNull: ["$oi_PE", 0] }] } } } },
      { $sort: { total_oi: -1 } },
      { $limit: 10 }
    ]).toArray()
    res.json(data)
  } catch (e) { console.error(e); res.status(500).json({ error: "Server error" }) }
})

// CALL vs PUT OI
router.get("/call-put-oi", async (req, res) => {
  try {
    if (isMongoAvailable()) {
      const snapshot = await getLatestMarketSummary() || await getLatestSnapshot()
      if (snapshot) {
        return res.json({
          callOI: snapshot.call_oi || 0,
          putOI: snapshot.put_oi || 0,
        })
      }
    }

    if (!isMongoAvailable()) {
      const totals = getFallbackGroups().reduce((acc, item) => {
        acc.callOI += item.ceOI
        acc.putOI += item.peOI
        return acc
      }, { callOI: 0, putOI: 0 })
      return res.json(totals)
    }

    const collection = getCollection()
    const result = await collection.aggregate([
      { $group: { _id: null, callOI: { $sum: { $ifNull: ["$oi_CE", 0] } }, putOI: { $sum: { $ifNull: ["$oi_PE", 0] } } } }
    ]).toArray()
    res.json({ callOI: result[0]?.callOI || 0, putOI: result[0]?.putOI || 0 })
  } catch (e) { console.error(e); res.status(500).json({ error: "Server error" }) }
})

// PUT CALL RATIO
router.get("/pcr", async (req, res) => {
  try {
    if (isMongoAvailable()) {
      const snapshot = await getLatestMarketSummary() || await getLatestSnapshot()
      if (snapshot) {
        return res.json({ pcr: snapshot.pcr || 0 })
      }
    }

    if (!isMongoAvailable()) {
      const totals = getFallbackGroups().reduce((acc, item) => {
        acc.callOI += item.ceOI
        acc.putOI += item.peOI
        return acc
      }, { callOI: 0, putOI: 0 })
      return res.json({ pcr: totals.callOI === 0 ? 0 : totals.putOI / totals.callOI })
    }

    const collection = getCollection()
    const result = await collection.aggregate([
      { $group: { _id: null, callOI: { $sum: { $ifNull: ["$oi_CE", 0] } }, putOI: { $sum: { $ifNull: ["$oi_PE", 0] } } } }
    ]).toArray()
    const callOI = result[0]?.callOI || 0
    const putOI = result[0]?.putOI || 0
    res.json({ pcr: callOI === 0 ? 0 : putOI / callOI })
  } catch (e) { console.error(e); res.status(500).json({ error: "Server error" }) }
})

// MAX PAIN
router.get("/max-pain", async (req, res) => {
  try {
    if (isMongoAvailable()) {
      const snapshot = await getLatestMarketSummary() || await getLatestSnapshot()
      if (snapshot) {
        return res.json({ maxPainStrike: snapshot.max_pain_strike ?? null })
      }
    }

    if (!isMongoAvailable()) {
      const strikes = getFallbackGroups()
      let minPain = Infinity, maxPainStrike = null
      strikes.forEach(s => {
        let pain = 0
        strikes.forEach(opt => {
          if (s._id > opt._id) pain += (s._id - opt._id) * (opt.ceOI || 0)
          if (s._id < opt._id) pain += (opt._id - s._id) * (opt.peOI || 0)
        })
        if (pain < minPain) { minPain = pain; maxPainStrike = s._id }
      })
      return res.json({ maxPainStrike })
    }

    const collection = getCollection()
    const strikes = await collection.aggregate([
      { $group: { _id: "$strike", ceOI: { $sum: "$oi_CE" }, peOI: { $sum: "$oi_PE" } } }
    ]).toArray()
    let minPain = Infinity, maxPainStrike = null
    strikes.forEach(s => {
      let pain = 0
      strikes.forEach(opt => {
        if (s._id > opt._id) pain += (s._id - opt._id) * (opt.ceOI || 0)
        if (s._id < opt._id) pain += (opt._id - s._id) * (opt.peOI || 0)
      })
      if (pain < minPain) { minPain = pain; maxPainStrike = s._id }
    })
    res.json({ maxPainStrike })
  } catch (e) { console.error(e); res.status(500).json({ error: "Server error" }) }
})

// UNUSUAL OI
router.get("/unusual-oi", async (req, res) => {
  try {
    if (isMongoAvailable()) {
      const anomalies = await getLatestAnomalySignals(5)
      if (anomalies.length > 0) {
        return res.json(anomalies.map(({ strike, total_oi, anomaly_score }) => ({
          strike,
          total_oi,
          anomaly_score,
        })))
      }
    }

    if (!isMongoAvailable()) {
      const data = getFallbackGroups()
        .sort((a, b) => b.total_oi - a.total_oi)
        .slice(0, 5)
        .map(({ _id, total_oi }) => ({ strike: _id, total_oi }))
      return res.json(data)
    }

    const collection = getCollection()
    const data = await collection.aggregate([
      { $group: { _id: "$strike", total_oi: { $sum: { $add: [{ $ifNull: ["$oi_CE", 0] }, { $ifNull: ["$oi_PE", 0] }] } } } },
      { $sort: { total_oi: -1 } },
      { $limit: 5 },
      { $project: { strike: "$_id", total_oi: 1, _id: 0 } }
    ]).toArray()
    res.json(data)
  } catch (e) { console.error(e); res.status(500).json({ error: "Server error" }) }
})

// NIFTY TICKS — live price data
router.get("/nifty-ticks", async (req, res) => {
  try {
    const data = await getDB()
      .collection("nifty_ticks")
      .find({})
      .sort({ datetime: -1 })
      .limit(60)
      .toArray()
    res.json(data.reverse())
  } catch (e) { console.error(e); res.status(500).json({ error: e.message }) }
})

module.exports = router
