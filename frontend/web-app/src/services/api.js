/**
 * Frontend API service — all backend calls go through this module.
 * Base URL defaults to the local FastAPI server on port 8000.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://sinai.onrender.com/api/v1' || 'http://localhost:8000/api/v1';

async function request(endpoint, body = null, method = 'POST') {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };

  if (body !== null && method !== 'GET') {
    options.body = JSON.stringify(body);
  }

  const res = await fetch(`${API_BASE}${endpoint}`, options);

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || err.message || `Request failed (${res.status})`);
  }

  return res.json();
}

// ── Grammar ──
export function checkGrammar(text) {
  return request('/grammar/check', { text });
}

export function getGrammarHistory(page = 1, pageSize = 20) {
  return request(`/grammar/history?page=${page}&page_size=${pageSize}`, null, 'GET');
}

// ── Headlines ──
export function generateHeadlines(text, options = {}) {
  const {
    count = 5,
    style = 'formal',
    maxLength = 80,
    numCandidates,
  } = typeof options === 'object' && !Array.isArray(options) ? options : { count: options };

  return request('/headline/generate', {
    article_text: text,
    num_candidates: numCandidates ?? count,
    style,
    max_length: maxLength,
  });
}

export function getHeadlineHistory(page = 1, pageSize = 20) {
  return request(`/headline/history?page=${page}&page_size=${pageSize}`, null, 'GET');
}

export function generateImage(prompt, headline = '') {
  return request('/headline/generate-image', { prompt, headline });
}

// ── Style Rewriter ──
export function rewriteStyle(text, tone = 'formal') {
  return request('/style/rewrite', { text, tone });
}

export function getStyleHistory(page = 1, pageSize = 20) {
  return request(`/style/history?page=${page}&page_size=${pageSize}`, null, 'GET');
}

// ── Summarizer ──
export function summarizeNews(text, length = 'medium') {
  return request('/summarize/check', { text, length });
}

export function getSummarizeHistory(page = 1, pageSize = 20) {
  return request(`/summarize/history?page=${page}&page_size=${pageSize}`, null, 'GET');
}
