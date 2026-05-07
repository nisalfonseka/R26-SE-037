import { useState } from 'react';
import {
  LayoutDashboard, SpellCheck, Newspaper, PenLine, FileText,
  Menu, X, History, Settings, ChevronLeft, ChevronRight, User, LogOut
} from 'lucide-react';
import DotField from './DotField';

const MAIN_NAV = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, color: 'text-blue-500' },
  { id: 'grammar', label: 'Grammar Checker', icon: SpellCheck, color: 'text-red-500' },
  { id: 'headlines', label: 'Headline Generator', icon: Newspaper, color: 'text-orange-500' },
  { id: 'rewriter', label: 'Style Rewriter', icon: PenLine, color: 'text-purple-500' },
  { id: 'summarizer', label: 'News Summarizer', icon: FileText, color: 'text-cyan-500' },
];

const BOTTOM_NAV = [
  { id: 'history', label: 'History', icon: History, color: 'text-rose-500' },
  { id: 'settings', label: 'Settings', icon: Settings, color: 'text-green-500' },
];

const SIDEBAR_ACCENT = '#cd191a';

export default function Sidebar({ activeTool, onSelectTool, isOpen, onToggle, collapsed, onCollapse }) {
  const [profileOpen, setProfileOpen] = useState(false);

  const renderNavItem = ({ id, label, icon: Icon }) => {
    const isActive = activeTool === id;
    return (
      <div key={id} className={`relative flex items-center w-full ${isActive ? 'z-20' : 'z-10'}`}>
        <button
          id={`nav-${id}`}
          onClick={() => {
            onSelectTool(id);
            if (window.innerWidth < 1024) onToggle();
          }}
          title={collapsed ? label : undefined}
          className={`
            group w-full flex items-center ${collapsed ? 'justify-center' : ''} gap-4
            ${collapsed ? 'pl-0 py-3' : 'pl-6 py-3'}
            text-[15px] font-medium transition-all duration-300 cursor-pointer
            ${isActive
              ? 'bg-white text-black rounded-l-[1.5rem] translate-x-4'
              : 'text-white hover:bg-black/10 hover:text-white hover:rounded-l-[1.5rem] hover:translate-x-4 hover:mr-[-1rem]'
            }
          `}
          style={{
            marginRight: isActive ? '-1rem' : '1rem',
            paddingRight: isActive ? '1rem' : '1rem',
            marginLeft: isActive ? '1rem' : '1rem',
            borderRadius: isActive ? '2.5rem 0 0 2.5rem' : '0.75rem',
            minHeight: '34px',
          }}
        >
          {/* Icon Circle */}
          <div className={`
            w-9 h-9 rounded-full flex items-center justify-center shrink-0
            ${isActive ? 'bg-white/0' : 'bg-white/0'}
          `}>
            <Icon
              size={18}
              strokeWidth={2.5}
              className={isActive ? 'text-black' : 'text-white'}
            />
          </div>
          {!collapsed && <span className="tracking-wide">{label}</span>}
        </button>
      </div>
    );
  };

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Mobile toggle */}
      <button
        id="sidebar-toggle"
        onClick={onToggle}
        className="fixed top-4 left-4 z-50 lg:hidden p-2 rounded-lg bg-white border border-gray-200 shadow-sm cursor-pointer"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      <aside
        className={`
          fixed inset-y-0 left-0 z-40 overflow-hidden
          ${collapsed ? 'w-20' : 'w-[20rem]'} bg-[#cd191a]
          flex flex-col shrink-0
          transition-transform duration-200 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <DotField
          className="absolute inset-0 z-0 opacity-40"
          dotRadius={1.5}
          dotSpacing={19}
          bulgeStrength={14}
          glowRadius={6}
          sparkle={false}
          waveAmplitude={0}
          cursorRadius={500}
          cursorForce={0.02}
          bulgeOnly
          gradientFrom="#ffffff"
          gradientTo="#950a1f"
          glowColor="#cd191a"
        />

        {/* Logo */}
        <div className={`relative z-10 pt-8 pb-6 flex items-center gap-3 ${collapsed ? 'justify-center px-2' : 'px-10'}`}>
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-14 h-14 rounded-full flex items-center justify-center shrink-0 relative overflow-hidden transition-colors duration-500">
               <img src="/logo.png" alt="SinAi logo" className="w-full h-full object-contain p-1" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-[34px] text-white tracking-tight leading-none drop-shadow-sm">SinAi</span>
              </div>
            )}
          </div>

          <button
            id="sidebar-collapse"
            onClick={onCollapse}
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className="hidden lg:flex items-center justify-center ml-auto w-8 h-8 rounded-lg text-white hover:bg-white/20 transition-colors duration-100 cursor-pointer"
          >
            {collapsed ? <ChevronRight size={20} strokeWidth={2} /> : <ChevronLeft size={20} strokeWidth={2} />}
          </button>
        </div>

        {/* Main navigation */}
        <nav className={`relative z-10 flex-1 py-4 space-y-5`}>
          {MAIN_NAV.map(renderNavItem)}
        </nav>

        {/* Bottom section */}
        <div className={`relative z-10 py-4 space-y-2`}>
          {BOTTOM_NAV.map(renderNavItem)}
        </div>

        {/* User profile */}
        <div className={`relative z-10 px-4 pb-6 pt-2`}>
          <button
            id="user-profile-btn"
            onClick={() => setProfileOpen((v) => !v)}
            className={`
              w-full flex items-center ${collapsed ? 'justify-center' : ''} gap-3
              px-2 py-2.5 rounded-xl
              hover:bg-white/20 transition-colors duration-100 cursor-pointer
            `}
          >
            <div className="w-10 h-10 rounded-full bg-white/30 flex items-center justify-center shrink-0 border-2 border-white/40">
              <User size={18} className="text-white" />
            </div>
            {!collapsed && (
              <div className="text-left min-w-0">
                <p className="text-[15px] font-bold text-white truncate">Journalist</p>
                <p className="text-[12px] text-white/80 truncate">journalist@sinai.lk</p>
              </div>
            )}
          </button>

          {/* Profile dropdown */}
          {profileOpen && (
            <>
              <div className="fixed inset-0 z-50" onClick={() => setProfileOpen(false)} />
              <div className={`absolute ${collapsed ? 'left-full ml-2' : 'left-4 right-4'} bottom-[4.5rem] z-50 bg-white rounded-xl shadow-xl py-2 border border-gray-100`}>
                <button
                  id="profile-view-btn"
                  onClick={() => {
                    onSelectTool('profile');
                    setProfileOpen(false);
                    if (window.innerWidth < 1024) onToggle();
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-[14px] font-medium text-gray-700 hover:bg-gray-50 hover:text-blue-600 cursor-pointer transition-colors"
                >
                  <User size={18} strokeWidth={2} />
                  <span>View Profile</span>
                </button>
                <button
                  id="profile-logout-btn"
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-[14px] font-medium text-red-600 hover:bg-red-50 cursor-pointer transition-colors"
                >
                  <LogOut size={18} strokeWidth={2} />
                  <span>Sign Out</span>
                </button>
              </div>
            </>
          )}
        </div>
      </aside>
    </>
  );
}
