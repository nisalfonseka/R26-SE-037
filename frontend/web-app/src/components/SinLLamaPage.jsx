import { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Bot, User, Loader2, Cpu, Wifi, WifiOff, ChevronDown, ChevronUp, Sliders } from 'lucide-react';

const SINLLAMA_API = 'https://carving-nebulizer-dandy.ngrok-free.dev/generate';

const EXAMPLE_PROMPTS = [
  'ශ්‍රී ලංකාවේ ප්‍රධාන නගර මොනවාද?',
  'සිංහල භාෂාවේ ඉතිහාසය කෙරෙහි කෙටියෙන් විස්තර කරන්න.',
  'ලංකාවේ ආර්ථිකය ගැන ලියන්න.',
  'Write a short Sinhala poem about the ocean.',
];

export default function SinLLamaPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [task, setTask] = useState('grammar'); // grammar | headline | summarizer | style
  const [showSettings, setShowSettings] = useState(false);
  const [online, setOnline] = useState(null); // null = unknown, true/false
  const [elapsed, setElapsed] = useState(null);

  const bottomRef = useRef(null);
  const textareaRef = useRef(null);
  const timerRef = useRef(null);

  // Ping the server once to check reachability
  useEffect(() => {
    const controller = new AbortController();
    fetch(SINLLAMA_API.replace('/generate', '/docs'), {
      method: 'GET',
      signal: controller.signal,
      headers: { 'ngrok-skip-browser-warning': 'true' },
    })
      .then(() => setOnline(true))
      .catch(() => setOnline(false));
    return () => controller.abort();
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async () => {
    const prompt = input.trim();
    if (!prompt || loading) return;

    setInput('');
    setError(null);
    setElapsed(null);

    const userMsg = { role: 'user', text: prompt };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    const start = Date.now();
    timerRef.current = setInterval(() => {
      setElapsed(((Date.now() - start) / 1000).toFixed(1));
    }, 100);

    try {
      const res = await fetch(SINLLAMA_API, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
        body: JSON.stringify({ prompt, task }),
      });

      clearInterval(timerRef.current);
      setElapsed(((Date.now() - start) / 1000).toFixed(1));

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Server error ${res.status}: ${errText}`);
      }

      const data = await res.json();
      const botMsg = {
        role: 'bot',
        text: data.response ?? JSON.stringify(data),
        meta: data.task ? {
          task:        data.task,
          inputTok:    data.input_tokens,
          cap:         data.max_cap_used,
          outputTok:   data.output_tokens,
        } : null,
      };
      setMessages((prev) => [...prev, botMsg]);
      setOnline(true);
    } catch (err) {
      clearInterval(timerRef.current);
      setError(err.message || 'Failed to reach SinLLaMA server.');
      setOnline(false);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    setMessages([]);
    setError(null);
    setElapsed(null);
  };

  const autoResize = (el) => {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 160) + 'px';
  };

  return (
    <div className="sinllama-page">
      {/* ── Header ── */}
      <div className="sl-header">
        <div className="sl-header-left">
          <div className="sl-model-badge">
            <Cpu size={16} strokeWidth={2.5} />
            <span>SinLLaMA</span>
          </div>
          <p className="sl-subtitle">GPU-backed Sinhala language model · ngrok tunnel</p>
        </div>

        <div className="sl-header-right">
          {/* Status pill */}
          <div className={`sl-status-pill ${online === true ? 'online' : online === false ? 'offline' : 'checking'}`}>
            {online === true ? <Wifi size={13} /> : online === false ? <WifiOff size={13} /> : <Loader2 size={13} className="spin" />}
            <span>{online === true ? 'Server online' : online === false ? 'Server offline' : 'Checking…'}</span>
          </div>

          {/* Settings toggle */}
          <button
            className="sl-icon-btn"
            onClick={() => setShowSettings((v) => !v)}
            title="Generation settings"
          >
            <Sliders size={17} />
            {showSettings ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>

          {/* Clear */}
          <button className="sl-icon-btn danger" onClick={handleClear} title="Clear conversation" disabled={messages.length === 0 && !error}>
            <Trash2 size={17} />
          </button>
        </div>
      </div>

      {/* ── Settings panel ── */}
      {showSettings && (
        <div className="sl-settings-panel">
          <div className="sl-setting-row">
            <label>Task</label>
            <div className="sl-toggle-group">
              {[
                { id: 'grammar',    label: 'Grammar',    hint: 'cap ×1.5 input' },
                { id: 'headline',   label: 'Headline',   hint: 'cap 60 tokens'   },
                { id: 'summarizer', label: 'Summarizer', hint: 'cap ×0.3 input'  },
                { id: 'style',      label: 'Style',      hint: 'cap ×1.5 input'  },
              ].map(({ id, label, hint }) => (
                <button
                  key={id}
                  id={`task-${id}`}
                  className={`sl-toggle-btn ${task === id ? 'active' : ''}`}
                  onClick={() => setTask(id)}
                >
                  {label}
                  <span className="sl-toggle-hint">{hint}</span>
                </button>
              ))}
            </div>
          </div>
          <p className="sl-settings-note">
            Endpoint: <code>{SINLLAMA_API}</code>
          </p>
        </div>
      )}

      {/* ── Chat area ── */}
      <div className="sl-chat-area">
        {messages.length === 0 && !loading && !error && (
          <div className="sl-empty-state">
            <div className="sl-empty-icon">
              <Bot size={40} strokeWidth={1.5} />
            </div>
            <h3>Test SinLLaMA</h3>
            <p>Send any Sinhala or English prompt to the GPU model running via ngrok.</p>

            <div className="sl-example-prompts">
              {EXAMPLE_PROMPTS.map((p, i) => (
                <button
                  key={i}
                  className="sl-example-chip"
                  onClick={() => {
                    setInput(p);
                    textareaRef.current?.focus();
                  }}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`sl-message ${msg.role}`}>
            <div className="sl-avatar">
              {msg.role === 'user' ? <User size={15} strokeWidth={2.5} /> : <Bot size={15} strokeWidth={2.5} />}
            </div>
            <div className="sl-bubble">
              <pre className="sl-text">{msg.text}</pre>
              {msg.meta && (
                <div className="sl-meta-chips">
                  <span className="sl-chip task">{msg.meta.task}</span>
                  <span className="sl-chip">in&nbsp;{msg.meta.inputTok}t</span>
                  <span className="sl-chip">cap&nbsp;{msg.meta.cap}t</span>
                  <span className="sl-chip">out&nbsp;{msg.meta.outputTok}t</span>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="sl-message bot">
            <div className="sl-avatar"><Bot size={15} strokeWidth={2.5} /></div>
            <div className="sl-bubble loading-bubble">
              <span className="sl-dot" />
              <span className="sl-dot" />
              <span className="sl-dot" />
              {elapsed && <span className="sl-elapsed">{elapsed}s</span>}
            </div>
          </div>
        )}

        {error && (
          <div className="sl-error-bar">
            <WifiOff size={15} />
            <span>{error}</span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ── Input bar ── */}
      <div className="sl-input-bar">
        <textarea
          ref={textareaRef}
          id="sinllama-input"
          rows={1}
          className="sl-textarea"
          placeholder="Type a Sinhala or English prompt… (Enter to send)"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            autoResize(e.target);
          }}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          id="sinllama-send"
          className="sl-send-btn"
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          {loading ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
        </button>
      </div>

      <style>{`
        /* ── Page shell ── */
        .sinllama-page {
          display: flex;
          flex-direction: column;
          height: 100%;
          max-height: calc(100vh - 3rem);
          font-family: 'Inter', sans-serif;
        }

        /* ── Header ── */
        .sl-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 12px;
          margin-bottom: 18px;
        }
        .sl-header-left { display: flex; flex-direction: column; gap: 4px; }
        .sl-header-right { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

        .sl-model-badge {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          background: linear-gradient(135deg, #cd191a 0%, #8b0000 100%);
          color: #fff;
          font-size: 14px;
          font-weight: 700;
          padding: 5px 14px;
          border-radius: 999px;
          letter-spacing: 0.03em;
          box-shadow: 0 2px 10px rgba(205,25,26,0.35);
        }
        .sl-subtitle {
          font-size: 12px;
          color: #6b7280;
          margin: 0;
          padding-left: 2px;
        }

        /* Status pill */
        .sl-status-pill {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          font-size: 12px;
          font-weight: 600;
          padding: 4px 12px;
          border-radius: 999px;
          letter-spacing: 0.02em;
        }
        .sl-status-pill.online  { background: #d1fae5; color: #065f46; }
        .sl-status-pill.offline { background: #fee2e2; color: #991b1b; }
        .sl-status-pill.checking { background: #f3f4f6; color: #6b7280; }

        /* Icon buttons */
        .sl-icon-btn {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 6px 10px;
          border-radius: 10px;
          border: 1px solid #e5e7eb;
          background: #fff;
          color: #374151;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.15s, color 0.15s;
        }
        .sl-icon-btn:hover { background: #f3f4f6; }
        .sl-icon-btn.danger:hover { background: #fee2e2; color: #cd191a; border-color: #fca5a5; }
        .sl-icon-btn:disabled { opacity: 0.4; cursor: not-allowed; }

        /* ── Settings panel ── */
        .sl-settings-panel {
          background: #f8fafc;
          border: 1px solid #e5e7eb;
          border-radius: 14px;
          padding: 14px 18px;
          margin-bottom: 16px;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .sl-setting-row {
          display: flex;
          align-items: center;
          gap: 14px;
          flex-wrap: wrap;
        }
        .sl-setting-row label {
          font-size: 13px;
          font-weight: 600;
          color: #374151;
          min-width: 100px;
        }

        /* Output-type toggle */
        .sl-toggle-group {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        .sl-toggle-btn {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 2px;
          padding: 7px 18px;
          border-radius: 10px;
          border: 1.5px solid #e5e7eb;
          background: #fff;
          color: #374151;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.15s;
          line-height: 1.2;
        }
        .sl-toggle-btn:hover {
          border-color: #fca5a5;
          background: #fef2f2;
          color: #cd191a;
        }
        .sl-toggle-btn.active {
          background: linear-gradient(135deg, #cd191a, #8b0000);
          border-color: transparent;
          color: #fff;
          box-shadow: 0 2px 8px rgba(205,25,26,0.3);
        }
        .sl-toggle-hint {
          font-size: 10px;
          font-weight: 400;
          opacity: 0.75;
          letter-spacing: 0.02em;
        }
        .sl-toggle-btn.active .sl-toggle-hint { opacity: 0.85; }

        .sl-settings-note {
          font-size: 11px;
          color: #9ca3af;
          margin: 0;
        }
        .sl-settings-note code {
          background: #f1f5f9;
          padding: 1px 5px;
          border-radius: 4px;
          font-size: 10.5px;
          color: #475569;
          word-break: break-all;
        }

        /* ── Chat area ── */
        .sl-chat-area {
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 14px;
          padding: 2px 2px 8px;
          min-height: 0;
          scroll-behavior: smooth;
        }
        .sl-chat-area::-webkit-scrollbar { width: 5px; }
        .sl-chat-area::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 999px; }

        /* Empty state */
        .sl-empty-state {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 48px 24px;
          gap: 10px;
          color: #6b7280;
        }
        .sl-empty-icon {
          width: 72px;
          height: 72px;
          border-radius: 50%;
          background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          color: #cd191a;
          margin-bottom: 6px;
          box-shadow: 0 4px 20px rgba(205,25,26,0.12);
        }
        .sl-empty-state h3 {
          font-size: 18px;
          font-weight: 700;
          color: #1f2937;
          margin: 0;
        }
        .sl-empty-state p {
          font-size: 13.5px;
          max-width: 380px;
          line-height: 1.6;
          margin: 0;
        }

        /* Example prompts */
        .sl-example-prompts {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          justify-content: center;
          margin-top: 10px;
          max-width: 520px;
        }
        .sl-example-chip {
          background: #fff;
          border: 1px solid #e5e7eb;
          border-radius: 999px;
          padding: 6px 14px;
          font-size: 12.5px;
          color: #374151;
          cursor: pointer;
          transition: all 0.15s;
          text-align: left;
        }
        .sl-example-chip:hover {
          background: #fef2f2;
          border-color: #fca5a5;
          color: #cd191a;
        }

        /* Messages */
        .sl-message {
          display: flex;
          gap: 10px;
          align-items: flex-start;
          animation: fadeUp 0.18s ease;
        }
        .sl-message.user { flex-direction: row-reverse; }

        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(6px); }
          to   { opacity: 1; transform: translateY(0);   }
        }

        .sl-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
        }
        .sl-message.user .sl-avatar {
          background: linear-gradient(135deg, #cd191a, #8b0000);
          color: #fff;
          box-shadow: 0 2px 8px rgba(205,25,26,0.3);
        }
        .sl-message.bot .sl-avatar {
          background: #f1f5f9;
          color: #475569;
          border: 1px solid #e2e8f0;
        }

        .sl-bubble {
          max-width: 78%;
          padding: 11px 16px;
          border-radius: 16px;
          font-size: 14px;
          line-height: 1.65;
          word-break: break-word;
        }
        .sl-message.user .sl-bubble {
          background: linear-gradient(135deg, #cd191a, #a01010);
          color: #fff;
          border-bottom-right-radius: 4px;
          box-shadow: 0 2px 10px rgba(205,25,26,0.25);
        }
        .sl-message.bot .sl-bubble {
          background: #f8fafc;
          color: #1f2937;
          border: 1px solid #e5e7eb;
          border-bottom-left-radius: 4px;
        }
        .sl-text {
          margin: 0;
          white-space: pre-wrap;
          font-family: inherit;
          font-size: 14px;
          line-height: 1.65;
        }

        /* Loading dots */
        .loading-bubble {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 14px 18px;
          background: #f8fafc;
          border: 1px solid #e5e7eb;
          border-bottom-left-radius: 4px;
        }
        .sl-dot {
          width: 7px;
          height: 7px;
          background: #9ca3af;
          border-radius: 50%;
          animation: bounce 1.2s infinite;
        }
        .sl-dot:nth-child(2) { animation-delay: 0.2s; }
        .sl-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
          40%            { transform: translateY(-5px); opacity: 1; }
        }
        .sl-elapsed {
          font-size: 11px;
          color: #9ca3af;
          margin-left: 8px;
          font-weight: 500;
        }

        /* Error bar */
        .sl-error-bar {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          background: #fff5f5;
          border: 1px solid #fca5a5;
          border-radius: 12px;
          padding: 11px 16px;
          color: #cd191a;
          font-size: 13px;
          font-weight: 500;
        }

        /* ── Input bar ── */
        .sl-input-bar {
          display: flex;
          align-items: flex-end;
          gap: 10px;
          padding: 10px 0 4px;
          border-top: 1px solid #e5e7eb;
          margin-top: 6px;
        }
        .sl-textarea {
          flex: 1;
          resize: none;
          border: 1.5px solid #e5e7eb;
          border-radius: 14px;
          padding: 10px 14px;
          font-size: 14px;
          font-family: inherit;
          line-height: 1.5;
          color: #1f2937;
          background: #fff;
          outline: none;
          transition: border-color 0.15s, box-shadow 0.15s;
          min-height: 44px;
          max-height: 160px;
          overflow-y: auto;
        }
        .sl-textarea:focus {
          border-color: #cd191a;
          box-shadow: 0 0 0 3px rgba(205,25,26,0.1);
        }
        .sl-textarea:disabled { background: #f9fafb; opacity: 0.7; }

        .sl-send-btn {
          width: 44px;
          height: 44px;
          border-radius: 12px;
          background: linear-gradient(135deg, #cd191a, #8b0000);
          color: #fff;
          border: none;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: opacity 0.15s, transform 0.1s, box-shadow 0.15s;
          box-shadow: 0 2px 10px rgba(205,25,26,0.3);
          flex-shrink: 0;
        }
        .sl-send-btn:hover:not(:disabled) {
          opacity: 0.9;
          transform: translateY(-1px);
          box-shadow: 0 4px 14px rgba(205,25,26,0.4);
        }
        .sl-send-btn:active:not(:disabled) { transform: scale(0.96); }
        .sl-send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

        /* Debug meta chips on bot bubbles */
        .sl-meta-chips {
          display: flex;
          flex-wrap: wrap;
          gap: 5px;
          margin-top: 8px;
        }
        .sl-chip {
          font-size: 10.5px;
          font-weight: 600;
          padding: 2px 8px;
          border-radius: 999px;
          background: #e2e8f0;
          color: #475569;
          letter-spacing: 0.02em;
        }
        .sl-chip.task {
          background: #fef2f2;
          color: #cd191a;
          text-transform: uppercase;
          letter-spacing: 0.06em;
        }

        /* Spinner utility */
        .spin { animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
