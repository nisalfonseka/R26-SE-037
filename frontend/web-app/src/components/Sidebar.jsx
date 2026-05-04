import { useState } from 'react';
import {
  LayoutDashboard, SpellCheck, Newspaper, PenLine, FileText,
  Menu, X, History, Settings, ChevronLeft, ChevronRight, User, LogOut
} from 'lucide-react';

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

export default function Sidebar({ activeTool, onSelectTool, isOpen, onToggle, collapsed, onCollapse }) {
  const [profileOpen, setProfileOpen] = useState(false);

  const renderNavItem = ({ id, label, icon: Icon, color }) => {
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
            w-full flex items-center ${collapsed ? 'justify-center' : ''} gap-4
            ${collapsed ? 'pl-0 py-3' : 'pl-6 py-3'}
            text-[15px] font-bold transition-all duration-300 cursor-pointer
            ${isActive
              ? 'bg-[#f8fafc] text-gray-800 rounded-l-[1.5rem] shadow-[-5px_0_15px_rgba(0,0,0,0.05)] translate-x-4'
              : 'text-white hover:bg-white/10'
            }
          `}
          style={{
            marginRight: isActive ? '-1rem' : '1rem',
            paddingRight: isActive ? '1rem' : '1rem',
            marginLeft: isActive ? '1rem' : '1rem',
            borderRadius: isActive ? '1.5rem 0 0 1.5rem' : '0.75rem',
          }}
        >
          {/* Icon Circle */}
          <div className={`
            w-9 h-9 rounded-full flex items-center justify-center shrink-0
            ${isActive ? 'bg-white shadow-sm' : 'bg-white/20'}
          `}>
            <Icon size={18} strokeWidth={2.5} className={isActive ? color : 'text-white'} />
          </div>
          {!collapsed && <span className="tracking-wide">{label}</span>}
        </button>
      </div>
    );
  };

  const getLogoColor = () => {
    switch (activeTool) {
      case 'grammar': return 'text-red-500';
      case 'headlines': return 'text-orange-500';
      case 'rewriter': return 'text-purple-500';
      case 'summarizer': return 'text-cyan-500';
      default: return 'text-blue-500';
    }
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
          fixed lg:static inset-y-0 left-0 z-40
          ${collapsed ? 'w-20' : 'w-[17rem]'} bg-transparent
          flex flex-col shrink-0
          transition-all duration-200 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Logo */}
        <div className={`pt-8 pb-6 flex items-center gap-3 ${collapsed ? 'justify-center px-2' : 'px-8'}`}>
          <div className="flex items-center gap-1.5 min-w-0">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shrink-0 shadow-lg relative overflow-hidden transition-colors duration-500">
               <span className={`${getLogoColor()} font-black text-2xl transition-colors duration-500`}>S</span>
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-[19px] text-white tracking-tight leading-none drop-shadow-sm">SinAi</span>
                <span className="text-[11px] text-white/80 font-medium">Assistant</span>
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
        <nav className={`flex-1 py-4 space-y-1`}>
          {MAIN_NAV.map(renderNavItem)}
        </nav>

        {/* Bottom section */}
        <div className={`py-4 space-y-1`}>
          {BOTTOM_NAV.map(renderNavItem)}
        </div>

        {/* User profile */}
        <div className={`relative px-4 pb-6 pt-2`}>
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
