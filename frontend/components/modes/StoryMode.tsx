"use client";

import { useState } from "react";
import { BookOpen, RefreshCw } from "lucide-react";
import { fetchStory } from "@/lib/api";
import GlassCard from "@/components/ui/GlassCard";
import LoadingDots from "@/components/ui/LoadingDots";
import clsx from "clsx";

const STYLES = [
  { id: "romantic",    emoji: "💕", label: "Romantic",     sub: "Heartfelt short story" },
  { id: "poem",        emoji: "🎭", label: "Poem",          sub: "Playful Hinglish poem" },
  { id: "bollywood",   emoji: "🎬", label: "Bollywood",    sub: "Dramatic filmy style" },
  { id: "roast_story", emoji: "😂", label: "Roast Story",  sub: "Funny & savage retelling" },
  { id: "fairy_tale",  emoji: "🏰", label: "Fairy Tale",   sub: "Modern fairy tale" },
];

export default function StoryMode() {
  const [style, setStyle] = useState("romantic");
  const [story, setStory] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    setLoading(true);
    setStory("");
    setError("");
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
      {/* Header */}
      <div className="text-center animate-fade-up">
        <div className="text-5xl mb-3">✍️</div>
        <h2 className="text-2xl font-bold text-white">Story Generator</h2>
        <p className="text-sm text-slate-500 mt-1.5 max-w-sm">
          Your relationship, rewritten in any style you want
        </p>
      </div>

      {/* Style picker */}
      <div className="grid grid-cols-5 gap-2.5 w-full max-w-2xl animate-fade-up" style={{ animationDelay: "0.1s" }}>
        {STYLES.map(({ id, emoji, label, sub }) => (
          <button
            key={id}
            onClick={() => setStyle(id)}
            className={clsx(
              "glass rounded-2xl px-3 py-3.5 text-center transition-all",
              style === id
                ? "glow-border bg-violet-500/10 text-white"
                : "glass-hover text-slate-400 hover:text-white"
            )}
          >
            <div className="text-2xl mb-1.5">{emoji}</div>
            <p className="text-xs font-semibold">{label}</p>
            <p className="text-[10px] text-slate-600 mt-0.5 leading-tight">{sub}</p>
          </button>
        ))}
      </div>

      {/* Generate */}
      <button
        onClick={generate}
        disabled={loading}
        className="btn-gradient flex items-center gap-2 px-8 py-3 rounded-2xl text-white font-semibold text-sm"
      >
        {loading ? (
          <><RefreshCw size={15} className="animate-spin" /> Writing…</>
        ) : (
          <><BookOpen size={15} /> Generate Story</>
        )}
      </button>

      {loading && (
        <GlassCard className="w-full max-w-2xl p-8 flex flex-col items-center gap-3">
          <LoadingDots />
          <p className="text-xs text-slate-500">The narrator is consulting your memories…</p>
        </GlassCard>
      )}

      {error && <div className="text-red-400 text-sm bg-red-500/10 rounded-xl px-4 py-3">{error}</div>}

      {story && !loading && (
        <GlassCard glow className="w-full max-w-2xl p-8 animate-fade-up">
          <div className="flex items-center gap-2 mb-5">
            <BookOpen size={14} className="text-pink-400" />
            <span className="text-xs font-semibold text-pink-400 uppercase tracking-widest">
              {STYLES.find((s) => s.id === style)?.label} Mode
            </span>
          </div>
          <div
            className="text-slate-200 text-sm leading-[1.85] whitespace-pre-wrap font-[Georgia,serif]"
            style={{ fontFamily: "'Georgia', 'Times New Roman', serif" }}
          >
            {story}
          </div>
          <button
            onClick={generate}
            className="mt-6 flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            <RefreshCw size={12} /> Write another
          </button>
        </GlassCard>
      )}
    </div>
  );
}
