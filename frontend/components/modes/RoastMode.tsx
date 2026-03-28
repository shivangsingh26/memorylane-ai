"use client";

import { useState } from "react";
import { Flame, RefreshCw } from "lucide-react";
import { fetchRoast } from "@/lib/api";
import GlassCard from "@/components/ui/GlassCard";
import LoadingDots from "@/components/ui/LoadingDots";
import clsx from "clsx";

const TARGETS = [
  { id: "Shivang", label: "Roast Shivang 🤡", sub: "The unbothered clown" },
  { id: "Krishna", label: "Roast Krishna 😭", sub: "The expressive one" },
  { id: "both",    label: "Roast Both 💥",    sub: "Fair and savage" },
];

export default function RoastMode() {
  const [target, setTarget] = useState("both");
  const [roast, setRoast] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    setLoading(true);
    setRoast("");
    setError("");
    try {
      const text = await fetchRoast(target);
      setRoast(text);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to generate roast");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center h-full px-6 py-8 gap-6 overflow-y-auto">
      {/* Heading */}
      <div className="text-center animate-fade-up">
        <div className="text-5xl mb-3">🔥</div>
        <h2 className="text-2xl font-bold text-white">Roast Mode</h2>
        <p className="text-sm text-slate-500 mt-1.5 max-w-sm">
          Based on actual stats from your chat — friendly fire only 😏
        </p>
      </div>

      {/* Target selector */}
      <div className="grid grid-cols-3 gap-3 w-full max-w-lg animate-fade-up" style={{ animationDelay: "0.1s" }}>
        {TARGETS.map(({ id, label, sub }) => (
          <button
            key={id}
            onClick={() => setTarget(id)}
            className={clsx(
              "glass rounded-2xl px-4 py-3.5 text-center transition-all",
              target === id
                ? "glow-border bg-violet-500/10 text-white"
                : "glass-hover text-slate-400 hover:text-white"
            )}
          >
            <p className="text-sm font-semibold">{label}</p>
            <p className="text-[11px] text-slate-500 mt-0.5">{sub}</p>
          </button>
        ))}
      </div>

      {/* Generate button */}
      <button
        onClick={generate}
        disabled={loading}
        className="btn-gradient flex items-center gap-2 px-8 py-3 rounded-2xl text-white font-semibold text-sm"
      >
        {loading ? (
          <><RefreshCw size={15} className="animate-spin" /> Generating…</>
        ) : (
          <><Flame size={15} /> Generate Roast</>
        )}
      </button>

      {/* Loading */}
      {loading && (
        <GlassCard className="w-full max-w-2xl p-8 flex flex-col items-center gap-3">
          <LoadingDots />
          <p className="text-xs text-slate-500">Reading 85k messages for ammo…</p>
        </GlassCard>
      )}

      {/* Roast result */}
      {roast && !loading && (
        <GlassCard glow className="w-full max-w-2xl p-8 animate-fade-up">
          <div className="flex items-center gap-2 mb-4">
            <Flame size={16} className="text-orange-400" />
            <span className="text-xs font-semibold text-orange-400 uppercase tracking-widest">The Roast</span>
          </div>
          <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">{roast}</p>
          <button
            onClick={generate}
            className="mt-5 flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            <RefreshCw size={12} /> Generate another
          </button>
        </GlassCard>
      )}

      {error && (
        <div className="text-red-400 text-sm bg-red-500/10 rounded-xl px-4 py-3">{error}</div>
      )}
    </div>
  );
}
