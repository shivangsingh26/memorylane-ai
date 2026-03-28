"use client";

import { useState } from "react";
import { BookOpen, RefreshCw } from "lucide-react";
import { fetchStory } from "@/lib/api";
import GlassCard from "@/components/ui/GlassCard";
import LoadingDots from "@/components/ui/LoadingDots";
import clsx from "clsx";

const STYLES = [
  { id: "romantic",    label: "Romantic",    sub: "Heartfelt short story" },
  { id: "poem",        label: "Poem",        sub: "Hinglish poem" },
  { id: "bollywood",   label: "Bollywood",   sub: "Filmy drama" },
  { id: "roast_story", label: "Roast Story", sub: "Honest & savage" },
  { id: "fairy_tale",  label: "Fairy Tale",  sub: "Modern fairy tale" },
];

export default function StoryMode() {
  const [style, setStyle]     = useState("romantic");
  const [story, setStory]     = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const generate = async () => {
    setLoading(true); setStory(""); setError("");
    try {
      setStory(await fetchStory(style));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center h-full px-6 py-8 gap-6 overflow-y-auto">
      <div className="text-center animate-fade-up">
        <h2 className="text-xl font-bold text-white">Story Generator</h2>
        <p className="text-sm text-slate-500 mt-1">Your relationship, rewritten in any style</p>
      </div>

      {/* Style picker */}
      <div className="flex gap-2 flex-wrap justify-center animate-fade-up" style={{ animationDelay: "0.05s" }}>
        {STYLES.map(({ id, label, sub }) => (
          <button
            key={id}
            onClick={() => setStyle(id)}
            className={clsx(
              "glass rounded-xl px-4 py-2.5 text-center transition-all",
              style === id
                ? "glow-border bg-violet-500/10 text-white"
                : "glass-hover text-slate-400 hover:text-white"
            )}
          >
            <p className="text-sm font-semibold">{label}</p>
            <p className="text-[11px] text-slate-500 mt-0.5">{sub}</p>
          </button>
        ))}
      </div>

      <button
        onClick={generate}
        disabled={loading}
        className="btn-gradient flex items-center gap-2 px-7 py-2.5 rounded-xl text-white font-semibold text-sm"
      >
        {loading ? <><RefreshCw size={14} className="animate-spin" /> Writing…</> : <><BookOpen size={14} /> Generate</>}
      </button>

      {loading && (
        <GlassCard className="w-full max-w-2xl p-8 flex flex-col items-center gap-3">
          <LoadingDots />
          <p className="text-xs text-slate-500">The narrator is going through your memories…</p>
        </GlassCard>
      )}

      {error && <p className="text-red-400 text-sm">{error}</p>}

      {story && !loading && (
        <GlassCard glow className="w-full max-w-2xl animate-fade-up">
          {/* Label bar */}
          <div className="flex items-center justify-between px-7 pt-6 pb-4 border-b border-white/[0.06]">
            <div className="flex items-center gap-2">
              <BookOpen size={13} className="text-slate-500" />
              <span className="text-xs text-slate-500 font-medium">
                {STYLES.find((s) => s.id === style)?.label}
              </span>
            </div>
            <button
              onClick={generate}
              className="flex items-center gap-1 text-[11px] text-slate-600 hover:text-slate-400 transition-colors"
            >
              <RefreshCw size={11} /> Rewrite
            </button>
          </div>

          {/* Story body — serif font for reading comfort */}
          <div className="px-7 py-6">
            <p
              className="text-slate-200 text-[15px] leading-[1.9] whitespace-pre-wrap"
              style={{ fontFamily: "'Georgia', 'Times New Roman', serif" }}
            >
              {story}
            </p>
          </div>
        </GlassCard>
      )}
    </div>
  );
}
