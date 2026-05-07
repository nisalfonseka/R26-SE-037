import { useState } from 'react';
import {
  Copy, Check, ChevronDown, ChevronUp, Trophy, AlertTriangle,
  CheckCircle2, XCircle, Sparkles, Tag, Eye, BarChart3
} from 'lucide-react';

/* ── Metric bar ─────────────────────────────────────────────────── */
function MetricBar({ label, value, threshold, suffix = '' }) {
  const pct = Math.min(value * 100, 100);
  const passed = value >= threshold;
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-[12px]">
        <span className="text-gray-500">{label}</span>
        <span className={passed ? 'text-emerald-600 font-semibold' : 'text-amber-600 font-semibold'}>
          {(value * 100).toFixed(1)}%{suffix}
        </span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            passed ? 'bg-emerald-400' : 'bg-amber-400'
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

/* ── Badge ──────────────────────────────────────────────────────── */
function Badge({ passed, label }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold
      ${passed ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : 'bg-red-50 text-red-500 border border-red-100'}`}>
      {passed ? <CheckCircle2 size={11} /> : <XCircle size={11} />}
      {label}
    </span>
  );
}

/* ── Single candidate card ──────────────────────────────────────── */
function CandidateCard({ candidate, index, isExpanded, onToggle, onCopy }) {
  const [copied, setCopied] = useState(false);
  const m = candidate.metrics;
  const isBest = candidate.rank === 1;

  const handleCopy = async (e) => {
    e.stopPropagation();
    await navigator.clipboard.writeText(candidate.headline);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className={`rounded-xl border transition-all duration-200 ${
      isBest
        ? 'border-emerald-200 bg-gradient-to-br from-emerald-50/50 to-white shadow-sm'
        : 'border-gray-200 bg-white hover:border-gray-300'
    }`}>
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-start gap-3 px-4 py-3.5 text-left cursor-pointer"
      >
        {/* Rank badge */}
        <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5 text-[12px] font-bold ${
          isBest ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-400'
        }`}>
          {isBest ? <Trophy size={14} /> : candidate.rank}
        </div>

        <div className="flex-1 min-w-0">
          <p className={`text-[15px] leading-relaxed ${isBest ? 'font-semibold text-gray-900' : 'text-gray-800'}`}>
            {candidate.headline}
          </p>
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            <Badge passed={candidate.passed_validation} label={candidate.passed_validation ? 'Passed' : 'Failed'} />
            <Badge passed={m.grammar_pass} label="Grammar" />
            <Badge passed={m.length_ok} label="Length" />
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0 mt-0.5">
          <button
            onClick={handleCopy}
            className="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors cursor-pointer"
            title="Copy headline"
          >
            {copied ? <Check size={14} className="text-emerald-500" /> : <Copy size={14} />}
          </button>
          {isExpanded ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
        </div>
      </button>

      {/* Expanded metrics */}
      {isExpanded && (
        <div className="px-4 pb-4 pt-0 border-t border-gray-100 mt-0">
          <div className="pt-3 space-y-3">
            <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
              <BarChart3 size={12} /> Quality Metrics
            </p>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2.5">
              <MetricBar label="ROUGE-1" value={m.rouge_1} threshold={0.15} />
              <MetricBar label="ROUGE-2" value={m.rouge_2} threshold={0.1} />
              <MetricBar label="ROUGE-L" value={m.rouge_l} threshold={0.1} />
              <MetricBar label="BLEU" value={m.bleu} threshold={0.01} />
              <MetricBar label="Semantic Sim." value={m.semantic_similarity} threshold={0.2} />
              <MetricBar label="Entity Cov." value={m.entity_coverage} threshold={0.3} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Entity tag ─────────────────────────────────────────────────── */
const ENTITY_COLORS = {
  PERSON: 'bg-blue-50 text-blue-600 border-blue-100',
  ORG:    'bg-purple-50 text-purple-600 border-purple-100',
  LOC:    'bg-green-50 text-green-600 border-green-100',
  DATE:   'bg-amber-50 text-amber-600 border-amber-100',
  NUMBER: 'bg-rose-50 text-rose-600 border-rose-100',
  EVENT:  'bg-indigo-50 text-indigo-600 border-indigo-100',
};

function EntityTag({ entity }) {
  const colors = ENTITY_COLORS[entity.label] || 'bg-gray-50 text-gray-600 border-gray-200';
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[12px] font-medium border ${colors}`}>
      <Tag size={10} />
      <span>{entity.text}</span>
      <span className="opacity-60 text-[10px]">{entity.label}</span>
    </span>
  );
}

/* ── Main export ────────────────────────────────────────────────── */
export default function HeadlineOutputPanel({ output, loading, error }) {
  const [expandedIdx, setExpandedIdx] = useState(null);
  const [showEntities, setShowEntities] = useState(false);
  const [showPipeline, setShowPipeline] = useState(false);

  if (loading) {
    return (
      <div id="headline-loading" className="mt-6 py-12 flex flex-col items-center justify-center gap-3">
        <div className="flex gap-1">
          {[0,1,2].map(i => (
            <div
              key={i}
              className="w-2 h-2 bg-accent rounded-full animate-bounce"
              style={{ animationDelay: `${i * 150}ms` }}
            />
          ))}
        </div>
        <span className="text-base text-gray-400">Generating headlines…</span>
        <p className="text-xs text-gray-300 max-w-xs text-center">
          Running preprocessing, entity extraction, generation, optimization, and validation pipeline
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div id="headline-error" className="mt-6 px-4 py-3.5 text-[15px] text-red-600 bg-red-50 rounded-xl border border-red-100 flex items-start gap-2.5">
        <AlertTriangle size={18} className="shrink-0 mt-0.5" />
        <div>
          <p className="font-medium">Generation failed</p>
          <p className="text-sm mt-0.5 text-red-500">{error}</p>
        </div>
      </div>
    );
  }

  if (!output) return null;

  const candidates = output.candidates || [];
  const entities = output.source_entities || [];
  const semantics = output.semantic_extraction || {};
  const pipelineLog = output.pipeline_log || [];

  return (
    <div id="headline-output" className="mt-6 space-y-5">
      {/* Section header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
            Generated Headlines
          </span>
          {output.regeneration_count > 0 && (
            <span className="text-[11px] px-2 py-0.5 bg-amber-50 text-amber-600 border border-amber-100 rounded-full font-medium">
              {output.regeneration_count} regen{output.regeneration_count > 1 ? 's' : ''}
            </span>
          )}
        </div>
        <span className="text-xs text-gray-300">
          {candidates.length} candidate{candidates.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Best headline highlight */}
      {output.best_headline && (
        <div className="px-5 py-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl border border-emerald-100">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-emerald-500" />
            <span className="text-[11px] font-semibold text-emerald-600 uppercase tracking-wider">Best Headline</span>
          </div>
          <p className="text-[17px] font-semibold text-gray-900 leading-relaxed">
            {output.best_headline}
          </p>
        </div>
      )}

      {/* Candidates list */}
      <div className="space-y-2.5">
        {candidates.map((c, i) => (
          <CandidateCard
            key={i}
            candidate={c}
            index={i}
            isExpanded={expandedIdx === i}
            onToggle={() => setExpandedIdx(expandedIdx === i ? null : i)}
          />
        ))}
      </div>

      {/* Entities section (collapsible) */}
      {entities.length > 0 && (
        <div className="rounded-xl border border-gray-200 overflow-hidden">
          <button
            onClick={() => setShowEntities(v => !v)}
            className="w-full flex items-center justify-between px-4 py-3 text-left cursor-pointer hover:bg-gray-50 transition-colors"
          >
            <span className="text-[12px] font-semibold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
              <Tag size={12} /> Source Entities ({entities.length})
            </span>
            {showEntities ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
          </button>
          {showEntities && (
            <div className="px-4 pb-4 flex flex-wrap gap-2">
              {entities.map((e, i) => <EntityTag key={i} entity={e} />)}
            </div>
          )}
        </div>
      )}

      {/* Semantic themes */}
      {semantics.key_themes && semantics.key_themes.length > 0 && (
        <div className="px-4 py-3 bg-gray-50 rounded-xl border border-gray-100">
          <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-2 flex items-center gap-1.5">
            <Eye size={12} /> Key Themes
          </p>
          <div className="flex flex-wrap gap-1.5">
            {semantics.key_themes.map((t, i) => (
              <span key={i} className="px-2.5 py-1 bg-white rounded-lg border border-gray-200 text-[12px] font-medium text-gray-600">
                {t}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Visual prompt */}
      {semantics.visual_prompt && (
        <div className="px-4 py-3 bg-indigo-50/50 rounded-xl border border-indigo-100">
          <p className="text-[11px] font-semibold text-indigo-400 uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
            <Sparkles size={12} /> Visual Prompt
          </p>
          <p className="text-[13px] text-indigo-700 leading-relaxed">{semantics.visual_prompt}</p>
        </div>
      )}

      {/* Pipeline log (collapsible) */}
      {pipelineLog.length > 0 && (
        <div className="rounded-xl border border-gray-200 overflow-hidden">
          <button
            onClick={() => setShowPipeline(v => !v)}
            className="w-full flex items-center justify-between px-4 py-3 text-left cursor-pointer hover:bg-gray-50 transition-colors"
          >
            <span className="text-[12px] font-semibold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
              <BarChart3 size={12} /> Pipeline Log
            </span>
            {showPipeline ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
          </button>
          {showPipeline && (
            <div className="px-4 pb-4">
              <div className="space-y-1">
                {pipelineLog.map((log, i) => (
                  <div key={i} className="flex items-center gap-3 py-1.5 text-[12px]">
                    <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                      log.status === 'success' ? 'bg-emerald-400' : log.status === 'warning' ? 'bg-amber-400' : 'bg-red-400'
                    }`} />
                    <span className="text-gray-500 font-mono w-32 shrink-0">{log.stage}</span>
                    <span className="text-gray-400 flex-1 truncate">{log.message}</span>
                    <span className="text-gray-300 shrink-0 font-mono">{log.duration_ms.toFixed(1)}ms</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
