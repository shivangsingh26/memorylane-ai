"use client";

import { useEffect, useState } from "react";
import { BarChart2, RefreshCw } from "lucide-react";
import { fetchAnalytics, formatSeconds, type AnalyticsData } from "@/lib/api";
import GlassCard from "@/components/ui/GlassCard";
import LoadingDots from "@/components/ui/LoadingDots";

export default function AnalyticsMode() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      setData(await fetchAnalytics());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <div className="flex flex-col items-center gap-3">
        <LoadingDots />
        <p className="text-xs text-slate-500">Loading analytics…</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="flex flex-col items-center justify-center h-full gap-3">
      <p className="text-slate-400 text-sm">{error}</p>
      <button onClick={load} className="btn-gradient px-5 py-2 rounded-xl text-white text-sm">Retry</button>
    </div>
  );

  if (!data) return null;

  const users = Object.keys(data.message_count);
  const topEmojis = Object.entries(data.top_emojis).slice(0, 8);
  const maxMsg = Math.max(...Object.values(data.message_count));

  return (
    <div className="h-full overflow-y-auto px-6 py-6">
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-up">
        {/* Top row: message counts */}
        <div className="grid grid-cols-2 gap-4">
          {users.map((u) => (
            <GlassCard key={u} className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">{u}</p>
                  <p className="text-4xl font-black gradient-text mt-1">
                    {data.message_count[u].toLocaleString()}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">messages sent</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-white">{data.message_percentage[u]}%</p>
                  <p className="text-xs text-slate-500 mt-1">of total</p>
                </div>
              </div>
              {/* Bar */}
              <div className="mt-4 h-1.5 rounded-full bg-white/5">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-violet-500 to-pink-500 transition-all"
                  style={{ width: `${(data.message_count[u] / maxMsg) * 100}%` }}
                />
              </div>
            </GlassCard>
          ))}
        </div>

        {/* Row 2: response time + initiations */}
        <div className="grid grid-cols-3 gap-4">
          <GlassCard className="p-5 col-span-1">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-3">Avg Response</p>
            <p className="text-2xl font-black gradient-text">{formatSeconds(data.response_time?.avg_seconds)}</p>
            <p className="text-[11px] text-slate-600 mt-1">Median: {formatSeconds(data.response_time?.median_seconds)}</p>
          </GlassCard>
          <GlassCard className="p-5 col-span-1">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-3">Total Messages</p>
            <p className="text-2xl font-black gradient-text">{data.total_messages.toLocaleString()}</p>
            <p className="text-[11px] text-slate-600 mt-1">Across all time</p>
          </GlassCard>
          <GlassCard className="p-5 col-span-1">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-3">Initiations</p>
            {users.map((u) => (
              <div key={u} className="flex items-center justify-between">
                <span className="text-xs text-slate-400">{u}</span>
                <span className="text-sm font-bold text-white">{data.initiations[u] ?? 0}×</span>
              </div>
            ))}
          </GlassCard>
        </div>

        {/* Row 3: emojis */}
        <GlassCard className="p-6">
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-4">Top Emojis Together 💬</p>
          <div className="flex flex-wrap gap-3">
            {topEmojis.map(([emoji, count]) => (
              <div key={emoji} className="glass rounded-xl px-4 py-2.5 text-center">
                <div className="text-2xl">{emoji}</div>
                <div className="text-[11px] text-slate-500 mt-1">{count.toLocaleString()}</div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Row 4: top words per user */}
        <div className="grid grid-cols-2 gap-4">
          {users.map((u) => {
            const words = Object.entries(data.top_words[u] ?? {}).slice(0, 10);
            const maxW = words[0]?.[1] ?? 1;
            return (
              <GlassCard key={u} className="p-6">
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-4">{u}'s Top Words</p>
                <div className="space-y-2">
                  {words.map(([word, cnt]) => (
                    <div key={word} className="flex items-center gap-3">
                      <span className="text-xs text-slate-300 w-20 shrink-0 font-medium">{word}</span>
                      <div className="flex-1 h-1.5 rounded-full bg-white/5">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-violet-500/60 to-pink-500/60"
                          style={{ width: `${(cnt / maxW) * 100}%` }}
                        />
                      </div>
                      <span className="text-[11px] text-slate-600 w-10 text-right">{cnt}</span>
                    </div>
                  ))}
                </div>
              </GlassCard>
            );
          })}
        </div>

        {/* Monthly activity */}
        {users.map((u) => {
          const months = Object.entries(data.messages_by_month[u] ?? {}).slice(-6);
          if (!months.length) return null;
          const maxM = Math.max(...months.map(([, v]) => v));
          return (
            <GlassCard key={u} className="p-6">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-4">{u} — Monthly Activity</p>
              <div className="flex items-end gap-2 h-20">
                {months.map(([month, count]) => (
                  <div key={month} className="flex-1 flex flex-col items-center gap-1">
                    <div
                      className="w-full rounded-t-lg bg-gradient-to-t from-violet-500/40 to-pink-500/40 transition-all"
                      style={{ height: `${(count / maxM) * 100}%`, minHeight: "4px" }}
                    />
                    <span className="text-[10px] text-slate-600">{month.slice(5)}</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          );
        })}

        <button
          onClick={load}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors mx-auto"
        >
          <RefreshCw size={12} /> Refresh
        </button>
      </div>
    </div>
  );
}
