"use client";

import clsx from "clsx";
import {
  MessageCircle,
  Flame,
  HelpCircle,
  GitCommitHorizontal,
  BookOpen,
  BarChart2,
} from "lucide-react";

export type Mode = "chat" | "roast" | "quiz" | "timeline" | "story" | "analytics";

const MODES: { id: Mode; label: string; icon: React.ElementType; description: string }[] = [
  { id: "chat",      label: "Chat",      icon: MessageCircle,       description: "Ask anything" },
  { id: "roast",     label: "Roast",     icon: Flame,               description: "Get roasted 🔥" },
  { id: "quiz",      label: "Quiz",      icon: HelpCircle,          description: "Test your knowledge" },
  { id: "timeline",  label: "Timeline",  icon: GitCommitHorizontal, description: "Your love story" },
  { id: "story",     label: "Story",     icon: BookOpen,            description: "Creative writing" },
  { id: "analytics", label: "Analytics", icon: BarChart2,           description: "Stats & insights" },
];

interface Props {
  active: Mode;
  onChange: (m: Mode) => void;
  chatLoaded: boolean;
}

export default function Sidebar({ active, onChange, chatLoaded }: Props) {
  return (
    <aside className="flex flex-col h-full w-[220px] shrink-0 glass border-r border-white/[0.06] py-6 px-3 gap-1">
      {/* Logo */}
      <div className="px-3 mb-6">
        <span className="gradient-text text-xl font-black tracking-tight">MemoryLane</span>
        <p className="text-xs text-slate-500 mt-0.5">Your relationship oracle ✨</p>
      </div>

      {/* Nav items */}
      {MODES.map(({ id, label, icon: Icon, description }) => {
        const isActive = active === id;
        const locked = !chatLoaded && id !== "chat";
        return (
          <button
            key={id}
            onClick={() => !locked && onChange(id)}
            disabled={locked}
            title={locked ? "Upload a chat file first" : description}
            className={clsx(
              "group flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-200",
              isActive
                ? "glow-border bg-violet-500/10 text-white"
                : "text-slate-400 hover:text-white hover:bg-white/[0.05]",
              locked && "opacity-35 cursor-not-allowed"
            )}
          >
            <div
              className={clsx(
                "p-1.5 rounded-lg transition-colors",
                isActive ? "bg-violet-500/20" : "bg-white/[0.05] group-hover:bg-white/10"
              )}
            >
              <Icon
                size={15}
                className={clsx(isActive ? "text-violet-400" : "text-slate-400 group-hover:text-slate-200")}
              />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium leading-tight">{label}</p>
              <p className={clsx("text-[11px] leading-tight mt-0.5", isActive ? "text-violet-400/70" : "text-slate-600")}>
                {description}
              </p>
            </div>
          </button>
        );
      })}

      {/* Bottom hint */}
      <div className="mt-auto px-3 pt-4 border-t border-white/[0.06]">
        <p className="text-[11px] text-slate-600 leading-relaxed">
          {chatLoaded
            ? "✅ Chat data loaded"
            : "⬆️ Upload a chat file to unlock all modes"}
        </p>
      </div>
    </aside>
  );
}
