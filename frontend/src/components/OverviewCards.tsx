import React from 'react';
import { Star, Sparkles } from 'lucide-react';
import type { AnalysisOverview } from '../types/analysis';

interface OverviewCardsProps {
  overview: AnalysisOverview;
  executiveSummary: string[];
  discoveredTopics: string[];
}

export const OverviewCards: React.FC<OverviewCardsProps> = ({
  overview,
  executiveSummary,
  discoveredTopics,
}) => {
  return (
    <div style={{ marginBottom: 32 }}>
      {/* Executive Summary Telemetry Panel */}
      {executiveSummary && executiveSummary.length > 0 && (
        <div
          className="telemetry-card highlight-gold"
          style={{
            padding: 24,
            marginBottom: 24,
            backgroundColor: 'var(--bg-surface-card)',
          }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            marginBottom: 12,
          }}>
            <Sparkles size={16} style={{ color: 'var(--lambo-gold)' }} />
            <span style={{
              fontFamily: 'var(--font-display)',
              fontSize: '0.8rem',
              fontWeight: 700,
              color: 'var(--lambo-gold)',
              letterSpacing: '0.12em',
            }}>
              EXECUTIVE TELEMETRY BRIEFING // KEY FINDINGS
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {executiveSummary.map((line, idx) => (
              <div
                key={idx}
                style={{
                  fontSize: '0.92rem',
                  color: 'var(--text-smoke)',
                  lineHeight: 1.6,
                  borderLeft: '2px solid var(--border-strong)',
                  paddingLeft: 12,
                }}
              >
                {line}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Primary KPI Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
        gap: 16,
      }}>
        {/* Total Reviews */}
        <div className="telemetry-card" style={{ padding: 20 }}>
          <div style={{
            fontSize: '0.72rem',
            color: 'var(--text-muted)',
            fontFamily: 'var(--font-display)',
            letterSpacing: '0.1em',
            marginBottom: 6,
          }}>
            DATASET VOLUME
          </div>
          <div style={{
            fontSize: '1.85rem',
            fontFamily: 'var(--font-display)',
            fontWeight: 800,
            color: '#FFFFFF',
          }}>
            {overview.total_reviews.toLocaleString()}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-smoke)', marginTop: 4 }}>
            Total Ingested Records
          </div>
        </div>

        {/* Usable / Cleaned Reviews */}
        <div className="telemetry-card highlight-cyan" style={{ padding: 20 }}>
          <div style={{
            fontSize: '0.72rem',
            color: 'var(--text-muted)',
            fontFamily: 'var(--font-display)',
            letterSpacing: '0.1em',
            marginBottom: 6,
          }}>
            CLEANED & AUDITED
          </div>
          <div style={{
            fontSize: '1.85rem',
            fontFamily: 'var(--font-display)',
            fontWeight: 800,
            color: 'var(--cyan-pulse)',
          }}>
            {overview.usable_reviews.toLocaleString()}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
            {overview.flagged_reviews > 0 ? (
              <span style={{ color: 'var(--danger-red)' }}>
                {overview.flagged_reviews} spam/empty excluded
              </span>
            ) : (
              '100% Signal Purity'
            )}
          </div>
        </div>

        {/* Average Rating */}
        <div className="telemetry-card highlight-gold" style={{ padding: 20 }}>
          <div style={{
            fontSize: '0.72rem',
            color: 'var(--text-muted)',
            fontFamily: 'var(--font-display)',
            letterSpacing: '0.1em',
            marginBottom: 6,
          }}>
            CUSTOMER SENTIMENT
          </div>
          <div style={{
            fontSize: '1.85rem',
            fontFamily: 'var(--font-display)',
            fontWeight: 800,
            color: 'var(--lambo-gold)',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}>
            {overview.avg_rating.toFixed(2)}
            <Star size={20} fill="var(--lambo-gold)" color="var(--lambo-gold)" />
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-smoke)', marginTop: 4 }}>
            {overview.rating_estimated ? 'Estimated from VADER' : '5-Star Benchmark'}
          </div>
        </div>

        {/* Brands Analysed */}
        <div className="telemetry-card" style={{ padding: 20 }}>
          <div style={{
            fontSize: '0.72rem',
            color: 'var(--text-muted)',
            fontFamily: 'var(--font-display)',
            letterSpacing: '0.1em',
            marginBottom: 6,
          }}>
            BRANDS BENCHMARKED
          </div>
          <div style={{
            fontSize: '1.85rem',
            fontFamily: 'var(--font-display)',
            fontWeight: 800,
            color: '#FFFFFF',
          }}>
            {overview.brands.length}
          </div>
          <div style={{
            fontSize: '0.75rem',
            color: 'var(--text-smoke)',
            marginTop: 4,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            {overview.brands.join(', ')}
          </div>
        </div>

        {/* Date Window */}
        {overview.has_dates && overview.date_range && overview.date_range[0] && (
          <div className="telemetry-card" style={{ padding: 20 }}>
            <div style={{
              fontSize: '0.72rem',
              color: 'var(--text-muted)',
              fontFamily: 'var(--font-display)',
              letterSpacing: '0.1em',
              marginBottom: 6,
            }}>
              OBSERVATION WINDOW
            </div>
            <div style={{
              fontSize: '1.1rem',
              fontFamily: 'var(--font-display)',
              fontWeight: 700,
              color: '#FFFFFF',
              marginTop: 6,
            }}>
              {overview.date_range[0]}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
              to {overview.date_range[1]}
            </div>
          </div>
        )}
      </div>

      {/* Discovered Aspects Pill Bar */}
      {discoveredTopics && discoveredTopics.length > 0 && (
        <div style={{
          marginTop: 16,
          padding: '12px 16px',
          backgroundColor: 'var(--bg-surface-2)',
          border: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          flexWrap: 'wrap',
        }}>
          <span style={{
            fontSize: '0.72rem',
            fontFamily: 'var(--font-display)',
            color: 'var(--lambo-gold)',
            fontWeight: 700,
            letterSpacing: '0.1em',
          }}>
            DISCOVERED TOPICS:
          </span>
          {discoveredTopics.map((t, idx) => (
            <span key={idx} className="telemetry-badge badge-neutral">
              {t}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
