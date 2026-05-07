import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

/**
 * Generic output panel for grammar, style rewriter, and summarizer tools.
 *
 * Handles the following response shapes from the backend:
 *   - Grammar:    { corrected, corrections, correction_count }
 *   - Style:      { rewritten, original, tone }
 *   - Summarizer: { summary, length }
 */
export default function OutputPanel({ output, loading, error, type }) {
  const [copied, setCopied] = useState(false);

  if (loading) {
    return (
      <div id="output-loading" className="mt-6">
        {/* Shimmer skeleton — mirrors the real output panel */}
        <div className="flex items-center justify-between mb-2.5">
          <span className="text-xs font-semibold text-gray-300 uppercase tracking-widest">Output</span>
        </div>
        <div className="px-5 py-4 bg-gray-50 rounded-xl border border-gray-100 space-y-3">
          {/* 4 full lines */}
          {[100, 92, 97, 88].map((w, i) => (
            <div
              key={i}
              className="h-4 rounded-md bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 animate-shimmer"
              style={{ width: `${w}%`, backgroundSize: '200% 100%' }}
            />
          ))}
          {/* half line */}
          <div
            className="h-4 rounded-md bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 animate-shimmer"
            style={{ width: '45%', backgroundSize: '200% 100%' }}
          />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div id="output-error" className="mt-6 px-4 py-3.5 text-[15px] text-red-600 bg-red-50 rounded-xl border border-red-100">
        {error}
      </div>
    );
  }

  if (!output) return null;

  // Resolve the primary display text from whichever response shape we received
  const displayText =
    output.corrected   ??  // grammar
    output.rewritten   ??  // style rewriter
    output.summary     ??  // summarizer
    (typeof output === 'string' ? output : JSON.stringify(output, null, 2));

  const handleCopy = async () => {
    await navigator.clipboard.writeText(displayText);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  // Grammar-specific: show correction count badge
  const correctionCount =
    output.correction_count != null ? output.correction_count : null;

  return (
    <div id="output-panel" className="mt-6">
      {/* Header row */}
      <div className="flex items-center justify-between mb-2.5">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
            Output
          </span>
          {correctionCount != null && (
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              correctionCount > 0
                ? 'bg-amber-50 text-amber-600 border border-amber-200'
                : 'bg-green-50 text-green-600 border border-green-200'
            }`}>
              {correctionCount > 0
                ? `${correctionCount} correction${correctionCount !== 1 ? 's' : ''}`
                : '✓ No errors found'}
            </span>
          )}
        </div>
        <button
          id="copy-output"
          onClick={handleCopy}
          className="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-colors cursor-pointer"
          title="Copy to clipboard"
        >
          {copied ? <Check size={17} className="text-green-500" /> : <Copy size={17} />}
        </button>
      </div>

      {/* Main output text */}
      <div className="px-5 py-4 bg-gray-50 rounded-xl border border-gray-100 text-[15px] text-gray-800 leading-[1.8]">
        <p className="whitespace-pre-wrap">{displayText}</p>
      </div>

      {/* Grammar: show individual correction details */}
      {output.corrections && output.corrections.length > 0 && (
        <div className="mt-3 space-y-2">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
            Corrections applied
          </p>
          {output.corrections.map((c, i) => (
            <div
              key={i}
              className="flex gap-3 px-4 py-3 bg-amber-50 border border-amber-100 rounded-lg text-sm"
            >
              <span className="text-amber-400 font-bold shrink-0">#{i + 1}</span>
              <div className="min-w-0">
                <p className="text-gray-700">
                  <span className="line-through text-red-500">{c.original}</span>
                  {' → '}
                  <span className="text-green-600 font-medium">{c.corrected}</span>
                </p>
                <p className="text-gray-400 text-xs mt-0.5">{c.rule}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
