import React from 'react';
import type { AspectSentiment } from '../types/analysis';

interface AspectsCardProps {
  aspects: AspectSentiment[];
}

export const AspectsCard: React.FC<AspectsCardProps> = ({ aspects }) => {
  return (
    <div className="telemetry-card" style={{ padding: 24, marginBottom: 32 }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 20,
        flexWrap: 'wrap',
        gap: 12,
      }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', letterSpacing: '0.1em' }}>
            <span style={{ color: 'var(--cyan-pulse)' }}>ASPECT SENTIMENT BREAKDOWN</span>
          </h2>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Net sentiment = (% Positive - % Negative) across all parsed clauses.
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16, fontSize: '0.72rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 10, height: 10, backgroundColor: 'var(--success-green)' }} />
            <span style={{ color: 'var(--text-smoke)' }}>Positive</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 10, height: 10, backgroundColor: 'var(--text-dark)' }} />
            <span style={{ color: 'var(--text-muted)' }}>Neutral</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 10, height: 10, backgroundColor: 'var(--danger-red)' }} />
            <span style={{ color: 'var(--text-smoke)' }}>Negative</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {aspects.map((asp, idx) => {
          const total = Math.max(asp.mentions, 1);
          const posPct = ((asp.pos / total) * 100);
          const neuPct = ((asp.neu / total) * 100);
          const negPct = ((asp.neg / total) * 100);

          return (
            <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.82rem',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{
                    fontFamily: 'var(--font-display)',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: '#FFFFFF',
                    letterSpacing: '0.08em',
                  }}>
                    {asp.aspect}
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    ({asp.mentions.toLocaleString()} mentions)
                  </span>
                </div>

                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  color: asp.net > 0 ? 'var(--success-green)' : asp.net < 0 ? 'var(--danger-red)' : 'var(--text-smoke)',
                }}>
                  {asp.net > 0 ? `+${asp.net.toFixed(2)}` : asp.net.toFixed(2)} NET
                </div>
              </div>

              {/* Segmented bar */}
              <div style={{
                display: 'flex',
                height: 8,
                backgroundColor: 'var(--bg-surface-3)',
                overflow: 'hidden',
              }}>
                <div style={{ width: `${posPct}%`, backgroundColor: 'var(--success-green)' }} />
                <div style={{ width: `${neuPct}%`, backgroundColor: 'var(--text-dark)' }} />
                <div style={{ width: `${negPct}%`, backgroundColor: 'var(--danger-red)' }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
