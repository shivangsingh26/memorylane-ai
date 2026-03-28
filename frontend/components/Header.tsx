"use client";

import { Upload, Trash2, User } from "lucide-react";
import type { Mode } from "./Sidebar";
import clsx from "clsx";

const MODE_LABELS: Record<Mode, string> = {
  chat:      "Chat",
  roast:     "Roast Mode 🔥",
  quiz:      "Quiz Mode 🧠",
  timeline:  "Timeline 💫",
  story:     "Story Generator ✍️",
  analytics: "Analytics 📊",
};

interface Props {
  mode: Mode;
  user: string;
  onUserChange: (u: string) => void;
  onUploadClick: () => void;
  onDeleteClick: () => void;
  chatLoaded: boolean;
}

const USERS = ["Shivang", "Krishna"];

export default function Header({
  mode,
  user,
  onUserChange,
  onUploadClick,
  onDeleteClick,
  chatLoaded,
}: Props) {
  return (
    <header className="flex items-center justify-between px-6 py-3.5 border-b border-white/[0.06] shrink-0">
      {/* Mode title */}
      <div>
        <h1 className="text-lg font-semibold text-white">{MODE_LABELS[mode]}</h1>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-2">
        {/* User picker */}
        <div className="flex items-center gap-1.5 glass rounded-xl px-3 py-1.5">
          <User size={13} className="text-violet-400" />
          <span className="text-xs text-slate-400 mr-1">Asking as</span>
          <div className="flex gap-1">
            {USERS.map((u) => (
              <button
                key={u}
                onClick={() => onUserChange(u)}
                className={clsx(
                  "text-xs px-2.5 py-1 rounded-lg font-medium transition-all",
                  user === u
                    ? "bg-violet-500/30 text-violet-300 border border-violet-500/40"
                    : "text-slate-500 hover:text-slate-300 hover:bg-white/5"
                )}
              >
                {u}
              </button>
            ))}
          </div>
        </div>

        {/* Upload */}
        <button
          onClick={onUploadClick}
          className="btn-gradient flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-white text-xs font-semibold"
        >
          <Upload size={13} />
          {chatLoaded ? "Re-upload" : "Upload Chat"}
        </button>

        {/* Delete */}
        {chatLoaded && (
          <button
            onClick={onDeleteClick}
            className="glass glass-hover flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-red-400 hover:text-red-300 text-xs font-medium transition-colors"
          >
            <Trash2 size={13} />
            Clear
          </button>
        )}
      </div>
    </header>
  );
}
