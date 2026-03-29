import { useState, useEffect, useCallback } from 'react';
import { apiGet, apiPost } from '@/api/client';
import type { SessionRun } from '@/types';

interface ReviewerPersona {
  name: string;
  type: string;
  icon: string;
  description: string;
}

interface ReviewComment {
  severity: string;
  section: string;
  comment: string;
  suggestion: string;
  resolved: boolean;
  user_response: string;
}

interface ReviewResultData {
  persona_name: string;
  persona_icon: string;
  summary: string;
  strengths: string[];
  comments: ReviewComment[];
  scores: Record<string, number>;
  recommendation: string;
  questions: string[];
  missing_references: string[];
  major_count: number;
  minor_count: number;
  suggestion_count: number;
  resolved_count: number;
}

interface ReviewPanelProps {
  run: SessionRun | null;
  isVisible?: boolean;
}

export function ReviewPanel({ run, isVisible = true }: ReviewPanelProps) {
  const [personas, setPersonas] = useState<ReviewerPersona[]>([]);
  const [selectedPersona, setSelectedPersona] = useState('rigorous');
  const [customInstructions, setCustomInstructions] = useState('');
  const [reviews, setReviews] = useState<ReviewResultData[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeReviewIdx, setActiveReviewIdx] = useState(0);

  useEffect(() => {
    if (!isVisible) return;
    apiGet<{ reviewers: ReviewerPersona[] }>('/api/reviewers')
      .then((data) => setPersonas(data.reviewers ?? []))
      .catch(() => {});
  }, [isVisible]);

  const runReview = useCallback(async () => {
    if (!run?.run_id) return;
    setLoading(true);
    try {
      const prevComments = reviews.length > 0 ? reviews[reviews.length - 1].comments : undefined;
      const data = await apiPost<{ review: ReviewResultData }>(`/api/runs/${run.run_id}/review`, {
        persona: selectedPersona,
        custom_instructions: customInstructions,
        previous_comments: prevComments,
      });
      if (data.review) {
        setReviews((prev) => [...prev, data.review]);
        setActiveReviewIdx(reviews.length); // point to newly added
      }
    } catch (err) {
      console.error('Review failed:', err);
    } finally {
      setLoading(false);
    }
  }, [run?.run_id, selectedPersona, customInstructions, reviews]);

  if (!run) {
    return <div className="review-panel"><p className="drawer-muted">Select a session to run a review.</p></div>;
  }

  const activeReview = reviews[activeReviewIdx] ?? null;

  return (
    <div className="review-panel">
      {/* Persona selector */}
      <div className="review-persona-section">
        <span className="review-section-label">Choose your reviewer</span>
        <div className="review-persona-grid">
          {personas.map((p) => (
            <button
              key={p.name}
              className={`review-persona-card${selectedPersona === p.name.toLowerCase() ? ' is-active' : ''}`}
              onClick={() => setSelectedPersona(p.name.toLowerCase())}
            >
              <span className="review-persona-icon">{p.icon}</span>
              <span className="review-persona-name">{p.name}</span>
              <span className="review-persona-desc">{p.description.slice(0, 60)}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Custom instructions */}
      <div className="review-instructions">
        <input
          type="text"
          className="review-instructions-input"
          placeholder="Custom instructions (optional): e.g. 'Focus on statistical methods'"
          value={customInstructions}
          onChange={(e) => setCustomInstructions(e.target.value)}
          disabled={loading}
        />
        <button className="btn btn-primary" onClick={() => void runReview()} disabled={loading}>
          {loading ? 'Reviewing...' : reviews.length > 0 ? 'Re-review' : 'Run Review'}
        </button>
      </div>

      {/* Review round tabs (if multiple reviews) */}
      {reviews.length > 1 && (
        <div className="review-rounds">
          {reviews.map((r, i) => (
            <button
              key={i}
              className={`review-round-tab${i === activeReviewIdx ? ' is-active' : ''}`}
              onClick={() => setActiveReviewIdx(i)}
            >
              {r.persona_icon} Round {i + 1}
            </button>
          ))}
        </div>
      )}

      {/* Review results */}
      {activeReview && (
        <div className="review-results">
          {/* Summary */}
          {activeReview.summary && (
            <div className="review-summary">
              <span className="review-persona-badge">{activeReview.persona_icon} {activeReview.persona_name}</span>
              <p>{activeReview.summary}</p>
            </div>
          )}

          {/* Strengths */}
          {activeReview.strengths.length > 0 && (
            <div className="review-strengths">
              <span className="review-section-label">Strengths</span>
              {activeReview.strengths.map((s: string, i: number) => (
                <div key={i} className="review-strength-item">+ {s}</div>
              ))}
            </div>
          )}

          {/* Comments by severity */}
          {(['major', 'minor', 'suggestion'] as const).map((sev) => {
            const items = activeReview.comments.filter((c: ReviewComment) => c.severity === sev);
            if (items.length === 0) return null;
            const labels: Record<string, string> = { major: 'MAJOR', minor: 'MINOR', suggestion: 'SUGGESTION' };
            const icons: Record<string, string> = { major: '🔴', minor: '🟡', suggestion: '💡' };
            return (
              <div key={sev} className={`review-issue-group review-issue--${sev}`}>
                <span className="review-section-label">{icons[sev]} {labels[sev]} ({items.length})</span>
                {items.map((c: ReviewComment, i: number) => (
                  <div key={i} className="review-comment">
                    <div className="review-comment-header">
                      {c.section && <span className="review-comment-section">[{c.section}]</span>}
                      <span className="review-comment-text">{c.comment}</span>
                    </div>
                    {c.suggestion && (
                      <div className="review-comment-suggestion">→ {c.suggestion}</div>
                    )}
                  </div>
                ))}
              </div>
            );
          })}

          {/* Scores */}
          {Object.keys(activeReview.scores).length > 0 && (
            <div className="review-scores">
              <span className="review-section-label">Scores</span>
              <div className="review-scores-grid">
                {Object.entries(activeReview.scores).map(([dim, score]) => (
                  <div key={dim} className="review-score-item">
                    <span className="review-score-label">{dim}</span>
                    <span className="review-score-value">{score as number}/10</span>
                    <div className="review-score-bar">
                      <div className="review-score-fill" style={{ width: `${((score as number) / 10) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendation */}
          {activeReview.recommendation && (
            <div className="review-recommendation">
              <strong>Recommendation:</strong> {activeReview.recommendation}
            </div>
          )}

          {/* Stats */}
          <div className="review-stats">
            {activeReview.major_count} major, {activeReview.minor_count} minor, {activeReview.suggestion_count} suggestions
          </div>
        </div>
      )}
    </div>
  );
}
