"use client";

import { useState } from "react";
import { HelpCircle, RefreshCw, CheckCircle, XCircle, ChevronRight } from "lucide-react";
import { fetchQuiz, type QuizData } from "@/lib/api";
import GlassCard from "@/components/ui/GlassCard";
import LoadingDots from "@/components/ui/LoadingDots";
import clsx from "clsx";

export default function QuizMode() {
  const [quiz, setQuiz] = useState<QuizData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [current, setCurrent] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);

  const generate = async () => {
    setLoading(true);
    setError("");
    setQuiz(null);
    setCurrent(0);
    setSelected(null);
    setRevealed(false);
    setScore(0);
    setDone(false);
    try {
      const data = await fetchQuiz();
      if (!data.questions?.length) throw new Error("No questions generated");
      setQuiz(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to generate quiz");
    } finally {
      setLoading(false);
    }
  };

  const pick = (option: string) => {
    if (revealed) return;
    setSelected(option);
  };

  const reveal = () => {
    if (!selected || !quiz) return;
    setRevealed(true);
    if (selected === quiz.questions[current].answer) {
      setScore((s) => s + 1);
    }
  };

  const next = () => {
    if (!quiz) return;
    if (current < quiz.questions.length - 1) {
      setCurrent((c) => c + 1);
      setSelected(null);
      setRevealed(false);
    } else {
      setDone(true);
    }
  };

  const q = quiz?.questions[current];

  return (
    <div className="flex flex-col items-center h-full px-6 py-8 gap-6 overflow-y-auto">
      {/* Header */}
      <div className="text-center animate-fade-up">
        <div className="text-5xl mb-3">🧠</div>
        <h2 className="text-2xl font-bold text-white">Relationship Quiz</h2>
        <p className="text-sm text-slate-500 mt-1.5 max-w-sm">
          How well do you know your own relationship?
        </p>
      </div>

      {/* Start / regenerate */}
      {!quiz && !loading && (
        <button
          onClick={generate}
          className="btn-gradient flex items-center gap-2 px-8 py-3 rounded-2xl text-white font-semibold text-sm animate-fade-up"
        >
          <HelpCircle size={15} /> Generate Quiz
        </button>
      )}

      {loading && (
        <GlassCard className="w-full max-w-lg p-8 flex flex-col items-center gap-3">
          <LoadingDots />
          <p className="text-xs text-slate-500">Mining your chat history for juicy questions…</p>
        </GlassCard>
      )}

      {error && (
        <div className="text-red-400 text-sm bg-red-500/10 rounded-xl px-4 py-3">{error}</div>
      )}

      {/* Done screen */}
      {done && quiz && (
        <GlassCard glow className="w-full max-w-lg p-8 text-center animate-fade-up">
          <div className="text-5xl mb-4">{score === quiz.questions.length ? "🏆" : score >= 3 ? "🎉" : "😅"}</div>
          <h3 className="text-xl font-bold text-white">Quiz Complete!</h3>
          <p className="text-3xl font-black gradient-text mt-2">{score}/{quiz.questions.length}</p>
          <p className="text-slate-400 text-sm mt-1">
            {score === quiz.questions.length
              ? "Perfect score! You really pay attention 👀"
              : score >= 3
              ? "Solid! You know your relationship well 💕"
              : "Hmm… maybe talk more? 😂"}
          </p>
          <button
            onClick={generate}
            className="mt-6 btn-gradient flex items-center gap-2 px-6 py-2.5 rounded-xl text-white text-sm font-semibold mx-auto"
          >
            <RefreshCw size={14} /> Play Again
          </button>
        </GlassCard>
      )}

      {/* Question card */}
      {q && !done && (
        <div className="w-full max-w-lg animate-fade-up">
          {/* Progress */}
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs text-slate-500">
              Question {current + 1} of {quiz!.questions.length}
            </span>
            <span className="text-xs font-semibold text-violet-400">Score: {score}</span>
          </div>
          <div className="h-1 rounded-full bg-white/5 mb-6">
            <div
              className="h-full rounded-full bg-gradient-to-r from-violet-500 to-pink-500 transition-all"
              style={{ width: `${((current + 1) / quiz!.questions.length) * 100}%` }}
            />
          </div>

          {/* Question */}
          <GlassCard className="p-6 mb-4">
            <p className="text-base font-semibold text-white leading-relaxed">{q.question}</p>
          </GlassCard>

          {/* Options */}
          <div className="grid grid-cols-1 gap-2.5 mb-4">
            {q.options.map((opt) => {
              const isSelected = selected === opt;
              const isCorrect  = opt === q.answer;
              return (
                <button
                  key={opt}
                  onClick={() => pick(opt)}
                  className={clsx(
                    "glass rounded-xl px-5 py-3.5 text-left text-sm font-medium transition-all",
                    !revealed && !isSelected && "glass-hover text-slate-300 hover:text-white",
                    !revealed && isSelected && "glow-border bg-violet-500/15 text-white",
                    revealed && isCorrect && "border-emerald-500/60 bg-emerald-500/10 text-emerald-300",
                    revealed && isSelected && !isCorrect && "border-red-500/60 bg-red-500/10 text-red-300",
                    revealed && !isSelected && !isCorrect && "opacity-40"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span>{opt}</span>
                    {revealed && isCorrect && <CheckCircle size={15} className="text-emerald-400 shrink-0" />}
                    {revealed && isSelected && !isCorrect && <XCircle size={15} className="text-red-400 shrink-0" />}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Explanation */}
          {revealed && (
            <GlassCard className="p-4 mb-4 animate-fade-up border-violet-500/20">
              <p className="text-xs text-slate-300 leading-relaxed">💡 {q.explanation}</p>
            </GlassCard>
          )}

          {/* Actions */}
          <div className="flex justify-end">
            {!revealed ? (
              <button
                onClick={reveal}
                disabled={!selected}
                className={clsx(
                  "px-6 py-2.5 rounded-xl text-sm font-semibold transition-all",
                  selected ? "btn-gradient text-white" : "glass text-slate-600 cursor-not-allowed"
                )}
              >
                Reveal Answer
              </button>
            ) : (
              <button
                onClick={next}
                className="btn-gradient flex items-center gap-1.5 px-6 py-2.5 rounded-xl text-white text-sm font-semibold"
              >
                {current < quiz!.questions.length - 1 ? "Next" : "Finish"}
                <ChevronRight size={15} />
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
