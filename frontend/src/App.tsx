import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import { Activity, AlertTriangle, ArrowRight, Download, FileSpreadsheet, FileText, Gauge, LoaderCircle, Search, ShieldAlert, Sparkles, X } from "lucide-react";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
type RecordRow = Record<string, string | number | boolean | null | undefined>;
type Result = {
  filename: string; format: string; products: string[]; selected_product: string; rows_received: number; rows_analysed: number; rating_estimated: boolean;
  notes: string[]; summary: { average_rating: number; review_count: number; flagged_count: number; brand_count: number; positive_share: number; negative_share: number };
  executive_summary: string[]; discovered_topics: string[]; aspects: RecordRow[]; issues: RecordRow[]; alerts: RecordRow[]; risks: RecordRow[];
  drivers: RecordRow[]; trends: RecordRow[]; reviews: RecordRow[]; cooccurrence: RecordRow[]; signal_words: RecordRow[]; brief: string;
};
const fmt = (v: unknown) => typeof v === "number" ? v.toLocaleString() : String(v ?? "—");

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [serverSearchResults, setServerSearchResults] = useState<RecordRow[] | null>(null);
  const [searchBusy, setSearchBusy] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [tab, setTab] = useState<"overview" | "issues" | "reviews">("overview");
  const [productBusy, setProductBusy] = useState(false);
  const [dragging, setDragging] = useState(false);


  const filteredReviews = useMemo(() => {
    const rows = serverSearchResults ?? result?.reviews ?? [];
    const q = searchQuery.trim().toLowerCase();
    return rows.filter((r) => !q || Object.values(r).some((v) => String(v ?? "").toLowerCase().includes(q))).slice(0, 100);
  }, [result, searchQuery, serverSearchResults]);

  async function runAnalysis() {
    if (!file || busy) return;
    setBusy(true); setError(""); setResult(null); setServerSearchResults(null);
    try {
      const body = new FormData(); body.append("file", file);
      const response = await fetch(`${API}/api/analyse`, { method: "POST", body });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || `Analysis failed (${response.status})`);
      setResult(payload); setTab("overview");
    } catch (e) { setError(e instanceof Error ? e.message : "Could not connect to the Review Lens API."); }
    finally { setBusy(false); }
  }

  async function runSampleAnalysis() {
    if (busy) return;
    setBusy(true); setError(""); setResult(null); setServerSearchResults(null);
    try {
      const response = await fetch(`${API}/api/analyse-sample`, { method: "POST" });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || `Sample analysis failed (${response.status})`);
      setResult(payload); setTab("overview");
    } catch (e) { setError(e instanceof Error ? e.message : "Could not load the sample dataset."); }
    finally { setBusy(false); }
  }

  async function selectProduct(product: string) {
    if (!result || productBusy) return;
    setProductBusy(true); setError(""); setServerSearchResults(null); setSearchQuery("");
    try {
      const response = await fetch(`${API}/api/product?product=${encodeURIComponent(product)}`, { method: "POST" });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Could not switch product.");
      setResult(payload);
    } catch (e) { setError(e instanceof Error ? e.message : "Could not switch product."); }
    finally { setProductBusy(false); }
  }

  async function searchAllReviews() {
    if (!searchQuery.trim() || searchBusy) { setServerSearchResults(null); return; }
    setSearchBusy(true); setSearchError("");
    try {
      const response = await fetch(`${API}/api/search?q=${encodeURIComponent(searchQuery)}&limit=20`);
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Search failed.");
      setServerSearchResults(payload.results ?? []);
    } catch (e) { setSearchError(e instanceof Error ? e.message : "Review search failed."); }
    finally { setSearchBusy(false); }
  }


  async function downloadBriefDocx() {
    try {
      const response = await fetch(`${API}/api/brief.docx`);
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || "Could not download the brief.");
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "reviewlens-product-manager-brief.docx";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not download the brief.");
    }
  }

  return <div className="app-shell">
    <header className="topbar">
      <a className="brand" href="#"><span className="brand-mark">RL</span><span>REVIEW<span className="gold">LENS</span><small>CUSTOMER VOICE INTELLIGENCE</small></span></a>
      <nav><button className={tab === "overview" ? "nav active" : "nav"} onClick={() => setTab("overview")}>OVERVIEW</button><button className={tab === "issues" ? "nav active" : "nav"} onClick={() => setTab("issues")}>PRIORITY ISSUES</button><button className={tab === "reviews" ? "nav active" : "nav"} onClick={() => setTab("reviews")}>REVIEW EXPLORER</button></nav>
      <div className="status"><span className="pulse" /> LOCAL ANALYTICS</div>
    </header>

    <main>
      <section className="hero-head">
        <div><p className="eyebrow"><span className="eyebrow-line" /> CUSTOMER VOICE / INTELLIGENCE PLATFORM</p><h1>TURN FEEDBACK<br /><span className="muted-heading">INTO FORWARD MOTION.</span></h1><p className="intro">Find what breaks trust, what drives ratings, and what to fix first.</p></div>
        <div className="hero-side"><span className="side-index">01 / ANALYSE</span><span className="side-rule" /><span className="side-copy">EVIDENCE-BACKED<br />PRODUCT DECISIONS</span></div>
      </section>

      <section className="upload-panel">
        <div className="section-top"><div><p className="eyebrow">01 — INGESTION</p><h2>ANALYSIS PIPELINE</h2></div><span className="tiny-note">NO FIXED APP UPLOAD CAP</span></div>
        <label className={`dropzone ${dragging ? "dragging" : ""}`} onDragOver={(e) => {e.preventDefault(); setDragging(true);}} onDragLeave={() => setDragging(false)} onDrop={(e) => {e.preventDefault(); setDragging(false); const dropped=e.dataTransfer.files?.[0]; if(dropped) setFile(dropped);}}>
          <input type="file" accept=".csv,.tsv,.txt,.xlsx,.xls,.xlsm,.json,.jsonl,.ndjson,.parquet,.gz" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          <span className="upload-icon"><FileSpreadsheet size={29} /></span><strong>{file ? file.name : "DROP YOUR REVIEW DATASET HERE"}</strong><span className="muted">{file ? `${(file.size / 1024 / 1024).toFixed(2)} MiB — Ready to process` : "CSV · TSV · TXT · EXCEL · JSON · PARQUET"}</span><span className="choose-file">BROWSE LOCAL FILE <ArrowRight size={15}/></span>
        </label>
        <div className="actions"><button className="button secondary" onClick={() => {setFile(null); setError("");}}><X size={15}/> CLEAR FILE</button><button className="button secondary" onClick={runSampleAnalysis} disabled={busy}><Sparkles size={15}/> LOAD SAMPLE DATASET</button><button className="button primary" onClick={runAnalysis} disabled={!file || busy}>{busy ? <><LoaderCircle className="spin" size={17}/> ANALYSING…</> : <>LAUNCH ANALYSIS PIPELINE <ArrowRight size={17}/></>}</button></div>
        {error && <div className="error"><AlertTriangle size={18}/><div><strong>ANALYSIS FAILED</strong><p>{error}</p></div></div>}
        {busy && <div className="progress"><span /></div>}
      </section>

      {result && <section className="results">
        <div className="section-top"><div><p className="eyebrow">02 — INTELLIGENCE</p><h2>{tab === "overview" ? "EXECUTIVE OVERVIEW" : tab === "issues" ? "PRIORITY ISSUES" : "REVIEW EXPLORER"}</h2></div><button className="button secondary" onClick={downloadBriefDocx}><Download size={15}/> DOWNLOAD BRIEF (.DOCX)</button></div>
        <div className="product-switcher">
          <label htmlFor="product-select"><span className="eyebrow">ANALYSIS SCOPE</span><strong>PRODUCT / BRAND</strong></label>
          <select id="product-select" value={result.selected_product || "__all__"} disabled={productBusy} onChange={(e) => void selectProduct(e.target.value)}>
            <option value="__all__">All products</option>
            {result.products.map((product) => <option value={product} key={product}>{product}</option>)}
          </select>
          {productBusy && <span className="muted">Recalculating insights…</span>}
        </div>
        {tab === "overview" && <>
        <div className="metrics">
          <Metric icon={<FileText size={18}/>} label="REVIEWS ANALYSED" value={fmt(result.summary.review_count)} note={`${fmt(result.rows_received)} rows received`} />
          <Metric icon={<Gauge size={18}/>} label="AVERAGE RATING" value={`${fmt(result.summary.average_rating)} / 5`} note={result.rating_estimated ? "Estimated from text" : "Source ratings"} />
          <Metric icon={<ShieldAlert size={18}/>} label="QUALITY FLAGS" value={fmt(result.summary.flagged_count)} note="Duplicate / short / repetitive" />
          <Metric icon={<Activity size={18}/>} label="NEGATIVE MENTIONS" value={`${fmt(result.summary.negative_share)}%`} note="Across detected aspects" />
        </div>
        {result.notes.length > 0 && <div className="notes"><strong>PROCESSING NOTES</strong>{result.notes.map((n,i)=><p key={i}>— {n}</p>)}</div>}
        {result.discovered_topics.length > 0 && <div className="notes"><strong>DISCOVERED PRODUCT TOPICS</strong><p>{result.discovered_topics.join(" · ")}</p></div>}
        <section className="panel brief-panel"><div className="section-top"><div><p className="eyebrow">PRODUCT MANAGER BRIEF</p><h2>RECOMMENDATIONS & EVIDENCE</h2></div><button className="button primary" onClick={downloadBriefDocx}><Download size={15}/> DOWNLOAD WORD FILE</button></div><div className="brief-content">{result.brief.split("\n").map((line, i) => { const text = line.replace(/\*\*/g, "").replace(/^#+\s?/, "").trim(); if (!text) return <div className="brief-spacer" key={i}/>; if (line.startsWith("# ")) return <h3 key={i}>{text}</h3>; if (line.startsWith("## ")) return <h4 key={i}>{text}</h4>; return <p key={i}>{text.replace(/^[-]\s+/, "• ")}</p>; })}</div></section>
        <div className="summary-grid"><div className="panel"><p className="eyebrow">KEY FINDINGS</p>{result.executive_summary.map((s,i)=><p className="finding" key={i}><span className="finding-mark">0{i+1}</span>{s}</p>)}</div><div className="panel"><p className="eyebrow">ASPECT SENTIMENT</p>{result.aspects.length ? result.aspects.map((a,i)=><div className="aspect-row" key={String(a.aspect ?? i)}><div className="aspect-label"><span>{String(a.aspect).toUpperCase()}</span><b>{Number(a.net ?? 0).toFixed(2)}</b></div><div className="bar-track"><div className="bar-fill" style={{width:`${Math.max(0,Math.min(100,(Number(a.net ?? 0)+1)*50))}%`}} /></div><small>{fmt(a.mentions)} mentions</small></div>) : <p className="muted">No aspect mentions detected.</p>}</div></div>
        </>}
        {tab === "issues" && <div className="panel"><div className="section-top"><div><p className="eyebrow">02 — ACTION PLAN</p><h2>PRIORITY ISSUES</h2><p className="muted">Ranked by prevalence, severity, trend and rating impact. Use the evidence to assign an owner and validate the fix.</p></div></div><IssueTable rows={result.issues}/></div>}
        {tab === "overview" && <div className="panel"><p className="eyebrow">TOP PRIORITY ISSUES</p><IssueTable rows={result.issues.slice(0,5)}/></div>}
        {tab === "overview" && <div className="summary-grid"><div className="panel"><p className="eyebrow">EMERGING ISSUE ALERTS</p>{result.alerts.length ? result.alerts.map((a,i)=><p className="finding" key={i}><AlertTriangle size={16} className="gold-icon"/><span><b>{a.brand} / {a.aspect}</b> — {fmt(a.spike)}× baseline ({fmt(a.recent)} recent mentions)</span></p>) : <p className="muted">No emerging spikes detected from available dates.</p>}</div><div className="panel"><p className="eyebrow">RISK SIGNALS</p>{result.risks.map((r,i)=><div className="risk-row" key={i}><span>{r.category}</span><b>{fmt(r.reviews)} <small>({Number(r.pct ?? 0).toFixed(1)}%)</small></b></div>)}</div></div>}
        {tab === "overview" && <div className="summary-grid"><div className="panel"><p className="eyebrow">WHAT MOVES THE RATING</p>{result.drivers.length ? result.drivers.slice(0,6).map((r,i)=><div className="risk-row" key={i}><span>{r.aspect}</span><b>+{Number(r.gain ?? 0).toFixed(2)} stars potential</b></div>) : <p className="muted">Not enough labelled reviews to estimate rating drivers reliably.</p>}</div><div className="panel"><p className="eyebrow">WEEKLY ASPECT SENTIMENT</p>{result.trends.length ? result.trends.slice(-10).map((r,i)=><div className="risk-row" key={i}><span>{String(r.week ?? "").slice(0,10)} / {r.aspect}</span><b>{Number(r.net ?? 0).toFixed(2)}</b></div>) : <p className="muted">Weekly trends need usable dates and detected aspect mentions.</p>}</div></div>}
        {tab === "overview" && <div className="summary-grid"><div className="panel"><p className="eyebrow">COMPLAINTS THAT TRAVEL TOGETHER</p>{result.cooccurrence.length ? result.cooccurrence.slice(0,6).map((r,i)=><div className="risk-row" key={i}><span>{r.a} + {r.b}</span><b>{fmt(r.reviews)} reviews</b></div>) : <p className="muted">Not enough repeated co-occurrence evidence detected.</p>}</div><div className="panel"><p className="eyebrow">WORDS SIGNALING TROUBLE</p>{result.signal_words.length ? result.signal_words.slice(0,8).map((r,i)=><div className="risk-row" key={i}><span>{r.word}</span><b>{Number(r.times_more_common ?? 0).toFixed(1)}×</b></div>) : <p className="muted">No words met the minimum evidence threshold.</p>}</div></div>}
      </section>}

      {result && tab === "reviews" && <section className="panel review-panel"><div className="section-top"><div><p className="eyebrow">03 — EVIDENCE</p><h2>REVIEW EXPLORER</h2></div><span className="tiny-note">SHOWING UP TO 500 LOADED REVIEWS</span></div><div className="searchbox"><Search size={17}/><input value={searchQuery} onChange={(e)=>{setSearchQuery(e.target.value);setServerSearchResults(null);}} onKeyDown={(e)=>{if(e.key==="Enter") void searchAllReviews();}} placeholder="Search review text, brand, rating…" /><button className="search-submit" onClick={searchAllReviews} disabled={!searchQuery.trim() || searchBusy}>{searchBusy ? "SEARCHING…" : "SEARCH ALL"}</button></div>{searchError && <div className="error"><AlertTriangle size={18}/><p>{searchError}</p></div>}{serverSearchResults && <p className="muted">Semantic keyword search across the analysed review set — {serverSearchResults.length} matches.</p>}<div className="table-wrap"><table><thead><tr><th>BRAND</th><th>RATING</th><th>DATE</th><th>REVIEW</th><th>FLAG</th></tr></thead><tbody>{filteredReviews.map((r,i)=><tr key={String(r.review_id ?? i)}><td>{String(r.brand ?? "—")}</td><td>{fmt(r.rating)} / 5</td><td>{String(r.date ?? "—").slice(0,10)}</td><td className="review-text">{String(r.review_text ?? "")}</td><td>{r.flagged ? <span className="flag">FLAGGED</span> : "—"}</td></tr>)}</tbody></table></div></section>}


      <footer><span>REVIEW<span className="gold">LENS</span> / LOCAL ANALYTICS</span><span>DECISIONS BACKED BY EVIDENCE.</span></footer>
    </main>
  </div>;
}

function Metric({icon,label,value,note}:{icon:ReactNode;label:string;value:string;note:string}) {
  return <div className="metric"><div className="metric-top">{icon}<span>{label}</span></div><strong>{value}</strong><small>{note}</small></div>;
}
function IssueTable({rows}:{rows:RecordRow[]}) {
  if (!rows.length) return <div className="empty-insight"><strong>NO HIGH-CONFIDENCE ISSUE CLUSTERS YET</strong><p>ReviewLens needs repeated negative comments about the same topic to rank a fix. Check the Review Explorer for raw feedback, confirm the review-text and rating columns were detected correctly, and upload more reviews if this sample is small.</p></div>;
  return <div className="table-wrap"><table><thead><tr><th>PRIORITY</th><th>ASPECT</th><th>ISSUE</th><th>REVIEWS</th><th>RECOMMENDED ACTION</th><th>OWNER</th><th>EVIDENCE</th></tr></thead><tbody>{rows.map((r,i)=><tr key={i}><td><span className="priority">{fmt(r.priority)}</span></td><td>{String(r.aspect ?? "")}</td><td>{String(r.issue ?? "")}<small className="block">{String(r.pct_reviews ?? 0)}% of reviews</small></td><td>{fmt(r.reviews)}</td><td>{String(r.action ?? "Investigate recurring feedback and validate the root cause.")}</td><td>{String(r.owner ?? "Product")}</td><td className="review-text">{Array.isArray(r.quotes) ? (r.quotes as string[]).join(" “ ") : ""}</td></tr>)}</tbody></table></div>;
}
