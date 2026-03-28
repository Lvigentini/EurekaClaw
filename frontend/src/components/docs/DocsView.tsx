import { useState, useEffect } from 'react';
import { apiGet } from '@/api/client';

interface DocEntry {
  slug: string;
  title: string;
  file: string;
}

interface DocContent {
  slug: string;
  title: string;
  content: string;
}

/**
 * Minimal markdown → HTML renderer for bundled user docs.
 * SECURITY: Content comes from trusted, bundled .md files shipped with the
 * package — not from user input or external sources.
 */
function renderMarkdown(md: string): string {
  let html = md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/^---$/gm, '<hr/>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/^\|(.+)\|$/gm, (match: string) => {
      const cells = match.split('|').filter((c: string) => c.trim()).map((c: string) => c.trim());
      if (cells.every((c: string) => /^[-:]+$/.test(c))) return '';
      return '<tr>' + cells.map((c: string) => `<td>${c}</td>`).join('') + '</tr>';
    })
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>');

  html = '<p>' + html + '</p>';
  html = html.replace(/<p>\s*<\/p>/g, '').replace(/<p>\s*<br\/>\s*<\/p>/g, '');
  html = html.replace(/(<tr>[\s\S]*?<\/tr>(?:\s*<tr>[\s\S]*?<\/tr>)*)/g, '<table>$1</table>');
  return html;
}

export function DocsView() {
  const [index, setIndex] = useState<DocEntry[]>([]);
  const [activeSlug, setActiveSlug] = useState('');
  const [doc, setDoc] = useState<DocContent | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiGet<{ docs: DocEntry[] }>('/api/docs')
      .then((data) => {
        setIndex(data.docs ?? []);
        if (data.docs?.length && !activeSlug) {
          setActiveSlug(data.docs[0].slug);
        }
      })
      .catch(() => setIndex([]));
  }, []);

  useEffect(() => {
    if (!activeSlug) return;
    setLoading(true);
    apiGet<DocContent>(`/api/docs/${activeSlug}`)
      .then(setDoc)
      .catch(() => setDoc(null))
      .finally(() => setLoading(false));
  }, [activeSlug]);

  // Content is from bundled .md files — trusted, not user-supplied
  return (
    <div className="docs-view">
      <nav className="docs-sidebar">
        <h2 className="docs-sidebar-title">User Guide</h2>
        {index.map((entry) => (
          <button
            key={entry.slug}
            className={`docs-nav-item${activeSlug === entry.slug ? ' is-active' : ''}`}
            onClick={() => setActiveSlug(entry.slug)}
          >
            {entry.title}
          </button>
        ))}
      </nav>
      <main className="docs-content">
        {loading && <p className="docs-loading">Loading...</p>}
        {!loading && doc && (
          <article
            className="docs-article"
            // Safe: content is from bundled markdown files, not user input
            dangerouslySetInnerHTML={{ __html: renderMarkdown(doc.content) }}
          />
        )}
        {!loading && !doc && activeSlug && (
          <p className="docs-empty">Document not found.</p>
        )}
      </main>
    </div>
  );
}
