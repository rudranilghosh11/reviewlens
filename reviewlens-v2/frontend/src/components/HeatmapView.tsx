import React, { useEffect, useState } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';
import { getHeatmap } from '../api/client';
import type { HeatmapData } from '../types/analysis';

interface HeatmapViewProps {
  analysisId: string;
}

export const HeatmapView: React.FC<HeatmapViewProps> = ({ analysisId }) => {
  const [data, setData] = useState<HeatmapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchMatrix = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await getHeatmap(analysisId);
        if (mounted) setData(res);
      } catch (err: any) {
        if (mounted) setError(err.message || 'Failed to load competitor heatmap.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchMatrix();
    return () => { mounted = false; };
  }, [analysisId]);

  if (loading) {
    return (
      <div className="telemetry-card" style={{ padding: 60, textAlign: 'center' }}>
        <Loader2 size={32} className="animate-spin" style={{ color: 'var(--lambo-gold)', margin: '0 auto 16px' }} />
        <div style={{ fontFamily: 'var(--font-display)', color: 'var(--text-smoke)', letterSpacing: '0.1em' }}>
          COMPUTING CROSS-BRAND NET SENTIMENT HEATMAP...
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="telemetry-card" style={{ padding: 32, textAlign: 'center', color: 'var(--danger-red)' }}>
        <AlertCircle size={24} style={{ margin: '0 auto 12px' }} />
        <div>{error || 'No brand matrix data available.'}</div>
      </div>
    );
  }

  const getCellBg = (val: number | null) => {
    if (val === null || val === undefined) return 'var(--bg-surface-2)';
    if (val > 0.4) return 'rgba(0, 230, 118, 0.25)';
    if (val > 0.1) return 'rgba(0, 230, 118, 0.12)';
    if (val >= -0.1) return 'rgba(255, 255, 255, 0.04)';
    if (val >= -0.4) return 'rgba(255, 51, 75, 0.15)';
    return 'rgba(255, 51, 75, 0.35)';
  };

  const getCellColor = (val: number | null) => {
    if (val === null || val === undefined) return 'var(--text-dark)';
    if (val > 0.1) return 'var(--success-green)';
    if (val >= -0.1) return 'var(--text-smoke)';
    return 'var(--danger-red)';
  };

  return (
    <div className="telemetry-card" style={{ padding: 24, marginBottom: 32 }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 24,
        flexWrap: 'wrap',
        gap: 12,
      }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', letterSpacing: '0.1em' }}>
            <span style={{ color: 'var(--lambo-gold)' }}>COMPETITOR BENCHMARK HEATMAP</span>
          </h2>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Net aspect sentiment score matrix across identified brand entities.
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16, fontSize: '0.72rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 14, height: 14, backgroundColor: 'rgba(0, 230, 118, 0.3)', border: '1px solid var(--success-green)' }} />
            <span style={{ color: 'var(--text-smoke)' }}>Advantage (&gt;+0.1)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 14, height: 14, backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-strong)' }} />
            <span style={{ color: 'var(--text-muted)' }}>Neutral</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 14, height: 14, backgroundColor: 'rgba(255, 51, 75, 0.3)', border: '1px solid var(--danger-red)' }} />
            <span style={{ color: 'var(--text-smoke)' }}>Disadvantage (&lt;-0.1)</span>
          </div>
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="data-table" style={{ textAlign: 'center' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', minWidth: 160 }}>BRAND / ENTITY</th>
              {data.aspects.map((asp, idx) => (
                <th key={idx} style={{ minWidth: 100, textTransform: 'capitalize' }}>
                  {asp}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.brands.map((brand, bIdx) => (
              <tr key={bIdx}>
                <td style={{
                  textAlign: 'left',
                  fontWeight: 700,
                  fontFamily: 'var(--font-display)',
                  fontSize: '0.9rem',
                  color: '#FFFFFF',
                  backgroundColor: 'var(--bg-surface-2)',
                }}>
                  {brand}
                </td>
                {data.aspects.map((asp, aIdx) => {
                  const val = data.matrix[brand]?.[asp] ?? null;
                  return (
                    <td
                      key={aIdx}
                      style={{
                        backgroundColor: getCellBg(val),
                        color: getCellColor(val),
                        fontFamily: 'var(--font-mono)',
                        fontWeight: 700,
                        fontSize: '0.85rem',
                      }}
                    >
                      {val !== null ? (val > 0 ? `+${val.toFixed(2)}` : val.toFixed(2)) : '—'}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
