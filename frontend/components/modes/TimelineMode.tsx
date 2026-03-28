"use client";

import { useState } from "react";
import { GitCommitHorizontal, RefreshCw, Sparkles } from "lucide-react";
import { fetchTimeline, type TimelineData } from "@/lib/api";
import GlassCard from "@/components/ui/GlassCard";
import LoadingDots from "@/components/ui/LoadingDots";

export default function TimelineMode() {
  const [data, setData] = useState<TimelineData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    setLoading(true);
    setError("");
    setData(null);
    try {
      setData(await fetchTimeline());
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
        <div className="text-5xl mb-3">💫</div>
        <h2 className="text-2xl font-bold text-white">Relationship Timeline</h2>
        <p className="text-sm text-slate-500 mt-1.5 max-w-sm">
          Your love story, chapter by chapter
        </p>
      </div>

      {!data && !loading && (
        <button
          onClick={generate}
          className="btn-gradient flex items-center gap-2 px-8 py-3 rounded-2xl text-white font-semibold text-sm animate-fade-up"
        >
          <GitCommitHorizontal size={15} /> Generate Timeline
        </button>
      )}

      {loading && (
        <GlassCard className="w-full max-w-2xl p-8 flex flex-col items-center gap-3">
          <LoadingDots />
          <p className="text-xs text-slate-500">Mapping your relationship journey…</p>
        </GlassCard>
      )}

      {error && <div className="text-red-400 text-sm bg-red-500/10 rounded-xl px-4 py-3">{error}</div>}

      {data && !loading && (
        <div className="w-full max-w-2xl animate-fade-up space-y-8">
          {/* Summary */}
          <GlassCard glow className="p-6">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={14} className="text-violet-400" />
              <span className="text-xs font-semibold text-violet-400 uppercase tracking-widest">Your Story</span>
            </div>
            <p className="text-slate-200 text-sm leading-relaxed">{data.overall_summary}</p>
          </GlassCard>

          {/* Phases */}
          <div className="relative">
            {/* Connecting line */}
            <div className="absolute left-5 top-6 bottom-6 timeline-line" />

            <div className="space-y-6">
              {data.phases.map((phase, i) => (
                <div key={i} className="flex gap-5 animate-fade-up" style={{ animationDelay: `${i * 0.1}s` }}>
                  {/* Node */}
                  <div className="relative z-10 shrink-0 w-10 h-10 rounded-full bg-[#070711] border-2 border-violet-500/50 flex items-center justify-center">
                    <span className="text-sm">{["🌱","💬","🔥","💕","⭐","🌟"][i % 6]}</span>
                  </div>

                  {/* Card */}
                  <GlassCard className="flex-1 p-5 hover:border-white/12 transition-colors">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <h3 className="text-sm font-bold text-white">{phase.name}</h3>
                      <span className="text-[11px] text-violet-400 bg-violet-500/10 px-2 py-0.5 rounded-full shrink-0">
                        {phase.period}
                      </span>
                    </div>
                    <p className="text-xs text-violet-300/80 mb-2 font-medium">{phase.vibe}</p>
                    <p className="text-sm text-slate-400 leading-relaxed">{phase.description}</p>
                    {phase.key_moment && (
                      <div className="mt-3 pl-3 border-l-2 border-violet-500/30">
                        <p className="text-xs text-slate-500 italic">"{phase.key_moment}"</p>
                      </div>
                    )}
                  </GlassCard>
                </div>
              ))}
            </div>
          </div>

          {/* Fun facts */}
          {data.fun_facts?.length > 0 && (
            <GlassCard className="p-6">
              <p className="text-xs font-semibold text-pink-400 uppercase tracking-widest mb-4">Fun Facts 🎉</p>
              <div className="space-y-2.5">
                {data.fun_facts.map((fact, i) => (
                  <div key={i} className="flex items-start gap-2.5">
                    <span className="text-violet-400 text-sm shrink-0 mt-0.5">•</span>
                    <p className="text-sm text-slate-300">{fact}</p>
                  </div>
                ))}
              </div>
            </GlassCard>
          )}

          <button
            onClick={generate}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors mx-auto"
          >
            <RefreshCw size={12} /> Regenerate
          </button>
        </div>
      )}
    </div>
  );
}
