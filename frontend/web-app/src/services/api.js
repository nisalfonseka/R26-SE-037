const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

async function request(endpoint, body) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || `Request failed (${res.status})`);
  }

  return res.json();
}

export function checkGrammar(text) {
  return request('/grammar/check', { text });
}

export function generateHeadlines(text, count = 5) {
  return request('/headlines/generate', { text, count });
}

export function rewriteStyle(text, tone) {
  return request('/rewrite', { text, tone });
}

export function summarizeNews(text, length) {
  return request('/summarize', { text, length });
}
