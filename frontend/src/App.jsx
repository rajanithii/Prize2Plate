import React, { useEffect, useMemo, useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  Check,
  ChevronRight,
  CircleAlert,
  CloudRain,
  Droplets,
  Leaf,
  LoaderCircle,
  MapPin,
  RefreshCw,
  Search,
  Sprout,
  Wheat,
} from "lucide-react";

const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

async function getJson(path) {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail || `Request failed (${response.status})`);
  }
  return response.json();
}

function formatPercent(value) {
  const number = Number(value) || 0;
  return `${number > 0 ? "+" : ""}${number.toFixed(1)}%`;
}

function signalTone(value) {
  if (value === "high" || value === "above_normal" || value === "below_normal") return "risk";
  if (value === "medium") return "watch";
  if (value === "low" || value === "normal") return "steady";
  return "muted";
}

function SignalPill({ value, label }) {
  const tone = signalTone(value);
  return <span className={`signal-pill ${tone}`}>{label || value?.replaceAll("_", " ") || "Unknown"}</span>;
}

function App() {
  const [foods, setFoods] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedName, setSelectedName] = useState("");
  const [detail, setDetail] = useState(null);
  const [climate, setClimate] = useState(null);
  const [alternatives, setAlternatives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [alertsOnly, setAlertsOnly] = useState(false);

  async function refreshDashboard() {
    setLoading(true);
    setError("");
    try {
      const [foodData, alertData] = await Promise.all([
        getJson("/foods"),
        getJson("/alerts"),
      ]);
      setFoods(foodData);
      setAlerts(alertData);
      setSelectedName((current) =>
        current && foodData.some((food) => food.name === current)
          ? current
          : foodData[0]?.name || "",
      );
    } catch (requestError) {
      setError(requestError.message || "Unable to connect to the Prize2Plate API.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshDashboard();
  }, []);

  useEffect(() => {
    if (!selectedName) return undefined;
    let cancelled = false;
    setDetailLoading(true);
    setDetail(null);
    setClimate(null);
    setAlternatives([]);

    Promise.all([
      getJson(`/foods/${encodeURIComponent(selectedName)}`),
      getJson(`/alternatives/${encodeURIComponent(selectedName)}`),
    ])
      .then(async ([foodDetail, alternativeData]) => {
        const climateData = await getJson(
          `/climate/${encodeURIComponent(foodDetail.primary_location)}`,
        );
        if (cancelled) return;
        setDetail(foodDetail);
        setAlternatives(alternativeData.alternatives || []);
        setClimate(climateData);
      })
      .catch((requestError) => {
        if (!cancelled) setError(requestError.message || "Unable to load food details.");
      })
      .finally(() => {
        if (!cancelled) setDetailLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedName]);

  const visibleFoods = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    const alertNames = new Set(alerts.map((alert) => alert.food));
    return foods
      .filter((food) => !alertsOnly || alertNames.has(food.name))
      .filter((food) => !normalizedQuery || food.name.toLowerCase().includes(normalizedQuery))
      .sort((a, b) => Number(b.increase_percent) - Number(a.increase_percent));
  }, [alerts, alertsOnly, foods, query]);

  const averageIncrease = foods.length
    ? foods.reduce((total, food) => total + (Number(food.increase_percent) || 0), 0) / foods.length
    : 0;
  const selectedIsAlert = alerts.some((alert) => alert.food === selectedName);

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Prize2Plate home">
          <span className="brand-mark"><Leaf size={19} strokeWidth={2.4} /></span>
          <span>Prize<span>2</span>Plate</span>
        </a>
        <div className="topbar-right">
          <span className={`connection-state ${error ? "offline" : loading ? "connecting" : "online"}`}>
            <span className="connection-dot" />
            {error ? "API offline" : loading ? "Connecting" : "Live connection"}
          </span>
          <button className="icon-button refresh-button" onClick={refreshDashboard} disabled={loading} title="Refresh data" aria-label="Refresh data">
            {loading ? <LoaderCircle className="spin" size={17} /> : <RefreshCw size={17} />}
          </button>
          <a className="api-link" href={`${API_URL}/docs`} target="_blank" rel="noreferrer">API docs <ChevronRight size={14} /></a>
        </div>
      </header>

      <main id="top" className="page-wrap">
        <section className="intro-block">
          <div className="intro-copy">
            <p className="eyebrow"><span /> FOOD SYSTEM INTELLIGENCE</p>
            <h1>Market <em>watch</em></h1>
            <p className="intro-subtitle">Price movement, supply pressure, and local climate signals in one view.</p>
          </div>
          <div className="intro-stamp">
            <span className="stamp-icon"><Wheat size={20} /></span>
            <div><strong>India</strong><span>Staple food monitor</span></div>
            <span className="stamp-count">{foods.length.toString().padStart(2, "0")} <small>foods</small></span>
          </div>
        </section>

        {error && (
          <div className="error-banner" role="alert">
            <CircleAlert size={18} />
            <span>{error}</span>
            <button onClick={refreshDashboard}>Retry</button>
          </div>
        )}

        <section className="metric-grid" aria-label="Market summary">
          <article className="metric-card metric-alerts">
            <div className="metric-top"><span>Active price alerts</span><CircleAlert size={18} /></div>
            <strong>{alerts.length.toString().padStart(2, "0")}</strong>
            <span className="metric-foot"><span className="tiny-dot red" /> Foods above the alert threshold</span>
          </article>
          <article className="metric-card metric-tracked">
            <div className="metric-top"><span>Foods tracked</span><Sprout size={19} /></div>
            <strong>{foods.length.toString().padStart(2, "0")}</strong>
            <span className="metric-foot"><span className="tiny-dot green" /> Across 5 food groups</span>
          </article>
          <article className="metric-card metric-movement">
            <div className="metric-top"><span>Average price movement</span><ArrowUpRight size={18} /></div>
            <strong className={averageIncrease >= 0 ? "text-risk" : "text-green"}>{formatPercent(averageIncrease)}</strong>
            <span className="metric-foot"><span className="tiny-dot gold" /> Versus recent normal price</span>
          </article>
          <article className="metric-note">
            <span className="note-kicker"><span className="tiny-dot gold" /> DATA NOTE</span>
            <p>Illustrative sample data</p>
            <span>Not a live government feed</span>
          </article>
        </section>

        <section className="work-area">
          <div className="market-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">THE DAILY BOARD</p>
                <h2>Food prices</h2>
              </div>
              <span className="result-count">{visibleFoods.length} of {foods.length}</span>
            </div>

            <div className="table-tools">
              <label className="search-box">
                <Search size={17} />
                <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find a food" aria-label="Search foods" />
                {query && <button className="clear-search" onClick={() => setQuery("")} aria-label="Clear search">×</button>}
              </label>
              <div className="filter-switch" role="group" aria-label="Food list filter">
                <button className={!alertsOnly ? "active" : ""} onClick={() => setAlertsOnly(false)}>All foods</button>
                <button className={alertsOnly ? "active" : ""} onClick={() => setAlertsOnly(true)}>Alerts <span>{alerts.length}</span></button>
              </div>
            </div>

            <div className="food-list" role="list" aria-label="Food price list">
              <div className="food-list-head" aria-hidden="true">
                <span>FOOD / GROUP</span><span>MARKET PRICE</span><span>CHANGE</span>
              </div>
              {loading && !foods.length ? (
                <div className="list-message"><LoaderCircle className="spin" size={20} /> Loading market data</div>
              ) : visibleFoods.length ? visibleFoods.map((food, index) => {
                const isAlert = alerts.some((alert) => alert.food === food.name);
                const isSelected = selectedName === food.name;
                const change = Number(food.increase_percent) || 0;
                return (
                  <button
                    key={food.name}
                    className={`food-row ${isSelected ? "selected" : ""}`}
                    onClick={() => setSelectedName(food.name)}
                    aria-pressed={isSelected}
                    role="listitem"
                  >
                    <span className="food-identity">
                      <span className={`food-index ${isSelected ? "selected-index" : ""}`}>{String(index + 1).padStart(2, "0")}</span>
                      <span className="food-name-wrap"><strong>{food.name}</strong><small>{isAlert ? "Price alert" : "Stable range"}</small></span>
                    </span>
                    <span className="food-price">{currency.format(food.current_price)}</span>
                    <span className={`change-value ${change >= 10 ? "change-risk" : change < 0 ? "change-down" : ""}`}>
                      {change >= 0 ? <ArrowUpRight size={15} /> : <ArrowDownRight size={15} />}
                      {formatPercent(change)}
                    </span>
                  </button>
                );
              }) : (
                <div className="list-message empty-message">No foods match this view.</div>
              )}
            </div>
            <div className="table-footer"><span>Sorted by largest price movement</span><span><span className="tiny-dot red" /> Alert threshold: 10%</span></div>
          </div>

          <aside className="detail-column" aria-label="Selected food details">
            {detailLoading && !detail ? (
              <div className="detail-loading"><LoaderCircle className="spin" size={22} /><span>Loading food signals</span></div>
            ) : detail ? (
              <>
                <section className="detail-card selected-card">
                  <div className="detail-card-top">
                    <span className="detail-category"><Sprout size={14} /> {detail.category}</span>
                    <SignalPill value={selectedIsAlert ? "high" : "low"} label={selectedIsAlert ? "Price alert" : "Within range"} />
                  </div>
                  <h2>{detail.name}</h2>
                  <div className="location-line"><MapPin size={14} /> {detail.primary_location} <span>·</span> per {detail.unit}</div>
                  <div className="price-focus">
                    <div><span className="label-caps">CURRENT PRICE</span><strong>{currency.format(detail.current_price)}</strong></div>
                    <div className={`price-change ${Number(detail.increase_percent) >= 10 ? "text-risk" : "text-green"}`}>
                      {Number(detail.increase_percent) >= 0 ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
                      <strong>{formatPercent(detail.increase_percent)}</strong>
                    </div>
                  </div>
                  <div className="baseline-line"><span>Recent normal</span><strong>{currency.format(detail.normal_price)}</strong></div>
                  <div className="price-track" aria-label={`Current price compared with normal price`}>
                    <span style={{ width: `${Math.min(100, Math.max(8, (Number(detail.normal_price) / Math.max(Number(detail.current_price), Number(detail.normal_price), 1)) * 100))}%` }} />
                    <i style={{ left: `${Math.min(100, Math.max(8, (Number(detail.current_price) / Math.max(Number(detail.current_price), Number(detail.normal_price), 1)) * 100))}%` }} />
                  </div>
                </section>

                <section className="detail-card signals-card">
                  <div className="card-title-row"><h3>Supply signals</h3><span className={`signal-orbit ${signalTone(detail.supply_signal)}`}><Sprout size={16} /></span></div>
                  <div className="signal-line">
                    <span><strong>Production</strong><small>{formatPercent(detail.production_change_percent)} vs normal</small></span>
                    <SignalPill value={detail.production_signal} />
                  </div>
                  <div className="signal-line">
                    <span><strong>Market arrivals</strong><small>{formatPercent(detail.arrival_change_percent)} vs normal</small></span>
                    <SignalPill value={detail.market_arrival_signal} />
                  </div>
                  <div className={`supply-summary ${signalTone(detail.supply_signal)}`}>
                    <span className="summary-mark"><Check size={15} /></span>
                    <span>Overall supply pressure</span>
                    <strong>{detail.supply_signal}</strong>
                  </div>
                </section>

                <section className="detail-card climate-card">
                  <div className="card-title-row"><h3>Climate signal</h3><span className="weather-mark"><CloudRain size={17} /></span></div>
                  {climate ? (
                    <>
                      <div className="climate-reading">
                        <div><span className="label-caps">RAINFALL</span><strong>{climate.rainfall}<small> mm</small></strong></div>
                        <span className="climate-vs">vs</span>
                        <div><span className="label-caps">NORMAL</span><strong>{climate.normal_rainfall}<small> mm</small></strong></div>
                        <SignalPill value={climate.status} label={climate.status.replaceAll("_", " ")} />
                      </div>
                      <div className="climate-foot"><Droplets size={14} /><span>{formatPercent(climate.deviation_percent)} rainfall deviation</span><strong>{climate.signal} signal</strong></div>
                    </>
                  ) : <div className="inline-loading"><LoaderCircle className="spin" size={16} /> Loading local climate</div>}
                </section>

                <section className="detail-card alternatives-card">
                  <div className="card-title-row"><div><p className="eyebrow">BETTER PLATE</p><h3>Consider instead</h3></div><span className="alt-count">{alternatives.length.toString().padStart(2, "0")}</span></div>
                  {alternatives.length ? alternatives.map((alternative, index) => {
                    const saving = Math.max(0, Math.round((1 - Number(alternative.price) / Math.max(Number(detail.current_price), 1)) * 100));
                    return (
                      <div className="alternative-row" key={alternative.name}>
                        <span className="alternative-rank">{String(index + 1).padStart(2, "0")}</span>
                        <span className="alternative-main"><strong>{alternative.name}</strong><small>{alternative.reason}</small></span>
                        <span className="alternative-price"><strong>{currency.format(alternative.price)}</strong><small>{saving}% less</small></span>
                      </div>
                    );
                  }) : <p className="no-alternatives">No alternatives available for this food.</p>}
                </section>

                {detail.possible_contributing_factors?.length > 0 && (
                  <section className="factor-note">
                    <span className="factor-icon"><CircleAlert size={16} /></span>
                    <div><strong>Possible contributing factors</strong><ul>{detail.possible_contributing_factors.map((factor) => <li key={factor}>{factor}</li>)}</ul></div>
                  </section>
                )}
              </>
            ) : (
              <div className="detail-empty"><Sprout size={24} /><span>Select a food to inspect its signals.</span></div>
            )}
          </aside>
        </section>
        <footer className="page-footer"><span><Leaf size={14} /> Prize2Plate</span><span>Sample data for demonstration · Not a live government feed</span></footer>
      </main>
    </div>
  );
}

export default App;
