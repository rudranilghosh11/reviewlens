import React, { useState, useRef } from 'react';
import { Upload, FileSpreadsheet, AlertTriangle, ArrowRight, Loader2, Sparkles } from 'lucide-react';
import { uploadAndAnalyse } from '../api/client';
import type { AnalysisResult } from '../types/analysis';

interface UploadHeroProps {
  onAnalysisComplete: (result: AnalysisResult) => void;
  loading: boolean;
  setLoading: (l: boolean) => void;
  error: string | null;
  setError: (e: string | null) => void;
}

export const UploadHero: React.FC<UploadHeroProps> = ({
  onAnalysisComplete,
  loading,
  setLoading,
  error,
  setError,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [pipelineStage, setPipelineStage] = useState<string>('Initializing pipeline...');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    setError(null);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };
  const handleUpload = async (file: File) => {
    // Size validation removed: unlimited file size allowed
    // Proceed directly to analysis


    setLoading(true);
    setError(null);

    // Dynamic telemetry progress steps
    const stages = [
      'Ingesting tabular data and validating headers...',
      'Cleaning noisy reviews and detecting duplicate spam...',
      'Aspect extraction & VADER sentiment scoring...',
      'K-Means clustering negative clauses into concrete issues...',
      'Calculating priority scores and rating drag telemetry...',
      'Detecting emerging spikes and building search indices...',
    ];
    let stageIdx = 0;
    const interval = setInterval(() => {
      stageIdx = (stageIdx + 1) % stages.length;
      setPipelineStage(stages[stageIdx]);
    }, 900);

    try {
      const result = await uploadAndAnalyse(file);
      clearInterval(interval);
      onAnalysisComplete(result);
    } catch (err: any) {
      clearInterval(interval);
      setError(err.message || 'An error occurred during dataset analysis.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = async () => {
    try {
      setLoading(true);
      setError(null);
      setPipelineStage('Loading bundled sample dataset (3,200 multi-brand reviews)...');
      const response = await fetch('/reviews.csv');
      if (!response.ok) {
        throw new Error('Sample file reviews.csv could not be loaded from public directory.');
      }
      const blob = await response.blob();
      const sampleFile = new File([blob], 'sample_reviews.csv', { type: 'text/csv' });
      setSelectedFile(sampleFile);
      await handleRunAnalysis(sampleFile);
    } catch (err: any) {
      setError(err.message || 'Failed to load sample dataset.');
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: '48px auto', padding: '0 24px' }}>
      {/* Hero Title */}
      <div style={{ textAlign: 'center', marginBottom: 40 }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          padding: '4px 12px',
          backgroundColor: 'var(--bg-surface-2)',
          border: '1px solid var(--border-subtle)',
          marginBottom: 16,
        }}>
          <span style={{ color: 'var(--lambo-gold)', fontSize: '0.75rem', fontWeight: 700 }}>SPECIFICATION:</span>
          <span style={{ color: 'var(--text-smoke)', fontSize: '0.75rem', letterSpacing: '0.08em' }}>AUTOMATED REVIEW TELEMETRY & FIX-FIRST RANKING</span>
        </div>

        <h1 style={{
          fontSize: 'clamp(2rem, 4vw, 3.2rem)',
          lineHeight: 1.1,
          letterSpacing: '0.08em',
          marginBottom: 16,
        }}>
          CUSTOMER VOICE <span style={{ color: 'var(--lambo-gold)' }}>TELEMETRY</span>
        </h1>
        <p style={{
          maxWidth: 680,
          margin: '0 auto',
          color: 'var(--text-muted)',
          fontSize: '1rem',
          lineHeight: 1.6,
        }}>
          High-precision aspect sentiment extraction, negative clause clustering, transparent issue-priority scoring, and automated executive PM briefings.
        </p>
      </div>

      {/* Main Upload Box */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className="telemetry-card highlight-gold"
        style={{
          padding: 40,
          backgroundColor: 'var(--bg-surface-card)',
          border: dragOver ? '1px solid var(--lambo-gold)' : '1px solid var(--border-subtle)',
          boxShadow: dragOver ? '0 0 30px rgba(255,192,0,0.1)' : 'none',
          transition: 'all 0.2s ease',
        }}
      >
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          gap: 20,
        }}>
          <div style={{
            width: 64,
            height: 64,
            backgroundColor: 'var(--bg-surface-2)',
            border: '1px solid var(--border-strong)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: selectedFile ? 'var(--lambo-gold)' : 'var(--text-smoke)',
          }}>
            {selectedFile ? <FileSpreadsheet size={32} /> : <Upload size={32} />}
          </div>

          <div>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.15rem',
              fontWeight: 700,
              letterSpacing: '0.08em',
              marginBottom: 6,
            }}>
              {selectedFile ? selectedFile.name : 'DRAG & DROP REVIEW DATASET HERE'}
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              {selectedFile
                ? `${(selectedFile.size / 1024).toFixed(1)} KB — Ready to process`
                : 'Supports CSV, TSV, Excel (.xlsx), JSON, NDJSON, and Parquet'}
            </div>
          </div>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".csv,.tsv,.txt,.xlsx,.xls,.json,.jsonl,.ndjson,.parquet,.gz"
            style={{ display: 'none' }}
          />

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, justifyContent: 'center' }}>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn-ghost"
              disabled={loading}
            >
              Browse Local File
            </button>

            <button
              onClick={handleLoadSample}
              className="btn-subtle"
              disabled={loading}
              title="Loads bundled sample dataset with 3,200 earbud reviews across 3 brands"
            >
              <Sparkles size={14} style={{ color: 'var(--lambo-gold)' }} />
              Load Sample Dataset (3.2k Reviews)
            </button>

            {selectedFile && (
              <button
                onClick={() => handleRunAnalysis()}
                className="btn-gold"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    Launch Analysis Pipeline
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Loading Progress State */}
        {loading && (
          <div style={{
            marginTop: 32,
            padding: 20,
            backgroundColor: 'var(--bg-surface-1)',
            border: '1px solid var(--border-gold)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
              <Loader2 size={18} style={{ color: 'var(--lambo-gold)', animation: 'spin 1s linear infinite' }} />
              <div style={{
                fontFamily: 'var(--font-display)',
                fontSize: '0.85rem',
                fontWeight: 700,
                color: 'var(--lambo-gold)',
                letterSpacing: '0.08em',
              }}>
                PIPELINE EXECUTION TELEMETRY
              </div>
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-smoke)', fontFamily: 'var(--font-mono)' }}>
              &gt; {pipelineStage}
            </div>
          </div>
        )}

        {/* Error Feedback */}
        {error && (
          <div style={{
            marginTop: 24,
            padding: 16,
            backgroundColor: 'rgba(255, 51, 75, 0.1)',
            border: '1px solid var(--danger-red)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: 12,
          }}>
            <AlertTriangle size={20} style={{ color: 'var(--danger-red)', flexShrink: 0, marginTop: 2 }} />
            <div>
              <div style={{
                fontFamily: 'var(--font-display)',
                fontSize: '0.85rem',
                fontWeight: 700,
                color: 'var(--danger-red)',
                letterSpacing: '0.08em',
                marginBottom: 4,
              }}>
                ANALYSIS VALIDATION FAILED
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-smoke)' }}>
                {error}
              </div>
              {error.toLowerCase().includes('review') && (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 8 }}>
                  Note: The dataset must have a column containing the customer review text (e.g. named <code>review_text</code>, <code>review</code>, <code>comment</code>, <code>feedback</code>, or <code>text</code>).
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Feature Pillars Preview */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: 16,
        marginTop: 32,
      }}>
        <div className="telemetry-card" style={{ padding: 20 }}>
          <div style={{ color: 'var(--lambo-gold)', fontSize: '0.75rem', fontWeight: 700, marginBottom: 6 }}>
            01 // FIX-FIRST RANKING
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-smoke)', lineHeight: 1.5 }}>
            Clusters negative sentences by aspect and ranks them by review share, rating drag, and spike velocity.
          </div>
        </div>

        <div className="telemetry-card" style={{ padding: 20 }}>
          <div style={{ color: 'var(--cyan-pulse)', fontSize: '0.75rem', fontWeight: 700, marginBottom: 6 }}>
            02 // ASPECT SENTIMENT
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-smoke)', lineHeight: 1.5 }}>
            Domain-lexicon and VADER sentiment mapped to Battery, Sound, Comfort, Connectivity, Price, and more.
          </div>
        </div>

        <div className="telemetry-card" style={{ padding: 20 }}>
          <div style={{ color: 'var(--lambo-gold)', fontSize: '0.75rem', fontWeight: 700, marginBottom: 6 }}>
            03 // COMPETITOR HEATMAP
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-smoke)', lineHeight: 1.5 }}>
            Cross-brand aspect net sentiment benchmark reveals specific strengths and weakness matrices.
          </div>
        </div>

        <div className="telemetry-card" style={{ padding: 20 }}>
          <div style={{ color: 'var(--cyan-pulse)', fontSize: '0.75rem', fontWeight: 700, marginBottom: 6 }}>
            04 // AUTOMATED BRIEFING
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-smoke)', lineHeight: 1.5 }}>
            Generates executive product-manager briefings with concrete action items and owner assignments.
          </div>
        </div>
      </div>
    </div>
  );
};
