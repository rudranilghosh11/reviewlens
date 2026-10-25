import React from 'react';
import { FileText, LayoutDashboard, Search, Grid } from 'lucide-react';

interface NavbarProps {
  backendOnline: boolean | null;
  activeTab: 'dashboard' | 'heatmap' | 'search' | 'brief';
  setActiveTab: (tab: 'dashboard' | 'heatmap' | 'search' | 'brief') => void;
  hasAnalysis: boolean;
  onNewAnalysis: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  backendOnline,
  activeTab,
  setActiveTab,
  hasAnalysis,
  onNewAnalysis,
}) => {
  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      backgroundColor: '#000000',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      padding: '0 24px',
    }}>
      <div style={{
        maxWidth: 1440,
        margin: '0 auto',
        height: 72,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 24,
      }}>
        {/* Brand & Mark */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{
            width: 36,
            height: 36,
            backgroundColor: '#000000',
            border: '2px solid var(--lambo-gold)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
          }}>
            <div style={{
              width: 14,
              height: 14,
              backgroundColor: 'var(--lambo-gold)',
              clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
            }} />
          </div>
          <div>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.25rem',
              fontWeight: 800,
              letterSpacing: '0.14em',
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}>
              REVIEW LENS <span style={{ color: 'var(--lambo-gold)' }}>V2</span>
            </div>
            <div style={{
              fontSize: '0.65rem',
              color: 'var(--text-muted)',
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              fontWeight: 600,
            }}>
              Customer Voice Intelligence
            </div>
          </div>
        </div>

        {/* Navigation Tabs (Available once analysis is loaded) */}
        {hasAnalysis && (
          <nav style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`btn-ghost ${activeTab === 'dashboard' ? 'active' : ''}`}
              style={{ padding: '8px 16px', fontSize: '0.78rem' }}
            >
              <LayoutDashboard size={14} />
              01 // Issues & Metrics
            </button>
            <button
              onClick={() => setActiveTab('heatmap')}
              className={`btn-ghost ${activeTab === 'heatmap' ? 'active' : ''}`}
              style={{ padding: '8px 16px', fontSize: '0.78rem' }}
            >
              <Grid size={14} />
              02 // Brand Heatmap
            </button>
            <button
              onClick={() => setActiveTab('search')}
              className={`btn-ghost ${activeTab === 'search' ? 'active' : ''}`}
              style={{ padding: '8px 16px', fontSize: '0.78rem' }}
            >
              <Search size={14} />
              03 // Evidence Search
            </button>
            <button
              onClick={() => setActiveTab('brief')}
              className={`btn-ghost ${activeTab === 'brief' ? 'active' : ''}`}
              style={{ padding: '8px 16px', fontSize: '0.78rem' }}
            >
              <FileText size={14} />
              04 // PM Brief
            </button>
          </nav>
        )}

        {/* Status & Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {hasAnalysis && (
            <button
              onClick={onNewAnalysis}
              className="btn-subtle"
              style={{ fontSize: '0.72rem', padding: '6px 14px' }}
            >
              New Dataset
            </button>
          )}

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '6px 12px',
            backgroundColor: 'var(--bg-surface-1)',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.72rem',
            fontFamily: 'var(--font-display)',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
          }}>
            <span
              className="pulse-indicator"
              style={{
                backgroundColor: backendOnline === true ? 'var(--success-green)' : backendOnline === false ? 'var(--danger-red)' : 'var(--lambo-gold)',
              }}
            />
            <span style={{ color: 'var(--text-smoke)' }}>
              {backendOnline === true ? 'Engine Online' : backendOnline === false ? 'Engine Offline' : 'Connecting'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
