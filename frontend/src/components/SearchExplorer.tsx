import React, { useState, useEffect } from 'react';
import { Search, Star, Loader2, ArrowLeft, ArrowRight } from 'lucide-react';
import { searchReviews, getReviews } from '../api/client';
import type { ReviewItem } from '../types/analysis';

interface SearchExplorerProps {
  analysisId: string;
  brands: string[];
  products: string[];
}

export const SearchExplorer: React.FC<SearchExplorerProps> = ({
  analysisId,
  brands,
  products,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('ALL');
  const [selectedProduct, setSelectedProduct] = useState('ALL');
  const [selectedSentiment, setSelectedSentiment] = useState('ALL');
  const [page, setPage] = useState(1);
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [isSearchMode, setIsSearchMode] = useState(false);

  // Fetch paginated reviews or search reviews
  const fetchReviews = async () => {
    setLoading(true);
    try {
      if (searchQuery.trim().length > 0) {
        setIsSearchMode(true);
        const results = await searchReviews(analysisId, searchQuery, 25);
        setReviews(results);
        setTotalCount(results.length);
        setTotalPages(1);
      } else {
        setIsSearchMode(false);
        const data = await getReviews(
          analysisId,
          page,
          20,
          selectedBrand,
          selectedSentiment,
          selectedProduct
        );
        setReviews(data.items);
        setTotalCount(data.total);
        setTotalPages(data.pages);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  },[analysisId, page, selectedBrand, selectedProduct, selectedSentiment])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchReviews();
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setIsSearchMode(false);
    setPage(1);
  };

  return (
    <div className="telemetry-card" style={{ padding: 24, marginBottom: 32 }}>
      {/* Title */}
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ fontSize: '1.25rem', letterSpacing: '0.1em' }}>
          <span style={{ color: 'var(--cyan-pulse)' }}>EVIDENCE EXPLORER & TF-IDF RETRIEVAL</span>
        </h2>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
          Search verbatim customer records with full-text retrieval or filter by brand and sentiment.
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 12,
        marginBottom: 24,
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', flex: '1 1 320px', gap: 8 }}>
          <div style={{
            position: 'relative',
            width: '100%',
          }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search complaints, topics, e.g. 'battery drains' or 'pairing drops'..."
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-surface-2)',
                border: '1px solid var(--border-strong)',
                color: '#FFFFFF',
                padding: '10px 14px 10px 38px',
                fontSize: '0.85rem',
                outline: 'none',
              }}
            />
            <Search size={16} style={{ position: 'absolute', left: 12, top: 13, color: 'var(--text-muted)' }} />
          </div>
          <button type="submit" className="btn-gold" style={{ padding: '10px 18px' }} disabled={loading}>
            Search
          </button>
          {searchQuery && (
            <button type="button" onClick={handleClearSearch} className="btn-ghost" style={{ padding: '10px 14px' }}>
              Clear
            </button>
          )}
        </form>

        {/* Brand & Sentiment Filters */}
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <select
            value={selectedBrand}
            onChange={(e) => { setSelectedBrand(e.target.value); setPage(1); }}
            style={{
              backgroundColor: 'var(--bg-surface-2)',
              border: '1px solid var(--border-strong)',
              color: '#FFFFFF',
              padding: '10px 14px',
              fontSize: '0.82rem',
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            <option value="ALL">All Brands</option>
            {brands.map((b, idx) => (
              <option key={idx} value={b}>{b}</option>
            ))}
          </select>

          <select
          value={selectedProduct}
          onChange={(e) => {
            setSelectedProduct(e.target.value);
            setPage(1);
          }}
          style={{
            backgroundColor: 'var(--bg-surface-2)',
            border: '1px solid var(--border-strong)',
            color: '#FFFFFF',
            padding: '10px 14px',
            fontSize: '0.82rem',
            outline: 'none',
            cursor: 'pointer',
            maxWidth: 220,
          }}
        >
          <option value="ALL">All Products</option>
          {products.map((product) => (
            <option key={product} value={product}>
              {product}
            </option>
          ))}
        </select>
        <select
        value={selectedSentiment}
        onChange={(e) => {
          setSelectedSentiment(e.target.value);
          setPage(1);
        }}
        style={{
          backgroundColor: 'var(--bg-surface-2)',
          border: '1px solid var(--border-strong)',
          color: '#FFFFFF',
          padding: '10px 14px',
          fontSize: '0.82rem',
          outline: 'none',
          cursor: 'pointer',
        }}
      >
        <option value="ALL">All Sentiments</option>
        <option value="negative">Negative Reviews</option>
        <option value="positive">Positive Reviews</option>
        <option value="neutral">Neutral Reviews</option>
      </select>
        </div>
      </div>

      {/* Meta Counter */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '0.78rem',
        color: 'var(--text-muted)',
        marginBottom: 16,
      }}>
        <div>
          {isSearchMode ? (
            <span>TF-IDF Search returned {reviews.length} relevant customer matches</span>
          ) : (
            <span>Showing {reviews.length} of {totalCount} matching reviews</span>
          )}
        </div>
        {!isSearchMode && totalPages > 1 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page <= 1 || loading}
              className="btn-subtle"
              style={{ padding: '4px 8px' }}
            >
              <ArrowLeft size={14} />
            </button>
            <span style={{ color: 'var(--text-smoke)' }}>
              Page {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page >= totalPages || loading}
              className="btn-subtle"
              style={{ padding: '4px 8px' }}
            >
              <ArrowRight size={14} />
            </button>
          </div>
        )}
      </div>

      {/* Reviews List */}
      {loading ? (
        <div style={{ padding: 40, textAlign: 'center' }}>
          <Loader2 size={24} className="animate-spin" style={{ color: 'var(--lambo-gold)', margin: '0 auto 12px' }} />
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Querying review database...</div>
        </div>
      ) : reviews.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {reviews.map((rev, idx) => (
            <div
              key={idx}
              style={{
                padding: '16px 20px',
                backgroundColor: 'var(--bg-surface-1)',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                flexDirection: 'column',
                gap: 10,
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: 8,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span className="telemetry-badge badge-gold" style={{ fontSize: '0.72rem' }}>
                    {rev.brand || 'Unbranded'}
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    {[1, 2, 3, 4, 5].map((s) => (
                      <Star
                        key={s}
                        size={13}
                        fill={s <= rev.rating ? 'var(--lambo-gold)' : 'transparent'}
                        color={s <= rev.rating ? 'var(--lambo-gold)' : 'var(--border-strong)'}
                      />
                    ))}
                  </div>
                  {rev.review_id && (
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      #{rev.review_id}
                    </span>
                  )}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  {rev.match !== undefined && rev.match !== null && (
                    <span className="telemetry-badge badge-cyan" style={{ fontSize: '0.7rem' }}>
                      Relevance: {(rev.match * 100).toFixed(0)}%
                    </span>
                  )}
                  {rev.date && (
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      {rev.date.toString().slice(0, 10)}
                    </span>
                  )}
                </div>
              </div>

              <div style={{ fontSize: '0.88rem', color: 'var(--text-smoke)', lineHeight: 1.6 }}>
                &ldquo;{rev.review_text}&rdquo;
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)' }}>
          No customer reviews matched the query criteria.
        </div>
      )}
    </div>
  );
};
