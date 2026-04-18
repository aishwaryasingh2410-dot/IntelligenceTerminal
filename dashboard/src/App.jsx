import React, { useEffect, useState, useRef, useCallback } from "react"
import axios from "axios"
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ComposedChart, Cell, ReferenceLine, AreaChart, Area, CartesianGrid, LineChart, Line
} from "recharts"

const API = "http://localhost:5000/api/options"
const POLL = 2000

const FALLBACK_TOP_OI = [
  { _id: 25500, total_oi: 87473000000 },
  { _id: 25600, total_oi: 85024000000 },
  { _id: 25700, total_oi: 84629000000 },
  { _id: 25800, total_oi: 73411000000 },
  { _id: 26000, total_oi: 85538000000 },
]

const FALLBACK_SMART_MONEY = [
  { strike: 25500, total_oi: 87473000000 },
  { strike: 26000, total_oi: 85538000000 },
  { strike: 25600, total_oi: 85024000000 },
  { strike: 25700, total_oi: 84629000000 },
  { strike: 25800, total_oi: 73411000000 },
]

const FALLBACK_CALL_PUT = { callOI: 669300000000, putOI: 537400000000 }
const FALLBACK_PCR = 0.8029
const FALLBACK_MAX_PAIN = 25650
const FALLBACK_SENTIMENT = "Neutral"

const C = {
  bg: "#0b0e11", panel: "#131921", panel2: "#1a2332",
  border: "#1e2d3d", border2: "#2a3f5a",
  accent: "#00d4ff", green: "#00c076", red: "#ef5350",
  yellow: "#f0b90b", text: "#eaecef", muted: "#5a6a7a",
  headerBg: "#161c24",
}
const mono = "'IBM Plex Mono', monospace"
const sans = "'Inter', 'Segoe UI', sans-serif"
const ttStyle = { background: C.panel, border: `1px solid ${C.border2}`, fontSize: "11px", fontFamily: mono, color: C.text, borderRadius: "2px", padding: "8px 12px" }

function Ticker({ value, format, color, size = 14 }) {
  const [flash, setFlash] = useState(false)
  const prev = useRef(value)
  useEffect(() => {
    if (value != null && value !== prev.current) { setFlash(true); setTimeout(() => setFlash(false), 400); prev.current = value }
  }, [value])
  return <span style={{ color: flash ? "#fff" : (color || C.text), transition: "color 0.2s", fontSize: size, fontVariantNumeric: "tabular-nums", fontFamily: mono }}>{value != null ? (format ? format(value) : value) : "—"}</span>
}

function Tab({ label, active, onClick }) {
  return <button onClick={onClick} style={{ background: "none", border: "none", cursor: "pointer", padding: "14px 20px", fontSize: "13px", fontFamily: sans, color: active ? C.text : C.muted, borderBottom: active ? `2px solid ${C.yellow}` : "2px solid transparent", fontWeight: active ? 600 : 400, transition: "all 0.15s", letterSpacing: "0.02em" }}>{label}</button>
}

function OrderBookRow({ price, size, type, maxSize }) {
  const pct = maxSize > 0 ? (size / maxSize) * 100 : 0
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", padding: "3px 12px", fontSize: "12px", fontFamily: mono, position: "relative", cursor: "default" }}>
      <div style={{ position: "absolute", top: 0, bottom: 0, [type === "bid" ? "right" : "left"]: 0, width: `${pct}%`, background: type === "bid" ? `${C.green}18` : `${C.red}18`, transition: "width 0.3s" }} />
      <span style={{ color: type === "bid" ? C.green : C.red, position: "relative", zIndex: 1 }}>{price.toLocaleString()}</span>
      <span style={{ color: C.text, textAlign: "right", position: "relative", zIndex: 1 }}>{(size / 1e6).toFixed(1)}M</span>
    </div>
  )
}

export default function App() {
  const [tab, setTab] = useState("orderbook")
  const [topOI, setTopOI] = useState([])
  const [pcr, setPCR] = useState(null)
  const [maxPain, setMaxPain] = useState(null)
  const [callPut, setCallPut] = useState({ callOI: 0, putOI: 0 })
  const [smartMoney, setSmartMoney] = useState([])
  const [sentiment, setSentiment] = useState("")
  const [errors, setErrors] = useState([])
  const [lastUpdated, setLastUpdated] = useState(null)
  const [tick, setTick] = useState(0)
  const [pcrHistory, setPcrHistory] = useState([])
  const [oiHistory, setOiHistory] = useState([])
  const [dataSource, setDataSource] = useState("")
  const [niftyTicks, setNiftyTicks] = useState([])
  const hasLiveData = topOI.length > 0 || pcr != null || maxPain != null || callPut.callOI > 0 || callPut.putOI > 0
  const useFallback = !hasLiveData && errors.length > 0

  const displayTopOI = useFallback ? FALLBACK_TOP_OI : topOI
  const displayPCR = useFallback ? FALLBACK_PCR : pcr
  const displayMaxPain = useFallback ? FALLBACK_MAX_PAIN : maxPain
  const displayCallPut = useFallback ? FALLBACK_CALL_PUT : callPut
  const displaySmartMoney = useFallback ? FALLBACK_SMART_MONEY : smartMoney
  const displaySentiment = useFallback ? FALLBACK_SENTIMENT : sentiment
  const latestNiftyTick = niftyTicks[niftyTicks.length - 1] || null
  const previousNiftyTick = niftyTicks[niftyTicks.length - 2] || null
  const niftyPrice = latestNiftyTick?.close ?? null
  const niftyMove = latestNiftyTick && previousNiftyTick ? latestNiftyTick.close - previousNiftyTick.close : 0
  const niftyMovePct = latestNiftyTick && previousNiftyTick && previousNiftyTick.close
    ? (niftyMove / previousNiftyTick.close) * 100
    : 0
  const niftyMoveColor = niftyMove > 0 ? C.green : niftyMove < 0 ? C.red : C.yellow
  const latestNiftyTime = latestNiftyTick?.datetime
    ? new Date(latestNiftyTick.datetime).toLocaleTimeString("en-US", { hour12: false })
    : null

  const fetchData = useCallback(async () => {
    const errs = [], now = new Date().toLocaleTimeString("en-US", { hour12: false })
    await Promise.allSettled([
      axios.get(`${API}/summary`).then(r => {
        const data = r.data
        const v = Number(data.pcr || 0)
        const callOI = Number(data.callOI || 0)
        const putOI = Number(data.putOI || 0)

        setDataSource(data.source || "")
        setTopOI(data.topOI || [])
        setPCR(v)
        setMaxPain(data.maxPainStrike ?? null)
        setSmartMoney(data.unusualOI || [])
        setCallPut({ callOI, putOI })
        setSentiment(data.sentiment || (v < 0.8 ? "Bullish" : v > 1.2 ? "Bearish" : "Neutral"))
        setPcrHistory(h => [...h.slice(-49), { t: now, v: +v.toFixed(4) }])
        setOiHistory(h => [...h.slice(-49), { t: now, ce: +(callOI / 1e9).toFixed(2), pe: +(putOI / 1e9).toFixed(2) }])
      }).catch(() => errs.push("summary")),
      axios.get(`${API}/nifty-ticks`).then(r => {
        const ticks = (r.data || []).map(item => ({
          ...item,
          close: Number(item.close || 0),
        }))
        setNiftyTicks(ticks)
      }).catch(() => errs.push("nifty-ticks")),
    ])
    setErrors(errs); setLastUpdated(now); setTick(t => t + 1)
  }, [])

  useEffect(() => { fetchData(); const id = setInterval(fetchData, POLL); return () => clearInterval(id) }, [fetchData])

  const asks = displayTopOI.slice(0, 6).map(d => ({ price: d._id, size: d.total_oi / 2 })).reverse()
  const bids = displayTopOI.slice(0, 6).map(d => ({ price: d._id - 50, size: d.total_oi / 2 }))
  const maxAskSize = Math.max(...asks.map(x => x.size), 1)
  const maxBidSize = Math.max(...bids.map(x => x.size), 1)
  const sentColor = displaySentiment === "Bullish" ? C.green : displaySentiment === "Bearish" ? C.red : C.yellow
  const pcrChange = pcrHistory.length >= 2 ? pcrHistory[pcrHistory.length - 1].v - pcrHistory[pcrHistory.length - 2].v : 0
  const topOIStrike = displayTopOI[0]?._id ?? null

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap');
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
        html,body{background:${C.bg};height:100%;font-family:${sans};color:${C.text}}
        ::-webkit-scrollbar{width:3px;height:3px}::-webkit-scrollbar-thumb{background:${C.border2}}
        @keyframes blink{0%,100%{opacity:1}50%{opacity:0.2}}
      `}</style>

      <div style={{ display: "flex", flexDirection: "column", height: "100vh", background: C.bg }}>
        {/* NAV */}
        <div style={{ background: C.headerBg, borderBottom: `1px solid ${C.border}`, display: "flex", alignItems: "stretch", justifyContent: "space-between", paddingRight: "20px", flexShrink: 0 }}>
          <div style={{ display: "flex", alignItems: "center" }}>
            <div style={{ padding: "0 20px", borderRight: `1px solid ${C.border}`, height: "100%", display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ color: C.yellow, fontSize: "16px" }}>◈</span>
              <span style={{ fontFamily: mono, fontSize: "13px", fontWeight: 600, letterSpacing: "0.1em" }}>NIFTY OI</span>
            </div>
            <Tab label="Overview" active={tab === "overview"} onClick={() => setTab("overview")} />
            <Tab label="Order Book" active={tab === "orderbook"} onClick={() => setTab("orderbook")} />
            <Tab label="Analysis" active={tab === "analysis"} onClick={() => setTab("analysis")} />
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "20px", fontSize: "12px" }}>
            <span style={{ color: errors.length > 0 ? C.red : C.green, fontFamily: mono }}>
              {useFallback ? "LOCAL FALLBACK" : errors.length > 0 ? `API DEGRADED ${errors.length}/2` : "API OK"}
            </span>
            <span style={{ color: niftyMoveColor, fontFamily: mono }}>
              LIVE MKT: {niftyPrice != null ? `${niftyPrice.toLocaleString()} ${niftyMove >= 0 ? "+" : ""}${niftyMove.toFixed(2)} (${niftyMovePct >= 0 ? "+" : ""}${niftyMovePct.toFixed(2)}%)` : "—"}
            </span>
            <span style={{ color: C.muted, fontFamily: mono }}>TOP OI: <span style={{ color: C.accent }}>{topOIStrike?.toLocaleString() || "—"}</span></span>
            <span style={{ color: C.muted, fontFamily: mono }}>PCR: <span style={{ color: sentColor }}>{displayPCR?.toFixed(4) || "—"}</span> <span style={{ color: pcrChange >= 0 ? C.green : C.red }}>{pcrChange >= 0 ? "▲" : "▼"}{Math.abs(pcrChange).toFixed(4)}</span></span>
            <span style={{ color: C.muted, fontFamily: mono }}>MAX PAIN: <span style={{ color: C.yellow }}>{displayMaxPain?.toLocaleString() || "—"}</span></span>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", padding: "5px 10px", background: `${C.green}15`, border: `1px solid ${C.green}44` }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: C.green, display: "inline-block", animation: "blink 1.5s infinite" }} />
              <span style={{ color: C.green, fontSize: "11px", fontFamily: mono }}>LIVE · #{tick}</span>
            </div>
          </div>
        </div>

        {/* PRICE BAR */}
        <div style={{ background: C.panel, borderBottom: `1px solid ${C.border}`, padding: "10px 20px", display: "flex", alignItems: "baseline", gap: "16px", flexShrink: 0 }}>
          <div style={{ fontSize: "32px", fontFamily: mono, fontWeight: 700 }}><Ticker value={niftyPrice ?? displayMaxPain} format={v => v.toLocaleString()} color={C.text} size={32} /></div>
          <div>
            <div style={{ fontSize: "12px", color: C.muted, fontFamily: mono }}>{niftyPrice != null ? "NIFTY LAST TRADE" : "MAX PAIN STRIKE"}</div>
            <div style={{ fontSize: "12px", fontFamily: mono, color: niftyPrice != null ? niftyMoveColor : sentColor, fontWeight: 600 }}>
              {niftyPrice != null ? `${niftyMove >= 0 ? "+" : ""}${niftyMove.toFixed(2)} (${niftyMovePct >= 0 ? "+" : ""}${niftyMovePct.toFixed(2)}%) · ${latestNiftyTime || "LIVE TICKS"} · ${niftyTicks.length} pts` : `${displaySentiment || "—"} · PCR ${displayPCR?.toFixed(4) || "—"}`}
            </div>
          </div>
          <div style={{ marginLeft: "auto", display: "flex", gap: "24px", fontSize: "12px", fontFamily: mono }}>
            {[{ l: "CALL OI", v: displayCallPut.callOI, c: C.green }, { l: "PUT OI", v: displayCallPut.putOI, c: C.red }, { l: "SIGNAL", v: displaySentiment, c: sentColor }, { l: "UPDATED", v: lastUpdated, c: C.text }].map((x, i) => (
              <div key={i}><div style={{ color: C.muted, marginBottom: 2 }}>{x.l}</div><div style={{ color: x.c, fontWeight: 600 }}>{typeof x.v === "number" ? (x.v / 1e9).toFixed(1) + "B" : (x.v || "—")}</div></div>
            ))}
          </div>
        </div>

        {/* CONTENT */}
        <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>

          {tab === "orderbook" && (
            <div style={{ flex: 1, display: "grid", gridTemplateColumns: "1fr 300px", overflow: "hidden" }}>
              <div style={{ display: "flex", flexDirection: "column", borderRight: `1px solid ${C.border}`, overflow: "hidden" }}>
                <div style={{ padding: "8px 16px", borderBottom: `1px solid ${C.border}`, background: C.panel, fontSize: "11px", fontFamily: mono, color: C.muted, letterSpacing: "0.1em", flexShrink: 0 }}>OI BY STRIKE — CANDLESTICK VIEW</div>
                <div style={{ flex: 1, padding: "16px", background: C.bg, overflow: "hidden", display: "flex", flexDirection: "column", gap: "12px" }}>
                  {displayTopOI.length > 0 ? (
                    <ResponsiveContainer width="100%" height="65%">
                      <BarChart data={displayTopOI} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="2 4" stroke={C.border} vertical={false} />
                        <XAxis dataKey="_id" tick={{ fontSize: 10, fill: C.muted, fontFamily: mono }} axisLine={{ stroke: C.border }} tickLine={false} />
                        <YAxis tick={{ fontSize: 10, fill: C.muted, fontFamily: mono }} tickFormatter={v => (v / 1e9).toFixed(0) + "B"} axisLine={false} tickLine={false} />
                        <Tooltip contentStyle={ttStyle} formatter={v => [(v / 1e9).toFixed(2) + "B", "Total OI"]} />
                        {displayMaxPain && <ReferenceLine x={displayMaxPain} stroke={C.yellow} strokeDasharray="4 4" label={{ value: "MAX PAIN", fill: C.yellow, fontSize: 10 }} />}
                        <Bar dataKey="total_oi" maxBarSize={20} radius={[2, 2, 0, 0]}>
                          {displayTopOI.map((_, i) => <Cell key={i} fill={i % 2 === 0 ? C.green : C.red} fillOpacity={0.85} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  ) : <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: C.muted, fontFamily: mono, fontSize: 12 }}>Loading...</div>}
                  {pcrHistory.length >= 2 && (
                    <div>
                      <div style={{ fontSize: "10px", fontFamily: mono, color: C.muted, marginBottom: "4px", letterSpacing: "0.1em" }}>PCR TREND</div>
                      <ResponsiveContainer width="100%" height={55}>
                        <AreaChart data={pcrHistory} margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
                          <defs><linearGradient id="pg2" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={C.accent} stopOpacity={0.3} /><stop offset="95%" stopColor={C.accent} stopOpacity={0} /></linearGradient></defs>
                          <XAxis hide /><YAxis hide domain={["auto", "auto"]} />
                          <Tooltip contentStyle={ttStyle} formatter={v => [v.toFixed(4), "PCR"]} />
                          <Area type="monotone" dataKey="v" stroke={C.accent} strokeWidth={1.5} fill="url(#pg2)" dot={false} />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </div>
              </div>

              {/* ORDER BOOK */}
              <div style={{ display: "flex", flexDirection: "column", background: C.panel, overflow: "auto" }}>
                <div style={{ padding: "10px 12px", borderBottom: `1px solid ${C.border}`, fontSize: "11px", fontFamily: mono, color: C.muted, letterSpacing: "0.1em", flexShrink: 0 }}>ORDER BOOK</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", padding: "5px 12px", fontSize: "10px", fontFamily: mono, color: C.muted, borderBottom: `1px solid ${C.border}` }}><span>STRIKE</span><span style={{ textAlign: "right" }}>OI</span></div>
                <div style={{ padding: "4px 0" }}>
                  <div style={{ padding: "3px 12px", fontSize: "10px", fontFamily: mono, color: C.muted, letterSpacing: "0.1em" }}>CALLS (RESISTANCE)</div>
                  {asks.map((a, i) => <OrderBookRow key={i} price={a.price} size={a.size} type="ask" maxSize={maxAskSize} />)}
                </div>
                <div style={{ padding: "6px 12px", borderTop: `1px solid ${C.border}`, borderBottom: `1px solid ${C.border}`, background: C.panel2, display: "flex", justifyContent: "space-between", fontSize: "11px", fontFamily: mono }}>
                  <span style={{ color: C.muted }}>MAX PAIN</span><span style={{ color: C.yellow, fontWeight: 600 }}>{displayMaxPain?.toLocaleString() || "—"}</span>
                </div>
                <div style={{ padding: "4px 0" }}>
                  <div style={{ padding: "3px 12px", fontSize: "10px", fontFamily: mono, color: C.muted, letterSpacing: "0.1em" }}>PUTS (SUPPORT)</div>
                  {bids.map((b, i) => <OrderBookRow key={i} price={b.price} size={b.size} type="bid" maxSize={maxBidSize} />)}
                </div>
                <div style={{ marginTop: "auto", borderTop: `1px solid ${C.border}`, padding: "10px 12px" }}>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", fontSize: "11px", fontFamily: mono }}>
                    <div style={{ background: `${C.green}15`, border: `1px solid ${C.green}33`, padding: "8px", textAlign: "center" }}>
                      <div style={{ color: C.muted, fontSize: "9px", marginBottom: "3px" }}>CALL OI</div>
                      <div style={{ color: C.green, fontWeight: 600 }}>{displayCallPut.callOI ? (displayCallPut.callOI / 1e9).toFixed(1) + "B" : "—"}</div>
                    </div>
                    <div style={{ background: `${C.red}15`, border: `1px solid ${C.red}33`, padding: "8px", textAlign: "center" }}>
                      <div style={{ color: C.muted, fontSize: "9px", marginBottom: "3px" }}>PUT OI</div>
                      <div style={{ color: C.red, fontWeight: 600 }}>{displayCallPut.putOI ? (displayCallPut.putOI / 1e9).toFixed(1) + "B" : "—"}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {tab === "overview" && (
            <div style={{ flex: 1, padding: "16px 20px", overflow: "auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", alignContent: "start" }}>
              <div style={{ background: C.panel, border: `1px solid ${C.border}`, padding: "16px", gridColumn: "1/-1" }}>
                <div style={{ fontSize: "11px", fontFamily: mono, color: C.muted, letterSpacing: "0.15em", marginBottom: "12px" }}>NIFTY LIVE TREND</div>
                {niftyTicks.length >= 2 ? (
                  <ResponsiveContainer width="100%" height={160}>
                    <AreaChart data={niftyTicks.map(item => ({ t: new Date(item.datetime).toLocaleTimeString("en-US", { hour12: false }), v: item.close }))} margin={{ top: 5, right: 20, left: 0, bottom: 0 }}>
                      <defs><linearGradient id="pgov" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={niftyMoveColor} stopOpacity={0.2} /><stop offset="95%" stopColor={niftyMoveColor} stopOpacity={0} /></linearGradient></defs>
                      <CartesianGrid strokeDasharray="2 4" stroke={C.border} vertical={false} />
                      <XAxis dataKey="t" tick={{ fontSize: 9, fill: C.muted, fontFamily: mono }} interval="preserveStartEnd" />
                      <YAxis tick={{ fontSize: 9, fill: C.muted, fontFamily: mono }} domain={["auto", "auto"]} />
                      <Tooltip contentStyle={ttStyle} formatter={v => [Number(v).toLocaleString(), "NIFTY"]} />
                      <Area type="monotone" dataKey="v" stroke={niftyMoveColor} strokeWidth={2} fill="url(#pgov)" dot={false} />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : <div style={{ padding: "40px", textAlign: "center", color: C.muted, fontFamily: mono, fontSize: 12 }}>Waiting for live NIFTY ticks</div>}
              </div>
              <div style={{ background: C.panel, border: `1px solid ${C.border}`, padding: "16px" }}>
                <div style={{ fontSize: "11px", fontFamily: mono, color: C.muted, letterSpacing: "0.15em", marginBottom: "12px" }}>TOP OI STRIKES</div>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={displayTopOI} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="2 4" stroke={C.border} vertical={false} />
                    <XAxis dataKey="_id" tick={{ fontSize: 9, fill: C.muted, fontFamily: mono }} />
                    <YAxis tick={{ fontSize: 9, fill: C.muted, fontFamily: mono }} tickFormatter={v => (v / 1e9).toFixed(0) + "B"} />
                    <Tooltip contentStyle={ttStyle} formatter={v => [(v / 1e9).toFixed(2) + "B", "OI"]} />
                    <Bar dataKey="total_oi" maxBarSize={24} radius={[2, 2, 0, 0]}>{displayTopOI.map((_, i) => <Cell key={i} fill={i === 0 ? C.accent : i < 3 ? "#0088ff" : C.border2} />)}</Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div style={{ background: C.panel, border: `1px solid ${C.border}`, padding: "16px" }}>
                <div style={{ fontSize: "11px", fontFamily: mono, color: C.muted, letterSpacing: "0.15em", marginBottom: "12px" }}>CALL / PUT OI TREND</div>
                {oiHistory.length >= 2 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={oiHistory} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="2 4" stroke={C.border} vertical={false} />
                      <XAxis dataKey="t" tick={{ fontSize: 9, fill: C.muted, fontFamily: mono }} interval="preserveStartEnd" />
                      <YAxis tick={{ fontSize: 9, fill: C.muted, fontFamily: mono }} tickFormatter={v => v + "B"} />
                      <Tooltip contentStyle={ttStyle} formatter={(v, n) => [v + "B", n.toUpperCase()]} />
                      <Line type="monotone" dataKey="ce" stroke={C.green} strokeWidth={2} dot={false} name="CE" />
                      <Line type="monotone" dataKey="pe" stroke={C.red} strokeWidth={2} dot={false} name="PE" />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                    <div style={{ height: 200, display: "flex", alignItems: "center", justifyContent: "center", gap: "24px" }}>
                    <span style={{ color: C.green, fontFamily: mono, fontSize: 20, fontWeight: 700 }}>{displayCallPut.callOI ? (displayCallPut.callOI / 1e9).toFixed(1) + "B" : "—"} CE</span>
                    <span style={{ color: C.red, fontFamily: mono, fontSize: 20, fontWeight: 700 }}>{displayCallPut.putOI ? (displayCallPut.putOI / 1e9).toFixed(1) + "B" : "—"} PE</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {tab === "analysis" && (
            <div style={{ flex: 1, padding: "16px 20px", overflow: "auto", display: "grid", gridTemplateColumns: "2fr 1fr", gap: "12px", alignContent: "start" }}>
              <div style={{ background: C.panel, border: `1px solid ${C.border}`, padding: "16px" }}>
                <div style={{ fontSize: "11px", fontFamily: mono, color: C.muted, letterSpacing: "0.15em", marginBottom: "12px" }}>INSTITUTIONAL ACTIVITY</div>
                {displaySmartMoney.length > 0 ? (
                  <>
                    <ResponsiveContainer width="100%" height={180}>
                      <BarChart data={displaySmartMoney} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="2 4" stroke={C.border} vertical={false} />
                        <XAxis dataKey="strike" tick={{ fontSize: 9, fill: C.muted, fontFamily: mono }} />
                        <YAxis tick={{ fontSize: 9, fill: C.muted, fontFamily: mono }} tickFormatter={v => (v / 1e9).toFixed(1) + "B"} />
                        <Tooltip contentStyle={ttStyle} formatter={v => [(v / 1e9).toFixed(3) + "B", "OI"]} />
                        <Bar dataKey="total_oi" fill={C.red} maxBarSize={28} radius={[2, 2, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                    <div style={{ marginTop: "12px", display: "grid", gridTemplateColumns: "1fr 1fr 1fr", fontSize: "11px", fontFamily: mono }}>
                      {["STRIKE", "TOTAL OI", "SIGNAL"].map(h => <span key={h} style={{ color: C.muted, padding: "4px 8px" }}>{h}</span>)}
                      {displaySmartMoney.map((s, i) => (
                        <React.Fragment key={i}>
                          <span style={{ padding: "5px 8px", borderTop: `1px solid ${C.border}` }}>{s.strike}</span>
                          <span style={{ padding: "5px 8px", borderTop: `1px solid ${C.border}`, color: C.red }}>{(s.total_oi / 1e9).toFixed(3)}B</span>
                          <span style={{ padding: "5px 8px", borderTop: `1px solid ${C.border}`, color: C.yellow, fontSize: "10px" }}>WATCH</span>
                        </React.Fragment>
                      ))}
                    </div>
                  </>
                ) : <div style={{ padding: "40px", textAlign: "center", color: C.muted, fontFamily: mono, fontSize: 12 }}>No unusual activity</div>}
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                <div style={{ background: C.panel, border: `1px solid ${C.border}`, padding: "16px" }}>
                  <div style={{ fontSize: "11px", fontFamily: mono, color: C.muted, letterSpacing: "0.15em", marginBottom: "12px" }}>SIGNAL</div>
                  <div style={{ textAlign: "center", padding: "16px", border: `1px solid ${sentColor}44`, background: `${sentColor}08` }}>
                    <div style={{ fontSize: "36px", fontWeight: 700, color: sentColor, fontFamily: mono }}>{displaySentiment || "—"}</div>
                    <div style={{ fontSize: "11px", color: C.muted, marginTop: "6px", fontFamily: mono }}>PCR: {displayPCR?.toFixed(4) || "—"}</div>
                  </div>
                </div>
                <div style={{ background: C.panel, border: `1px solid ${C.border}`, padding: "16px" }}>
                  <div style={{ fontSize: "11px", fontFamily: mono, color: C.muted, letterSpacing: "0.15em", marginBottom: "12px" }}>PCR ZONES</div>
                  {[{ label: "BULLISH", range: "< 0.8", color: C.green, active: displayPCR != null && displayPCR < 0.8 }, { label: "NEUTRAL", range: "0.8–1.2", color: C.yellow, active: displayPCR != null && displayPCR >= 0.8 && displayPCR <= 1.2 }, { label: "BEARISH", range: "> 1.2", color: C.red, active: displayPCR != null && displayPCR > 1.2 }].map((z, i) => (
                    <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "8px 10px", marginBottom: "4px", fontSize: "11px", fontFamily: mono, background: z.active ? `${z.color}18` : "transparent", border: `1px solid ${z.active ? z.color : C.border}`, transition: "all 0.3s" }}>
                      <span style={{ color: z.active ? z.color : C.muted }}>{z.active ? "▶ " : ""}{z.label}</span>
                      <span style={{ color: C.muted }}>{z.range}</span>
                    </div>
                  ))}
                </div>
                <div style={{ background: C.panel, border: `1px solid ${C.border}`, padding: "16px" }}>
                  <div style={{ fontSize: "11px", fontFamily: mono, color: C.muted, letterSpacing: "0.15em", marginBottom: "8px" }}>KEY LEVELS</div>
                  {[{ label: "MAX PAIN", value: displayMaxPain?.toLocaleString(), color: C.yellow }, { label: "TOP STRIKE", value: displayTopOI[0]?._id?.toLocaleString(), color: C.green }, { label: "PCR", value: displayPCR?.toFixed(4), color: C.accent }].map((x, i) => (
                    <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: `1px solid ${C.border}`, fontSize: "12px", fontFamily: mono }}>
                      <span style={{ color: C.muted }}>{x.label}</span><span style={{ color: x.color, fontWeight: 600 }}>{x.value || "—"}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* STATUS BAR */}
        <div style={{ background: C.headerBg, borderTop: `1px solid ${C.border}`, padding: "4px 20px", display: "flex", justifyContent: "space-between", fontSize: "10px", fontFamily: mono, color: C.muted, flexShrink: 0 }}>
          <span>OPTIONS INTELLIGENCE TERMINAL v2.0 · NIFTY OPTIONS ANALYTICS</span>
          <span>{(dataSource || "unknown").toUpperCase()} · POLL {POLL / 1000}s · {lastUpdated || "—"}</span>
        </div>
      </div>
    </>
  )
}
