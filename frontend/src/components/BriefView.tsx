import React, { useState, useEffect } from 'react';
import { Copy, Check, Download, Loader2, AlertCircle } from 'lucide-react';
import { getBrief } from '../api/client';

interface BriefViewProps {
  analysisId: string;
}

export const BriefView: React.FC<BriefViewProps> = ({ analysisId }) => {
  const [briefText, setBriefText] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let mounted = true;
    const fetchBrief = async () => {
      try {
        setLoading(true);
        setError(null);
        const text = await getBrief(analysisId);
        if (mounted) setBriefText(text);
      } catch (err: any) {
        if (mounted) setError(err.message || 'Failed to generate PM brief.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchBrief();
    return () => { mounted = false; };
  }, [analysisId]);

  const handleCopy = () => {
    navigator.clipboard.writeText(briefText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([briefText], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ReviewLens-Brief-${analysisId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="telemetry-card" style={{ padding: 60, textAlign: 'center' }}>
        <Loader2 size={32} className="animate-spin" style={{ color: 'var(--lambo-gold)', margin: '0 auto 16px' }} />
        <div style={{ fontFamily: 'var(--font-display)', color: 'var(--text-smoke)', letterSpacing: '0.1em' }}>
          GENERATING EXECUTIVE PRODUCT MANAGER BRIEFING...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="telemetry-card" style={{ padding: 32, textAlign: 'center', color: 'var(--danger-red)' }}>
        <AlertCircle size={24} style={{ margin: '0 auto 12px' }} />
        <div>{error}</div>
      </div>
    );
  }

  return (
    <div className="telemetry-card" style={{ padding: 32, marginBottom: 32 }}>
      {/* Header & Actions */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 24,
        paddingBottom: 20,
        borderBottom: '1px solid var(--border-subtle)',
        flexWrap: 'wrap',
        gap: 12,
      }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', letterSpacing: '0.1em' }}>
            <span style={{ color: 'var(--lambo-gold)' }}>PRODUCT MANAGER BRIEFING</span>
          </h2>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Synthesized executive document with priority fix list and verbatim evidence.
          </div>
        </div>

        <div style={{ display: 'flex', gap: 10 }}>
          <button onClick={handleCopy} className="btn-ghost" style={{ padding: '8px 16px' }}>
            {copied ? (
              <>
                <Check size={14} style={{ color: 'var(--success-green)' }} />
                Copied to Clipboard
              </>
            ) : (
              <>
                <Copy size={14} />
                Copy Markdown
              </>
            )}
          </button>
          <button onClick={handleDownload} className="btn-gold" style={{ padding: '8px 16px' }}>
            <Download size={14} />
            Export .md
          </button>
        </div>
      </div>

      {/* Brief Content Viewer */}
      <div style={{
        backgroundColor: 'var(--bg-surface-1)',
        border: '1px solid var(--border-subtle)',
        padding: 28,
        fontFamily: 'var(--font-mono)',
        fontSize: '0.85rem',
        lineHeight: 1.7,
        color: 'var(--text-smoke)',
        whiteSpace: 'pre-wrap',
        overflowX: 'auto',
      }}>
        {briefText}
      </div>
    </div>
  );
};
