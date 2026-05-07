export default function InputBox({ value, onChange, placeholder, onSubmit, disabled, activeTool }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      onSubmit?.();
    }
  };

  const getBorderColor = () => {
    switch (activeTool) {
      case 'dashboard': return 'border-[#cd191a]';
      case 'grammar': return 'border-[#cd191a]';
      case 'headlines': return 'border-[#cd191a]';
      case 'rewriter': return 'border-[#cd191a]';
      case 'summarizer': return 'border-[#cd191a]';
      default: return 'border-[#cd191a]';
    }
  };

  return (
    <div className="w-full">
      <div className="relative">
        <textarea
          id="input-box"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={9}
          className={`w-full px-4 py-3.5 text-[15px] text-gray-900 placeholder-gray-400
            border-2 ${getBorderColor()} rounded-xl leading-relaxed
            focus:outline-none focus:ring-0
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors duration-100 resize-y min-h-[200px] shadow-sm`}
        />
        <div className="absolute top-3 right-3 text-gray-400">
           {/* small icon placeholder */}
           <svg className="w-5 h-5 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
        </div>
      </div>
    </div>
  );
}
