import { useState, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import ToolHeader from './components/ToolHeader';
import InputBox from './components/InputBox';
import OutputPanel from './components/OutputPanel';
import HeadlineOutputPanel from './components/HeadlineOutputPanel';
import RightPanel from './components/RightPanel';
import Dashboard from './components/Dashboard';
import HistoryPage from './components/HistoryPage';
import SettingsPage from './components/SettingsPage';
import ProfilePage from './components/ProfilePage';
import { useToolProcessor } from './hooks/useToolProcessor';
import { checkGrammar, generateHeadlines, rewriteStyle, summarizeNews } from './services/api';
import { saveToHistory } from './components/HistoryPage';

const TOOL_CONFIG = {
  grammar: {
    title: 'Grammar Checker',
    description: 'Check and correct Sinhala grammar',
    placeholder: 'මෙහි ඔබගේ සිංහල වාක්‍යය ඇතුළත් කරන්න…',
    actionLabel: 'Correct',
    outputType: 'text',
  },
  headlines: {
    title: 'Headline Generator',
    description: 'Generate headline options from an article',
    placeholder: 'මෙහි ප්‍රවෘත්ති ලිපිය ඇතුළත් කරන්න…',
    actionLabel: 'Generate',
    outputType: 'headlines',
  },
  rewriter: {
    title: 'Style Rewriter',
    description: 'Rewrite text in a different tone',
    placeholder: 'නැවත ලිවීමට අවශ්‍ය පෙළ ඇතුළත් කරන්න…',
    actionLabel: 'Rewrite',
    outputType: 'text',
  },
  summarizer: {
    title: 'News Summarizer',
    description: 'Summarize long-form articles',
    placeholder: 'සාරාංශ කිරීමට ලිපිය ඇතුළත් කරන්න…',
    actionLabel: 'Summarize',
    outputType: 'text',
  },
};

const TOOL_IDS = ['grammar', 'headlines', 'rewriter', 'summarizer'];

function App() {
  const [activeTool, setActiveTool] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [settings, setSettings] = useState({
    tone: 'formal',
    length: 'short',
    count: 3,
    headlineStyle: 'formal',
    headlineMaxLength: 80,
  });

  const { input, setInput, output, loading, error, process, clear } = useToolProcessor();

  const handleSelectTool = useCallback((toolId) => {
    setActiveTool(toolId);
    if (TOOL_IDS.includes(toolId)) {
      clear();
    }
  }, [clear]);

  const handleRun = useCallback(() => {
    if (!input.trim()) return;
    const wrappedProcess = async (apiCall) => {
      await process(async (text) => {
        const result = await apiCall(text);
        saveToHistory(activeTool, text, result);
        return result;
      });
    };

    switch (activeTool) {
      case 'grammar':
        wrappedProcess((text) => checkGrammar(text));
        break;
      case 'headlines':
        wrappedProcess((text) =>
          generateHeadlines(text, {
            style: settings.headlineStyle,
            maxLength: settings.headlineMaxLength,
            numCandidates: settings.count,
          })
        );
        break;
      case 'rewriter':
        wrappedProcess((text) => rewriteStyle(text, settings.tone));
        break;
      case 'summarizer':
        wrappedProcess((text) => summarizeNews(text, settings.length));
        break;
    }
  }, [activeTool, input, settings, process]);

  const config = TOOL_CONFIG[activeTool];
  const isTool = TOOL_IDS.includes(activeTool);

  const renderContent = () => {
    switch (activeTool) {
      case 'dashboard':
        return <Dashboard onSelectTool={handleSelectTool} />;
      case 'history':
        return <HistoryPage onSelectTool={handleSelectTool} />;
      case 'settings':
        return <SettingsPage />;
      case 'profile':
        return <ProfilePage />;
      default:
        if (!config) return null;
        return (
          <>
            <ToolHeader title={config.title} description={config.description} />

            <InputBox
              value={input}
              onChange={setInput}
              placeholder={config.placeholder}
              onSubmit={handleRun}
              disabled={loading}
              activeTool={activeTool}
            />

            <div className="flex items-center gap-3 mt-4 justify-end w-full">
              <button
                id="btn-run"
                onClick={handleRun}
                disabled={loading || !input.trim()}
                className={`px-8 py-2 text-white text-[15px] font-semibold rounded-full shadow-sm
                  ${getButtonColor(activeTool)} active:scale-[0.98]
                  disabled:opacity-40 disabled:cursor-not-allowed
                  transition-all duration-100 cursor-pointer`}
              >
                {config.actionLabel}
              </button>
              <button
                id="btn-clear"
                onClick={clear}
                disabled={loading}
                className={`px-6 py-2 text-[15px] font-semibold text-white rounded-full shadow-sm
                  ${getButtonColor(activeTool)} active:scale-[0.98]
                  disabled:opacity-40 disabled:cursor-not-allowed
                  transition-all duration-100 cursor-pointer`}
              >
                Clear
              </button>
            </div>

            {/* Use dedicated panel for headlines, generic for others */}
            {activeTool === 'headlines' ? (
              <HeadlineOutputPanel
                output={output}
                loading={loading}
                error={error}
              />
            ) : (
              <OutputPanel
                output={output}
                loading={loading}
                error={error}
                type={config.outputType}
              />
            )}
          </>
        );
    }
  };

  const getBgColor = () => {
    switch (activeTool) {
      case 'dashboard': return 'bg-[#0ea5e9]'; // blue
      case 'grammar': return 'bg-[#ef4444]'; // red
      case 'headlines': return 'bg-[#f97316]'; // orange
      case 'rewriter': return 'bg-[#8b5cf6]'; // purple
      case 'summarizer': return 'bg-[#06b6d4]'; // cyan
      case 'history': return 'bg-[#f43f5e]'; // rose
      case 'settings': return 'bg-[#10b981]'; // green
      case 'profile': return 'bg-[#64748b]'; // slate
      default: return 'bg-[#0ea5e9]';
    }
  };

  const getButtonColor = (tool) => {
    switch (tool) {
      case 'dashboard': return 'bg-[#0ea5e9] hover:bg-[#0284c7]';
      case 'grammar': return 'bg-[#ef4444] hover:bg-[#dc2626]';
      case 'headlines': return 'bg-[#f97316] hover:bg-[#ea580c]';
      case 'rewriter': return 'bg-[#8b5cf6] hover:bg-[#7c3aed]';
      case 'summarizer': return 'bg-[#06b6d4] hover:bg-[#0891b2]';
      case 'history': return 'bg-[#f43f5e] hover:bg-[#e11d48]';
      case 'settings': return 'bg-[#10b981] hover:bg-[#059669]';
      case 'profile': return 'bg-[#64748b] hover:bg-[#475569]';
      default: return 'bg-[#0ea5e9] hover:bg-[#0284c7]';
    }
  };

  return (
    <div className={`h-full flex ${getBgColor()} pattern-bg transition-colors duration-500`}>
      <Sidebar
        activeTool={activeTool}
        onSelectTool={handleSelectTool}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen((v) => !v)}
        collapsed={sidebarCollapsed}
        onCollapse={() => setSidebarCollapsed((v) => !v)}
      />

      <main className="flex-1 flex flex-col bg-[#f8fafc] rounded-tl-[2rem] sm:rounded-tl-[3rem] my-2 mr-2 sm:my-4 sm:mr-4 shadow-2xl relative overflow-hidden">
        <div className="flex-1 flex min-w-0 overflow-y-auto">
          <div className="flex-1 min-w-0 flex justify-center">
            <div className="w-full max-w-4xl px-4 py-6 sm:px-8 sm:py-8">
              {renderContent()}
            </div>
          </div>

          {isTool && (
            <RightPanel
              activeTool={activeTool}
              settings={settings}
              onSettingsChange={setSettings}
              output={output}
              loading={loading}
              input={input}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
