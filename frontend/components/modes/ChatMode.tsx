"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Sparkles } from "lucide-react";
import { streamChat } from "@/lib/api";
import LoadingDots from "@/components/ui/LoadingDots";
import clsx from "clsx";

interface Message {
  id: string;
  role: "user" | "bot";
  content: string;
  streaming?: boolean;
}

interface Props {
  user: string;
}

const STARTERS = [
  "What do we talk about the most? 🤔",
  "Who texts more — me or Krishna?",
  "What's our funniest conversation?",
  "Tell me something sweet about us 💕",
  "What are our biggest inside jokes?",
];

export default function ChatMode({ user }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = useCallback(
    async (text: string) => {
      if (!text.trim() || loading) return;
      setInput("");

      const userMsg: Message = { id: Date.now().toString(), role: "user", content: text };
      const botId = (Date.now() + 1).toString();
      const botMsg: Message = { id: botId, role: "bot", content: "", streaming: true };

      setMessages((prev) => [...prev, userMsg, botMsg]);
      setLoading(true);

      try {
        for await (const token of streamChat(text, user)) {
          setMessages((prev) =>
            prev.map((m) => (m.id === botId ? { ...m, content: m.content + token } : m))
          );
        }
      } catch (e: unknown) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === botId
              ? { ...m, content: "Something went wrong 😔 Make sure the backend is running.", streaming: false }
              : m
          )
        );
      } finally {
        setMessages((prev) =>
          prev.map((m) => (m.id === botId ? { ...m, streaming: false } : m))
        );
        setLoading(false);
      }
    },
    [loading, user]
  );

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-6 animate-fade">
            <div className="text-center">
              <div className="text-4xl mb-3">✨</div>
              <p className="text-lg font-semibold text-white">Ask me anything about you two</p>
              <p className="text-sm text-slate-500 mt-1">I remember every conversation</p>
            </div>
            <div className="grid grid-cols-1 gap-2 w-full max-w-md">
              {STARTERS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="glass glass-hover text-left px-4 py-3 rounded-xl text-sm text-slate-300 hover:text-white transition-all"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={clsx("flex animate-fade-up", msg.role === "user" ? "justify-end" : "justify-start")}
            >
              {msg.role === "bot" && (
                <div className="w-7 h-7 rounded-full bg-violet-500/20 border border-violet-500/30 flex items-center justify-center shrink-0 mt-1 mr-2.5">
                  <Sparkles size={12} className="text-violet-400" />
                </div>
              )}
              <div
                className={clsx(
                  "max-w-[72%] px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap",
                  msg.role === "user" ? "bubble-user text-white" : "bubble-bot text-slate-100",
                  msg.streaming && !msg.content && "min-w-[60px] min-h-[40px] flex items-center"
                )}
              >
                {msg.role === "bot" && !msg.content && msg.streaming ? (
                  <LoadingDots />
                ) : (
                  <span className={clsx(msg.streaming && "cursor-blink")}>{msg.content}</span>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-6 pb-6 shrink-0">
        <div className="glass rounded-2xl flex items-end gap-3 px-4 py-3 focus-within:border-violet-500/40 focus-within:shadow-[0_0_0_1px_rgba(139,92,246,0.2)] transition-all">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask me anything about you two…"
            rows={1}
            disabled={loading}
            className="flex-1 bg-transparent text-sm text-white placeholder-slate-600 resize-none outline-none max-h-32 leading-relaxed disabled:opacity-50"
            style={{ minHeight: "24px" }}
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className={clsx(
              "shrink-0 p-2 rounded-xl transition-all",
              input.trim() && !loading
                ? "btn-gradient text-white"
                : "bg-white/5 text-slate-600 cursor-not-allowed"
            )}
          >
            <Send size={15} />
          </button>
        </div>
        <p className="text-[11px] text-slate-700 text-center mt-2">Shift+Enter for new line · Enter to send</p>
      </div>
    </div>
  );
}
