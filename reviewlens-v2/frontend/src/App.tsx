import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { UploadHero } from './components/UploadHero';
import { OverviewCards } from './components/OverviewCards';
import { IssuesTable } from './components/IssuesTable';
import { AspectsCard } from './components/AspectsCard';
import { EmergingAndRisks } from './components/EmergingAndRisks';
import { HeatmapView } from './components/HeatmapView';
import { SearchExplorer } from './components/SearchExplorer';
import { BriefView } from './components/BriefView';
import { checkHealth } from './api/client';
import type { AnalysisResult } from './types/analysis';

function App() {
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'heatmap' | 'search' | 'brief'>('dashboard');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const verifyBackend = async () => {
      try {
        await checkHealth();
        setBackendOnline(true);
      } catch (e) {
        setBackendOnline(false);
      }
    };
    verifyBackend();
    const interval = setInterval(verifyBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleNewAnalysis = () => {
    setAnalysis(null);
    setActiveTab('dashboard');
    setError(null);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#000000' }}>
      <Navbar
        backendOnline={backendOnline}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        hasAnalysis={!!analysis}
        onNewAnalysis={handleNewAnalysis}
      />

      <main style={{ flex: 1, padding: '32px 24px', maxWidth: 1440, margin: '0 auto', width: '100%' }}>
        {!analysis ? (
          <UploadHero
            onAnalysisComplete={(res) => {
              setAnalysis(res);
              setActiveTab('dashboard');
            }}
            loading={loading}
            setLoading={setLoading}
            error={error}
            setError={setError}
          />
        ) : (
          <div>
            {/* Always visible top-level KPIs & Executive summary */}
            <OverviewCards
              overview={analysis.overview}
              executiveSummary={analysis.executive_summary}
              discoveredTopics={analysis.discovered_topics}
            />

            {/* Tab 01: Dashboard & Issues */}
            {activeTab === 'dashboard' && (
              <div>
                <IssuesTable issues={analysis.issues} />
                <AspectsCard aspects={analysis.aspect_summary} />
                <EmergingAndRisks
                  alerts={analysis.emerging_alerts}
                  risks={analysis.risk_signals}
                  drivers={analysis.key_drivers}
                  signalWords={analysis.signal_words}
                  r2={analysis.key_drivers_r2}
                />
              </div>
            )}

            {/* Tab 02: Competitor Heatmap */}
            {activeTab === 'heatmap' && (
              <HeatmapView analysisId={analysis.analysis_id} />
            )}

            {/* Tab 03: Evidence Explorer & TF-IDF Search */}
            {activeTab === 'search' && (
              <SearchExplorer
                analysisId={analysis.analysis_id}
                brands={analysis.overview.brands}
              />
            )}

            {/* Tab 04: Executive PM Brief */}
            {activeTab === 'brief' && (
              <BriefView analysisId={analysis.analysis_id} />
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        padding: '24px',
        backgroundColor: '#080808',
        fontSize: '0.72rem',
        color: 'var(--text-dark)',
        textAlign: 'center',
        fontFamily: 'var(--font-display)',
        letterSpacing: '0.1em',
      }}>
        <div style={{ maxWidth: 1440, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div>
            REVIEW LENS V2.0 // NOCTURNAL PERFORMANCE SPECIFICATION
          </div>
          <div>
            FASTAPI + REACT + VADER + TF-IDF RETRIEVAL ENGINE
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
