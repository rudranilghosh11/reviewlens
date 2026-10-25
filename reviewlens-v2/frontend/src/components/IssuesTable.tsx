import React, { useState } from 'react';
import { ChevronDown, ChevronRight, TrendingUp, Quote } from 'lucide-react';
import type { Issue } from '../types/analysis';

interface IssuesTableProps {
  issues: Issue[];
}

export const IssuesTable: React.FC<IssuesTableProps> = ({ issues }) => {
  const [expandedIdx, setExpandedIdx] = useState<number | null>(0);

  if (!issues || issues.length === 0) {
    return (
      <div className="telemetry-card" style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)' }}>
        No critical issue clusters found in this dataset.
      </div>
    );
  }

  const getPriorityBadgeClass = (priority: number) => {
    if (priority >= 70) return 'badge-red';
    if (priority >= 40) return 'badge-gold';
    return 'badge-neutral';
  };

  return (
    <div className="telemetry-card" style={{ marginBottom: 32 }}>
      {/* Table Header */}
      <div style={{
        padding: '20px 24px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 12,
      }}>
        <div>
          <h2 style={{
            fontSize: '1.15rem',
            letterSpacing: '0.1em',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
          }}>
            <span style={{ color: 'var(--lambo-gold)' }}>PRIORITY FIX-FIRST MATRIX</span>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              ({issues.length} ACTIONABLE CLUSTERS)
            </span>
          </h2>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Ranked by customer volume × severity × rating drag × trend growth.
          </div>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <span className="telemetry-badge badge-red">CRITICAL (70+)</span>
          <span className="telemetry-badge badge-gold">ELEVATED (40-69)</span>
          <span className="telemetry-badge badge-neutral">STANDARD (&lt;40)</span>
        </div>
      </div>

      {/* Table List */}
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: 60 }}>PRI</th>
              <th>ISSUE DESCRIPTION</th>
              <th>ASPECT</th>
              <th>VOLUME</th>
              <th>RATING DRAG</th>
              <th>SPIKE / TREND</th>
              <th>OWNER & ACTION</th>
              <th style={{ width: 40 }}></th>
            </tr>
          </thead>
          <tbody>
            {issues.map((issue, idx) => {
              const isExpanded = expandedIdx === idx;
              return (
                <React.Fragment key={idx}>
                  <tr
                    onClick={() => setExpandedIdx(isExpanded ? null : idx)}
                    style={{
                      cursor: 'pointer',
                      backgroundColor: isExpanded ? 'rgba(255,192,0,0.03)' : 'transparent',
                    }}
                  >
                    {/* Priority score */}
                    <td>
                      <span className={`telemetry-badge ${getPriorityBadgeClass(issue.priority)}`}>
                        #{idx + 1} ({issue.priority})
                      </span>
                    </td>

                    {/* Issue name */}
                    <td style={{ fontWeight: 600, color: '#FFFFFF' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        {issue.issue}
                      </div>
                    </td>

                    {/* Aspect */}
                    <td>
                      <span className="telemetry-badge badge-neutral" style={{ textTransform: 'capitalize' }}>
                        {issue.aspect}
                      </span>
                    </td>

                    {/* Volume */}
                    <td>
                      <div>
                        <span style={{ color: '#FFFFFF', fontWeight: 700 }}>{issue.reviews}</span>{' '}
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          ({issue.pct_reviews.toFixed(1)}%)
                        </span>
                      </div>
                    </td>

                    {/* Drag on rating */}
                    <td>
                      <span style={{
                        color: issue.rating_drag > 0.5 ? 'var(--danger-red)' : 'var(--text-smoke)',
                        fontWeight: 700,
                      }}>
                        -{issue.rating_drag.toFixed(2)} ★
                      </span>
                    </td>

                    {/* Trend */}
                    <td>
                      {issue.dated ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                          {issue.trend > 0 ? (
                            <span style={{ color: 'var(--danger-red)', display: 'flex', alignItems: 'center', gap: 2 }}>
                              <TrendingUp size={12} />
                              +{(issue.trend * 100).toFixed(0)}%
                            </span>
                          ) : (
                            <span style={{ color: 'var(--text-muted)' }}>Stable</span>
                          )}
                        </div>
                      ) : (
                        <span style={{ color: 'var(--text-dark)' }}>N/A</span>
                      )}
                    </td>

                    {/* Owner & Recommended Action */}
                    <td>
                      <div style={{ fontSize: '0.78rem' }}>
                        <div style={{ color: 'var(--lambo-gold)', fontWeight: 600 }}>
                          {issue.owner}
                        </div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>
                          {issue.action}
                        </div>
                      </div>
                    </td>

                    {/* Expand icon */}
                    <td style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                      {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                    </td>
                  </tr>

                  {/* Expanded Customer Quotes Drawer */}
                  {isExpanded && (
                    <tr style={{ backgroundColor: 'var(--bg-surface-1)' }}>
                      <td colSpan={8} style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-strong)' }}>
                        <div style={{ marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                          <Quote size={14} style={{ color: 'var(--lambo-gold)' }} />
                          <span style={{
                            fontFamily: 'var(--font-display)',
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            color: 'var(--lambo-gold)',
                            letterSpacing: '0.1em',
                          }}>
                            VERBATIM CUSTOMER EVIDENCE (SAMPLE QUOTES):
                          </span>
                        </div>

                        {issue.quotes && issue.quotes.length > 0 ? (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                            {issue.quotes.map((quote, qIdx) => (
                              <div
                                key={qIdx}
                                style={{
                                  padding: '8px 12px',
                                  backgroundColor: 'var(--bg-surface-2)',
                                  borderLeft: '2px solid var(--danger-red)',
                                  fontSize: '0.82rem',
                                  color: 'var(--text-smoke)',
                                  fontStyle: 'italic',
                                }}
                              >
                                &ldquo;{quote}&rdquo;
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            No individual verbatim quotes isolated for this cluster.
                          </div>
                        )}
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
