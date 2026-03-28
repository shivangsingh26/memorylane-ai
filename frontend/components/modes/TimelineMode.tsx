"use client";

import { useState } from "react";
import { GitCommitHorizontal, RefreshCw } from "lucide-react";
import { fetchTimeline, type TimelineData } from "@/lib/api";
import GlassCard from "@/components/ui/GlassCard";
import LoadingDots from "@/components/ui/LoadingDots";

interface ExtendedPhase {
  name: string;
  date_range?: string;
  period: string;
  vibe: string;
  description: string;
  key_quote?: string;
  key_moment?: string;
}

interface ExtendedTimeline extends Omit<TimelineData, "phases"> {
  phases: ExtendedPhase[];
}

const PHASE_ICONS = ["🌱", "💬", "🔥", "💕", "✨", "🌟", "🎯", "💫"];

export default function TimelineMode() {
  const [data, setData]       = useState<ExtendedTimeline | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const generate = async () => {
    setLoading(true); setError(""); setData(null);
    try {
      setData(await fetchTimeline() as ExtendedTimeline);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center h-full px-6 py-8 gap-6 overflow-y-auto">
      <div className="text-center animate-fade-up">
        <h2 className="text-xl font-bold text-white">Relationship Timeline</h2>
        <p className="text-sm text-slate-500 mt-1">Built from memories sampled across every month</p>
      </div>

      {!data && !loading && (
        <button onClick={generate} className="btn-gradient flex items-center gap-2 px-7 py-2.5 rounded-xl text-white font-semibold text-sm animate-fade-up">
          <GitCommitHorizontal size={14} /> Generate Timeline
        </button>
      )}

      {loading && (
        <GlassCard className="w-full max-w-2xl p-8 flex flex-col items-center gap-3">
          <LoadingDots />
          <p className="text-xs text-slate-500">Mapping your relationship arc month by month…</p>
        </GlassCard>
      )}

      {error && <p className="text-red-400 text-sm">{error}</p>}

      {data && !loading && (
        <div className="w-full max-w-2xl space-y-6 animate-fade-up">
          {/* Summary */}
          <GlassCard glow className="p-6">
            <p className="text-xs font-semibold text-violet-400 uppercase tracking-widest mb-3">The Story So Far</p>
            <p className="text-sm text-slate-200 leading-relaxed">{data.overall_summary}</p>
          </GlassCard>

          {/* Phases */}
          <div className="relative">
            <div className="absolute left-5 top-6 bottom-6 timeline-line" />
            <div className="space-y-4">
              {data.phases.map((phase, i) => (
                <div key={i} className="flex gap-4 animate-fade-up" style={{ animationDelay: `${i * 0.08}s` }}>
                  {/* Node */}
                  <div className="relative z-10 shrink-0 w-10 h-10 rounded-full bg-[#070711] border-2 border-violet-500/40 flex items-center justify-center">
                    <span className="text-base">{PHASE_ICONS[i % PHASE_ICONS.length]}</span>
                  </div>

                  <GlassCard className="flex-1 p-5">
                    {/* Header row */}
                    <div className="flex items-start justify-between gap-3 mb-1.5">
                      <p className="text-sm font-bold text-white">{phase.name}</p>
                      {(phase.date_range || phase.period) && (
                        <span className="text-[11px] text-violet-400 bg-violet-500/10 px-2.5 py-0.5 rounded-full shrink-0 border border-violet-500/20">
                          {phase.date_range || phase.period}
                        </span>
                      )}
                    </div>

                    {/* Vibe */}
                    <p className="text-xs text-slate-500 mb-3">{phase.vibe}</p>

                    {/* Description */}
                    <p className="text-sm text-slate-300 leading-relaxed">{phase.description}</p>

                    {/* Key quote */}
                    {(phase.key_quote || phase.key_moment) && (
                      <div className="mt-3.5 pl-3 border-l-2 border-violet-500/25">
                        <p className="text-xs text-slate-500 italic leading-relaxed">
                          "{phase.key_quote || phase.key_moment}"
                        </p>
                      </div>
                    )}
                  </GlassCard>
                </div>
              ))}
            </div>
          </div>

          {/* Fun facts */}
          {data.fun_facts?.length > 0 && (
            <GlassCard className="p-5">
              <p className="text-xs font-semibold text-pink-400 uppercase tracking-widest mb-4">By The Numbers</p>
              <div className="space-y-2.5">
                {data.fun_facts.map((fact, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <span className="text-slate-600 text-xs shrink-0 mt-0.5">—</span>
                    <p className="text-sm text-slate-300 leading-relaxed">{fact}</p>
                  </div>
                ))}
              </div>
            </GlassCard>
          )}

          <button onClick={generate} className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-400 transition-colors mx-auto">
            <RefreshCw size={11} /> Regenerate
          </button>
        </div>
      )}
    </div>
  );
}
