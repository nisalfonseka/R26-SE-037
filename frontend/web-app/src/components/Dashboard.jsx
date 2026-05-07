import { SpellCheck, Newspaper, PenLine, FileText } from 'lucide-react';

const TOOLS = [
  { id: 'grammar',   label: 'Grammar Checker',    desc: 'Check and correct Sinhala grammar',          icon: SpellCheck, color: 'text-red-500', bg: 'bg-red-50', hover: 'hover:border-red-500 hover:shadow-red-500/10' },
  { id: 'headlines', label: 'Headline Generator', desc: 'Generate headline options from articles',    icon: Newspaper, color: 'text-orange-500', bg: 'bg-orange-50', hover: 'hover:border-orange-500 hover:shadow-orange-500/10'  },
  { id: 'rewriter',  label: 'Style Rewriter',     desc: 'Rewrite text in different tones',            icon: PenLine, color: 'text-purple-500', bg: 'bg-purple-50', hover: 'hover:border-purple-500 hover:shadow-purple-500/10'    },
  { id: 'summarizer',label: 'News Summarizer',    desc: 'Summarize long-form articles',               icon: FileText, color: 'text-cyan-500', bg: 'bg-cyan-50', hover: 'hover:border-cyan-500 hover:shadow-cyan-500/10'   },
];

export default function Dashboard({ onSelectTool }) {
  return (
    <div className="w-full flex flex-col items-center pt-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome to SinAi</h1>
      <p className="text-gray-500 mb-10 text-center">Select a tool to get started</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full max-w-2xl">
        {TOOLS.map(({ id, label, desc, icon: Icon, color, bg, hover }) => (
          <button
            key={id}
            id={`dashboard-${id}`}
            onClick={() => onSelectTool(id)}
            className={`text-left p-6 rounded-2xl border-2 border-transparent bg-white shadow-md
              ${hover} hover:-translate-y-1
              transition-all duration-300 cursor-pointer group`}
          >
            <div className="flex items-start gap-4 flex-col items-center text-center">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center shrink-0 mb-2 ${bg} group-hover:scale-110 transition-transform duration-300`}>
                <Icon size={28} className={`${color}`} />
              </div>
              <div>
                <h2 className="text-lg font-bold text-gray-800">{label}</h2>
                <p className="text-sm text-gray-500 mt-1">{desc}</p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
