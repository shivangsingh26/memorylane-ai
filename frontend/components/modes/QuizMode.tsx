"use client";

import { useState } from "react";
import { HelpCircle, RefreshCw, CheckCircle, XCircle, ChevronRight, Quote } from "lucide-react";
import { fetchQuiz, type QuizData } from "@/lib/api";
import GlassCard from "@/components/ui/GlassCard";
import LoadingDots from "@/components/ui/LoadingDots";
import clsx from "clsx";

interface QuizQuestion {
  question: string;
  options: string[];
  answer: string;
  memory_snippet?: string;
  explanation: string;
}

interface ExtendedQuizData extends QuizData {
  questions: QuizQuestion[];
}

export default function QuizMode() {
  const [quiz, setQuiz]       = useState<ExtendedQuizData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");
  const [current, setCurrent] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [score, setScore]     = useState(0);
  const [done, setDone]       = useState(false);

  const generate = async () => {
    setLoading(true); setError(""); setQuiz(null);
    setCurrent(0); setSelected(null); setRevealed(false); setScore(0); setDone(false);
    try {
      const data = await fetchQuiz() as ExtendedQuizData;
      if (!data.questions?.length) throw new Error("No questions generated");
      setQuiz(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to generate quiz");
    } finally {
      setLoading(false);
    }
  };

  const reveal = () => {
    if (!selected || !quiz) return;
    setRevealed(true);
    if (selected === quiz.questions[current].answer) setScore((s) => s + 1);
  };

  const next = () => {
    if (!quiz) return;
    if (current < quiz.questions.length - 1) {
      setCurrent((c) => c + 1); setSelected(null); setRevealed(false);
    } else {
      setDone(true);
    }
  };

  const q = quiz?.questions[current];

  return (
    <div className="flex flex-col items-center h-full px-6 py-8 gap-6 overflow-y-auto">
      <div className="text-center animate-fade-up">
        <h2 className="text-xl font-bold text-white">Relationship Quiz</h2>
        <p className="text-sm text-slate-500 mt-1">Questions pulled from your actual chat history</p>
      </div>

      {!quiz && !loading && (
        <button onClick={generate} className="btn-gradient flex items-center gap-2 px-7 py-2.5 rounded-xl text-white font-semibold text-sm animate-fade-up">
          <HelpCircle size={14} /> Generate Quiz
        </button>
      )}

      {loading && (
        <GlassCard className="w-full max-w-lg p-8 flex flex-col items-center gap-3">
          <LoadingDots />
          <p className="text-xs text-slate-500">Mining your chat history for questions…</p>
        </GlassCard>
      )}

      {error && <p className="text-red-400 text-sm">{error}</p>}

      {/* Done screen */}
      {done && quiz && (
        <GlassCard glow className="w-full max-w-lg p-8 text-center animate-fade-up">
          <div className="text-4xl mb-4">{score === quiz.questions.length ? "🏆" : score >= 3 ? "🎉" : "😅"}</div>
          <p className="text-xl font-bold gradient-text">{score}/{quiz.questions.length}</p>
          <p className="text-slate-400 text-sm mt-2">
            {score === quiz.questions.length ? "Perfect. You were actually paying attention." :
             score >= 3 ? "Solid. You know your relationship." : "Hmm. Maybe read the chat more carefully."}
          </p>
          <button onClick={generate} className="mt-6 btn-gradient flex items-center gap-2 px-6 py-2.5 rounded-xl text-white text-sm font-semibold mx-auto">
            <RefreshCw size={13} /> New Quiz
          </button>
        </GlassCard>
      )}

      {/* Question */}
      {q && !done && (
        <div className="w-full max-w-lg animate-fade-up">
          {/* Progress */}
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs text-slate-500">Question {current + 1} of {quiz!.questions.length}</span>
            <span className="text-xs font-semibold text-violet-400">{score} correct</span>
          </div>
          <div className="h-0.5 rounded-full bg-white/5 mb-5">
            <div
              className="h-full rounded-full bg-gradient-to-r from-violet-500 to-pink-500 transition-all"
              style={{ width: `${((current + 1) / quiz!.questions.length) * 100}%` }}
            />
          </div>

          {/* Question card */}
          <GlassCard className="p-5 mb-3">
            <p className="text-sm font-semibold text-white leading-relaxed">{q.question}</p>
          </GlassCard>

          {/* Options */}
          <div className="space-y-2 mb-4">
            {q.options.map((opt) => {
              const isSelected = selected === opt;
              const isCorrect  = opt === q.answer;
              return (
                <button
                  key={opt}
                  onClick={() => !revealed && setSelected(opt)}
                  className={clsx(
                    "w-full glass rounded-xl px-4 py-3 text-left text-sm transition-all",
                    !revealed && !isSelected && "glass-hover text-slate-300 hover:text-white",
                    !revealed && isSelected && "glow-border bg-violet-500/10 text-white",
                    revealed && isCorrect && "border-emerald-500/50 bg-emerald-500/8 text-emerald-300",
                    revealed && isSelected && !isCorrect && "border-red-500/50 bg-red-500/8 text-red-300",
                    revealed && !isSelected && !isCorrect && "opacity-30"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span>{opt}</span>
                    {revealed && isCorrect  && <CheckCircle size={14} className="text-emerald-400 shrink-0" />}
                    {revealed && isSelected && !isCorrect && <XCircle size={14} className="text-red-400 shrink-0" />}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Post-reveal: memory snippet + explanation */}
          {revealed && (
            <div className="space-y-2.5 mb-4 animate-fade-up">
              {q.memory_snippet && (
                <div className="glass rounded-xl px-4 py-3 border-white/[0.06]">
                  <div className="flex items-start gap-2">
                    <Quote size={12} className="text-slate-600 shrink-0 mt-0.5" />
                    <p className="text-xs text-slate-400 italic leading-relaxed">{q.memory_snippet}</p>
                  </div>
                </div>
              )}
              <GlassCard className="p-4 border-violet-500/15">
                <p className="text-xs text-slate-300 leading-relaxed">{q.explanation}</p>
              </GlassCard>
            </div>
          )}

          {/* Action */}
          <div className="flex justify-end">
            {!revealed ? (
              <button
                onClick={reveal}
                disabled={!selected}
                className={clsx(
                  "px-5 py-2.5 rounded-xl text-sm font-semibold transition-all",
                  selected ? "btn-gradient text-white" : "glass text-slate-600 cursor-not-allowed"
                )}
              >
                Reveal Answer
              </button>
            ) : (
              <button onClick={next} className="btn-gradient flex items-center gap-1.5 px-5 py-2.5 rounded-xl text-white text-sm font-semibold">
                {current < quiz!.questions.length - 1 ? "Next" : "See Results"}
                <ChevronRight size={14} />
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
