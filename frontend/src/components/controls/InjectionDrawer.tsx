import { useState } from 'react';
import { apiPost } from '@/api/client';
import type { SessionRun } from '@/types';

interface InjectionDrawerProps {
  run: SessionRun;
}

type InjectType = 'idea' | 'paper' | 'draft';

const TYPE_CONFIG: Record<InjectType, { label: string; icon: string; placeholder: string; rows: number }> = {
  idea: {
    label: 'Idea',
    icon: '💡',
    placeholder: 'What if we used spectral methods instead?',
    rows: 3,
  },
  paper: {
    label: 'Paper',
    icon: '📄',
    placeholder: 'arXiv ID (e.g. 2401.12345) or paper title',
    rows: 1,
  },
  draft: {
    label: 'Draft',
    icon: '📝',
    placeholder: 'Paste draft content or key sections to consider…',
    rows: 6,
  },
};

export function InjectionDrawer({ run }: InjectionDrawerProps) {
  const [open, setOpen] = useState(false);
  const [type, setType] = useState<InjectType>('idea');
  const [text, setText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState('');

  const cfg = TYPE_CONFIG[type];

  const handleInject = async () => {
    if (!text.trim()) return;
    setSubmitting(true);
    setResult('');
    try {
      const data = await apiPost<{ ok: boolean; pool_version: number; session_version: number }>(
        `/api/runs/${run.run_id}/ideation-pool/inject`,
        { type, text: text.trim(), source: 'ui' },
      );
      setResult(`Injected! Version: v${String(data.session_version).padStart(3, '0')}`);
      setText('');
      setTimeout(() => setResult(''), 4000);
    } catch (err) {
      setResult(`Failed: ${(err as Error).message}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (run.status !== 'paused') return null;

  if (!open) {
    return (
      <button className="injection-toggle-btn" onClick={() => setOpen(true)}>
        <span>⊕</span> Inject paper / idea / draft
      </button>
    );
  }

  return (
    <div className="injection-drawer">
      <div className="injection-drawer-header">
        <span className="injection-drawer-title">Inject into Session</span>
        <button className="injection-close" onClick={() => setOpen(false)}>×</button>
      </div>

      <div className="injection-type-row">
        {(Object.keys(TYPE_CONFIG) as InjectType[]).map((t) => (
          <button
            key={t}
            className={`injection-type-btn${type === t ? ' is-active' : ''}`}
            onClick={() => setType(t)}
          >
            <span>{TYPE_CONFIG[t].icon}</span>
            <span>{TYPE_CONFIG[t].label}</span>
          </button>
        ))}
      </div>

      <textarea
        className="injection-textarea"
        placeholder={cfg.placeholder}
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={cfg.rows}
        disabled={submitting}
      />

      <div className="injection-actions">
        <button
          className="btn btn-primary"
          disabled={submitting || !text.trim()}
          onClick={() => void handleInject()}
        >
          {submitting ? 'Injecting…' : `Inject ${cfg.label}`}
        </button>
      </div>

      {result && <p className="injection-result">{result}</p>}
    </div>
  );
}
