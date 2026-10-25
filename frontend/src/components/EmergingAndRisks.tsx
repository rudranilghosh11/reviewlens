import React from 'react';
import { Flame, ShieldAlert, Target, Zap } from 'lucide-react';
import type { EmergingAlert, RiskSignal, KeyDriver, SignalWord } from '../types/analysis';

interface EmergingAndRisksProps {
  alerts: EmergingAlert[];
  risks: RiskSignal[];
  drivers: KeyDriver[];
  signalWords: SignalWord[];
  r2: number;
}

export const EmergingAndRisks: React.FC<EmergingAndRisksProps> = ({
  alerts,
  risks,
  drivers,
  signalWords,
  r2,
}) => {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))',
      gap: 24,
      marginBottom: 32,
    }}>
      {/* Emerging Alerts & Velocity Spikes */}
      <div className="telemetry-card" style={{ padding: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <Flame size={18} style={{ color: 'var(--danger-red)' }} />
          <div>
            <h3 style={{ fontSize: '1rem', letterSpacing: '0.08em', color: '#FFFFFF' }}>
              EMERGING VELOCITY SPIKES
            </h3>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Topics exceeding baseline frequency in the most recent window.
            </div>
          </div>
        </div>

        {alerts && alerts.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {alerts.map((al, idx) => (
              <div
                key={idx}
                style={{
                  padding: '12px 16px',
                  backgroundColor: 'var(--bg-surface-2)',
                  borderLeft: '3px solid var(--danger-red)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', fontSize: '0.85rem' }}>
                    {al.brand} // {al.aspect}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Recent mentions: {al.recent} (Expected baseline: {al.expected.toFixed(1)})
                  </div>
                </div>
                <span className="telemetry-badge badge-red" style={{ fontSize: '0.8rem' }}>
                  {al.spike.toFixed(1)}x SPIKE
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem', padding: '16px 0' }}>
            No statistically significant emerging spikes detected in current date window.
          </div>
        )}
      </div>

      {/* High-Risk Category Signals */}
      <div className="telemetry-card" style={{ padding: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <ShieldAlert size={18} style={{ color: 'var(--warning-amber)' }} />
          <div>
            <h3 style={{ fontSize: '1rem', letterSpacing: '0.08em', color: '#FFFFFF' }}>
              HIGH-STAKES RISK SIGNALS
            </h3>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Specific safety, legal, warranty, and churn triggers.
            </div>
          </div>
        </div>

        {risks && risks.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {risks.map((rk, idx) => (
              <div
                key={idx}
                style={{
                  padding: '12px 16px',
                  backgroundColor: 'var(--bg-surface-2)',
                  borderLeft: `3px solid ${rk.color === 'red' ? 'var(--danger-red)' : 'var(--warning-amber)'}`,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <span style={{ fontWeight: 700, textTransform: 'uppercase', fontSize: '0.85rem', color: '#FFFFFF' }}>
                    {rk.category}
                  </span>
                  <span className={`telemetry-badge ${rk.color === 'red' ? 'badge-red' : 'badge-gold'}`}>
                    {rk.reviews} reviews ({rk.pct.toFixed(1)}%)
                  </span>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-smoke)', fontStyle: 'italic' }}>
                  &ldquo;{rk.example}&rdquo;
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem', padding: '16px 0' }}>
            No high-stakes risk triggers matched.
          </div>
        )}
      </div>

      {/* Key Drivers of Rating Gain */}
      <div className="telemetry-card" style={{ padding: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <Target size={18} style={{ color: 'var(--lambo-gold)' }} />
          <div>
            <h3 style={{ fontSize: '1rem', letterSpacing: '0.08em', color: '#FFFFFF' }}>
              KEY DRIVERS OF RATING DRAG
            </h3>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              OLS regression model (R² = {(r2 * 100).toFixed(1)}% explained variance).
            </div>
          </div>
        </div>

        {drivers && drivers.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {drivers.slice(0, 5).map((dr, idx) => (
              <div
                key={idx}
                style={{
                  padding: '10px 14px',
                  backgroundColor: 'var(--bg-surface-2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ fontWeight: 700, textTransform: 'uppercase', fontSize: '0.82rem', color: '#FFFFFF' }}>
                    Fix {dr.aspect}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    {dr.reviews_negative} negative reviews ({dr.share_negative.toFixed(1)}% share)
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ color: 'var(--success-green)', fontWeight: 700, fontSize: '0.85rem' }}>
                    +{dr.gain.toFixed(2)} ★
                  </span>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                    Est. Star Lift
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
            Regression model requires non-estimated ratings.
          </div>
        )}
      </div>

      {/* Signal Words in Negative Reviews */}
      <div className="telemetry-card" style={{ padding: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <Zap size={18} style={{ color: 'var(--cyan-pulse)' }} />
          <div>
            <h3 style={{ fontSize: '1rem', letterSpacing: '0.08em', color: '#FFFFFF' }}>
              HIGH-IMPACT SIGNAL WORDS
            </h3>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Words far more prevalent in complaints than praises.
            </div>
          </div>
        </div>

        {signalWords && signalWords.length > 0 ? (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {signalWords.map((sw, idx) => (
              <div
                key={idx}
                style={{
                  padding: '6px 12px',
                  backgroundColor: 'var(--bg-surface-2)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 700,
                  fontSize: '0.82rem',
                  color: 'var(--cyan-pulse)',
                }}>
                  {sw.word}
                </span>
                <span style={{ fontSize: '0.72rem', color: 'var(--danger-red)', fontWeight: 600 }}>
                  {sw.times_more_common.toFixed(1)}x
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
            No distinct signal words isolated at current mention thresholds.
          </div>
        )}
      </div>
    </div>
  );
};
