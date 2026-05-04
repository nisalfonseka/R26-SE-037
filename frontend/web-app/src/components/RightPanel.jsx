import {
  AlertCircle, CheckCircle2, Lightbulb, BookOpen,
  Newspaper, BarChart3, Tag, Sparkles
} from 'lucide-react';

// ─── Settings Panels ─────────────────────────────────────────────────────────

const TONES = [
  { id: 'formal',    label: 'Formal'    },
  { id: 'editorial', label: 'Editorial' },
  { id: 'youth',     label: 'Youth'     },
];

const LENGTHS = [
  { id: 'short',  label: 'Short'  },
  { id: 'medium', label: 'Medium' },
];

const HEADLINE_STYLES = [
  { id: 'formal',        label: 'Formal',        desc: 'Authoritative, broadsheet tone' },
  { id: 'breaking_news', label: 'Breaking News', desc: 'Urgent, attention-grabbing' },
  { id: 'youth',         label: 'Youth',         desc: 'Casual, social media friendly' },
  { id: 'editorial',     label: 'Editorial',     desc: 'Analytical, thought-provoking' },
];

const HEADLINE_COUNTS = [
  { id: 3, label: '3 Headlines' },
  { id: 5, label: '5 Headlines' },
  { id: 7, label: '7 Headlines' },
];

const MAX_LENGTHS = [
  { id: 60,  label: 'Short (60 chars)' },
  { id: 80,  label: 'Medium (80 chars)' },
  { id: 120, label: 'Long (120 chars)' },
];

function OptionGroup({ label, options, value, onChange }) {
  return (
    <div className="mb-6">
      <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">
        {label}
      </label>
      <div className="space-y-1">
        {options.map((opt) => (
          <button
            key={opt.id}
            onClick={() => onChange(opt.id)}
            className={`
              w-full text-left px-3.5 py-2.5 rounded-lg text-[14px] font-medium
              transition-colors duration-100 cursor-pointer
              ${value === opt.id
                ? 'bg-red-50 text-accent'
                : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
              }
            `}
          >
            <span>{opt.label}</span>
            {opt.desc && (
              <span className={`block text-[11px] mt-0.5 ${
                value === opt.id ? 'text-red-400' : 'text-gray-400'
              }`}>
                {opt.desc}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── Grammar Suggestions Panel ────────────────────────────────────────────────

const SUGGESTION_TYPES = {
  spelling:    { label: 'Spelling',    color: 'text-red-500',    bg: 'bg-red-50',    border: 'border-red-100'    },
  grammar:     { label: 'Grammar',     color: 'text-orange-500', bg: 'bg-orange-50', border: 'border-orange-100' },
  punctuation: { label: 'Punctuation', color: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-100' },
  style:       { label: 'Style',       color: 'text-blue-500',   bg: 'bg-blue-50',   border: 'border-blue-100'   },
  info:        { label: 'Info',        color: 'text-gray-500',   bg: 'bg-gray-50',   border: 'border-gray-200'   },
};

function deriveSuggestions(input, output) {
  if (!output?.corrected || !input) return [];

  // Use API-provided suggestions if present
  if (Array.isArray(output.suggestions) && output.suggestions.length > 0) {
    return output.suggestions;
  }

  // Auto-derive by word-level diff
  const inputWords  = input.trim().split(/\s+/);
  const outputWords = output.corrected.trim().split(/\s+/);
  const derived = [];

  const maxLen = Math.max(inputWords.length, outputWords.length);
  for (let i = 0; i < maxLen; i++) {
    const orig = inputWords[i];
    const corr = outputWords[i];
    if (orig !== corr && orig && corr) {
      derived.push({
        type: 'grammar',
        original: orig,
        correction: corr,
        message: `"${orig}" → "${corr}"`,
      });
    }
  }

  if (derived.length === 0 && output.corrected !== input.trim()) {
    derived.push({
      type: 'style',
      message: 'Minor stylistic improvements applied',
    });
  }

  return derived;
}

function GrammarSuggestionsPanel({ output, loading, input }) {
  const suggestions = deriveSuggestions(input, output);
  const isCorrect   = output?.corrected && output.corrected === input?.trim();

  return (
    <>
      <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">
        Suggestions
      </h2>

      {/* Loading */}
      {loading && (
        <div className="flex flex-col gap-2.5">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-16 bg-gray-100 rounded-2xl animate-subtle-pulse" />
          ))}
        </div>
      )}

      {/* No output yet */}
      {!loading && !output && (
        <div className="flex flex-col items-center justify-center py-10 text-center">
          <BookOpen size={30} className="text-gray-200 mb-3" />
          <p className="text-sm text-gray-400 leading-relaxed">
            Run the checker to see grammar suggestions here.
          </p>
        </div>
      )}

      {/* All correct */}
      {!loading && isCorrect && (
        <div className="flex flex-col items-center gap-2 py-8 text-center">
          <CheckCircle2 size={30} className="text-green-400" />
          <p className="text-sm font-medium text-gray-700">No issues found</p>
          <p className="text-xs text-gray-400">Your text looks correct.</p>
        </div>
      )}

      {/* Suggestions list */}
      {!loading && !isCorrect && suggestions.length > 0 && (
        <div className="space-y-2.5">
          <p className="text-xs text-gray-400 mb-3">
            {suggestions.length} issue{suggestions.length !== 1 ? 's' : ''} detected
          </p>
          {suggestions.map((s, i) => {
            const typeStyle = SUGGESTION_TYPES[s.type] || SUGGESTION_TYPES.info;
            return (
              <div
                key={i}
                className={`rounded-2xl border px-4 py-3.5 ${typeStyle.bg} ${typeStyle.border}`}
              >
                <div className="flex items-start gap-2.5">
                  <AlertCircle
                    size={15}
                    className={`${typeStyle.color} shrink-0 mt-0.5`}
                  />
                  <div className="min-w-0">
                    <span className={`text-[11px] font-semibold uppercase tracking-wider ${typeStyle.color}`}>
                      {typeStyle.label}
                    </span>
                    {s.original && s.correction ? (
                      <div className="mt-1 space-y-0.5">
                        <p className="text-[13px] text-gray-500 line-through">{s.original}</p>
                        <p className="text-[13px] font-medium text-gray-800">{s.correction}</p>
                      </div>
                    ) : (
                      <p className="text-[13px] text-gray-700 mt-0.5">{s.message}</p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Tip */}
      {!loading && output && (
        <div className="mt-5 flex items-start gap-2 px-3 py-3 bg-gray-50 rounded-2xl border border-gray-100">
          <Lightbulb size={14} className="text-gray-300 shrink-0 mt-0.5" />
          <p className="text-[12px] text-gray-400 leading-relaxed">
            Review each suggestion before applying. Context matters in journalism.
          </p>
        </div>
      )}
    </>
  );
}

// ─── Headline Insights Panel ──────────────────────────────────────────────────

function HeadlineInsightsPanel({ output, loading }) {
  if (loading) {
    return (
      <>
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">
          Pipeline Insights
        </h2>
        <div className="flex flex-col gap-2.5">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-14 bg-gray-100 rounded-2xl animate-subtle-pulse" />
          ))}
        </div>
      </>
    );
  }

  if (!output) {
    return (
      <>
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">
          Pipeline Insights
        </h2>
        <div className="flex flex-col items-center justify-center py-10 text-center">
          <Newspaper size={30} className="text-gray-200 mb-3" />
          <p className="text-sm text-gray-400 leading-relaxed">
            Generate headlines to see pipeline insights here.
          </p>
        </div>
      </>
    );
  }

  const candidates = output.candidates || [];
  const passed = candidates.filter(c => c.passed_validation).length;
  const entities = output.source_entities || [];
  const semantics = output.semantic_extraction || {};
  const pipelineLog = output.pipeline_log || [];
  const totalTime = pipelineLog.reduce((sum, l) => sum + l.duration_ms, 0);

  return (
    <div className="space-y-5">
      {/* Summary stats */}
      <div>
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
          <BarChart3 size={12} /> Pipeline Summary
        </h2>
        <div className="grid grid-cols-2 gap-2">
          <div className="px-3 py-2.5 bg-gray-50 rounded-xl text-center">
            <p className="text-lg font-bold text-gray-800">{candidates.length}</p>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider">Candidates</p>
          </div>
          <div className="px-3 py-2.5 bg-emerald-50 rounded-xl text-center">
            <p className="text-lg font-bold text-emerald-600">{passed}</p>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider">Passed</p>
          </div>
          <div className="px-3 py-2.5 bg-blue-50 rounded-xl text-center">
            <p className="text-lg font-bold text-blue-600">{entities.length}</p>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider">Entities</p>
          </div>
          <div className="px-3 py-2.5 bg-amber-50 rounded-xl text-center">
            <p className="text-lg font-bold text-amber-600">{totalTime.toFixed(0)}<span className="text-xs font-normal">ms</span></p>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider">Total Time</p>
          </div>
        </div>
      </div>

      {/* Regeneration warning */}
      {output.regeneration_count > 0 && (
        <div className="flex items-start gap-2 px-3 py-2.5 bg-amber-50 rounded-xl border border-amber-100">
          <AlertCircle size={14} className="text-amber-500 shrink-0 mt-0.5" />
          <p className="text-[12px] text-amber-700">
            Pipeline triggered <strong>{output.regeneration_count}</strong> regeneration{output.regeneration_count > 1 ? 's' : ''} to meet quality thresholds.
          </p>
        </div>
      )}

      {/* Top candidate metrics */}
      {candidates.length > 0 && (
        <div>
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
            <Sparkles size={12} /> Best Headline Metrics
          </h2>
          {(() => {
            const best = candidates[0];
            const m = best.metrics;
            return (
              <div className="space-y-2">
                {[
                  ['ROUGE-1',       m.rouge_1],
                  ['ROUGE-2',       m.rouge_2],
                  ['Semantic Sim.', m.semantic_similarity],
                  ['Entity Cov.',   m.entity_coverage],
                ].map(([label, val]) => (
                  <div key={label} className="space-y-1">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-gray-500">{label}</span>
                      <span className="text-gray-600 font-semibold">{(val * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-1 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-accent/70 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(val * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            );
          })()}
        </div>
      )}

      {/* Entity distribution */}
      {entities.length > 0 && (
        <div>
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
            <Tag size={12} /> Entity Types
          </h2>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(
              entities.reduce((acc, e) => {
                acc[e.label] = (acc[e.label] || 0) + 1;
                return acc;
              }, {})
            ).map(([label, count]) => (
              <span
                key={label}
                className="px-2.5 py-1 bg-gray-50 rounded-lg border border-gray-200 text-[11px] font-medium text-gray-600"
              >
                {label} <span className="text-gray-400">×{count}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Tip */}
      <div className="flex items-start gap-2 px-3 py-3 bg-gray-50 rounded-2xl border border-gray-100">
        <Lightbulb size={14} className="text-gray-300 shrink-0 mt-0.5" />
        <p className="text-[12px] text-gray-400 leading-relaxed">
          Click on any headline candidate to expand its detailed quality metrics.
        </p>
      </div>
    </div>
  );
}

// ─── Main Export ─────────────────────────────────────────────────────────────

export default function RightPanel({ activeTool, settings, onSettingsChange, output, loading, input }) {
  if (!['grammar', 'rewriter', 'summarizer', 'headlines'].includes(activeTool)) return null;

  const getThemeColor = () => {
    switch (activeTool) {
      case 'grammar': return 'bg-red-500';
      case 'rewriter': return 'bg-purple-500';
      case 'summarizer': return 'bg-cyan-500';
      case 'headlines': return 'bg-orange-500';
      default: return 'bg-blue-500';
    }
  };

  const getTitle = () => {
    switch (activeTool) {
      case 'grammar': return 'Grammar Suggestions';
      case 'rewriter': return 'Style Settings';
      case 'summarizer': return 'Summarizer Options';
      case 'headlines': return 'Headline Insights';
      default: return 'Settings';
    }
  };

  return (
    <aside className="hidden xl:flex flex-col w-80 shrink-0 pr-8 py-8 pl-4">
      {/* Banner */}
      <div className="rounded-2xl bg-white shadow-xl overflow-hidden flex flex-col h-full border border-gray-100">
        <div className={`h-32 ${getThemeColor()} flex items-end justify-center pb-4 relative overflow-hidden shrink-0`}>
          {/* subtle background pattern in banner */}
          <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '16px 16px' }} />
          <h2 className="text-xl font-bold text-white relative z-10">{getTitle()}</h2>
        </div>

        <div className="p-5 flex-1 overflow-y-auto bg-gray-50/50">
          {activeTool === 'grammar' && (
            <GrammarSuggestionsPanel output={output} loading={loading} input={input} />
          )}

          {activeTool === 'rewriter' && (
            <OptionGroup
              label="Tone"
              options={TONES}
              value={settings.tone}
              onChange={(v) => onSettingsChange({ ...settings, tone: v })}
            />
          )}

          {activeTool === 'summarizer' && (
            <OptionGroup
              label="Length"
              options={LENGTHS}
              value={settings.length}
              onChange={(v) => onSettingsChange({ ...settings, length: v })}
            />
          )}

          {activeTool === 'headlines' && (
            <>
              {/* Settings section — shown when no output yet */}
              {!output && !loading && (
                <>
                  <OptionGroup
                    label="Style"
                    options={HEADLINE_STYLES}
                    value={settings.headlineStyle}
                    onChange={(v) => onSettingsChange({ ...settings, headlineStyle: v })}
                  />
                  <OptionGroup
                    label="Max Length"
                    options={MAX_LENGTHS}
                    value={settings.headlineMaxLength}
                    onChange={(v) => onSettingsChange({ ...settings, headlineMaxLength: v })}
                  />
                  <OptionGroup
                    label="Count"
                    options={HEADLINE_COUNTS}
                    value={settings.count}
                    onChange={(v) => onSettingsChange({ ...settings, count: v })}
                  />
                </>
              )}

              {/* Insights panel — shown when loading or output exists */}
              {(loading || output) && (
                <HeadlineInsightsPanel output={output} loading={loading} />
              )}
            </>
          )}
        </div>
      </div>
    </aside>
  );
}
