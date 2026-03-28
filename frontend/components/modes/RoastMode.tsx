"use client";

import { useState } from "react";
import { Flame, RefreshCw } from "lucide-react";
import { fetchRoast } from "@/lib/api";
import GlassCard from "@/components/ui/GlassCard";
import LoadingDots from "@/components/ui/LoadingDots";
import clsx from "clsx";

interface RoastData {
  sections: { label: string; text: string }[];
  verdict: string;
  save: string;
}

const TARGETS = [
  { id: "Shivang", label: "Shivang",  sub: "The unbothered one" },
  { id: "Krishna", label: "Krishna",  sub: "The expressive one" },
  { id: "both",    label: "Both",     sub: "Fair and even" },
];

const SECTION_ACCENTS: Record<string, string> = {
  "The Numbers":  "text-cyan-400 border-cyan-500/20",
  "Caught In 4K": "text-orange-400 border-orange-500/20",
  "The Habit":    "text-pink-400 border-pink-500/20",
  "The Roast":    "text-violet-400 border-violet-500/20",
};

export default function RoastMode() {
  const [target, setTarget]   = useState("both");
  const [roast, setRoast]     = useState<RoastData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const generate = async () => {
    setLoading(true);
    setRoast(null);
    setError("");
    try {
      const data = await fetchRoast(target) as unknown as RoastData;
      setRoast(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to generate roast");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center h-full px-6 py-8 gap-6 overflow-y-auto">
      {/* Header */}
      <div className="text-center animate-fade-up">
        <h2 className="text-xl font-bold text-white">Roast Mode</h2>
        <p className="text-sm text-slate-500 mt-1">Based on 9 months of actual data. No mercy.</p>
      </div>

      {/* Target selector */}
      <div className="flex gap-2 animate-fade-up" style={{ animationDelay: "0.05s" }}>
        {TARGETS.map(({ id, label, sub }) => (
          <button
            key={id}
            onClick={() => setTarget(id)}
            className={clsx(
              "glass rounded-xl px-5 py-3 text-center transition-all",
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
        className="btn-gradient flex items-center gap-2 px-7 py-2.5 rounded-xl text-white font-semibold text-sm"
      >
        {loading ? <><RefreshCw size={14} className="animate-spin" /> Generating…</> : <><Flame size={14} /> Generate Roast</>}
      </button>

      {loading && (
        <GlassCard className="w-full max-w-xl p-8 flex flex-col items-center gap-3">
          <LoadingDots />
          <p className="text-xs text-slate-500">Reading 9 months of receipts…</p>
        </GlassCard>
      )}

      {error && <p className="text-red-400 text-sm">{error}</p>}

      {/* Structured roast output */}
      {roast && !loading && (
        <div className="w-full max-w-xl space-y-3 animate-fade-up">
          {/* Sections */}
          {roast.sections.map((section, i) => {
            const accent = SECTION_ACCENTS[section.label] ?? "text-violet-400 border-violet-500/20";
            const [colorClass] = accent.split(" ");
            return (
              <GlassCard key={i} className="p-5">
                <p className={clsx("text-[11px] font-semibold uppercase tracking-widest mb-3", colorClass)}>
                  {section.label}
                </p>
                <p className="text-sm text-slate-200 leading-relaxed">{section.text}</p>
              </GlassCard>
            );
          })}

          {/* Verdict */}
          {roast.verdict && (
            <div className="glass rounded-xl px-5 py-4 border-orange-500/20">
              <p className="text-[11px] font-semibold uppercase tracking-widest text-orange-400 mb-2">Verdict</p>
              <p className="text-white font-semibold text-sm italic">"{roast.verdict}"</p>
            </div>
          )}

          {/* Warm close */}
          {roast.save && (
            <div className="px-5 py-3">
              <p className="text-sm text-slate-400 leading-relaxed">{roast.save}</p>
            </div>
          )}

          <button
            onClick={generate}
            className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-400 transition-colors mx-auto pt-1"
          >
            <RefreshCw size={11} /> Generate another
          </button>
        </div>
      )}
    </div>
  );
}
