"use client";

import { useRef, useState, useCallback } from "react";
import { Upload, X, FileText, CheckCircle, AlertCircle } from "lucide-react";
import { uploadChat } from "@/lib/api";
import clsx from "clsx";

interface Props {
  onClose: () => void;
  onSuccess: () => void;
}

type State = "idle" | "uploading" | "success" | "error";

export default function UploadModal({ onClose, onSuccess }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<State>("idle");
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState("");
  const [result, setResult] = useState<{ message_count: number; chunk_count: number } | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith(".txt")) {
      setErrorMsg("Please upload a .txt file exported from WhatsApp.");
      setState("error");
      return;
    }
    setFileName(file.name);
    setState("uploading");
    try {
      const data = await uploadChat(file);
      setResult(data);
      setState("success");
      setTimeout(onSuccess, 1800);
    } catch (e: unknown) {
      setErrorMsg(e instanceof Error ? e.message : "Upload failed");
      setState("error");
    }
  }, [onSuccess]);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    /* backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.7)", backdropFilter: "blur(6px)" }}
      onClick={(e) => e.target === e.currentTarget && state !== "uploading" && onClose()}
    >
      <div className="glass rounded-3xl p-8 w-full max-w-md animate-fade-up shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-white">Upload Chat Export</h2>
            <p className="text-xs text-slate-500 mt-1">WhatsApp .txt export file</p>
          </div>
          {state !== "uploading" && (
            <button onClick={onClose} className="p-2 rounded-xl hover:bg-white/10 transition-colors">
              <X size={16} className="text-slate-400" />
            </button>
          )}
        </div>

        {/* Drop zone */}
        {state === "idle" || state === "error" ? (
          <>
            <div
              className={clsx(
                "border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all",
                dragOver ? "drag-over" : "border-white/10 hover:border-violet-500/40 hover:bg-white/[0.02]"
              )}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={onDrop}
              onClick={() => inputRef.current?.click()}
            >
              <Upload size={28} className="mx-auto mb-3 text-violet-400" />
              <p className="text-sm font-medium text-white">Drop your .txt file here</p>
              <p className="text-xs text-slate-500 mt-1.5">or click to browse</p>
              <input ref={inputRef} type="file" accept=".txt" className="hidden" onChange={onInputChange} />
            </div>

            {state === "error" && (
              <div className="mt-4 flex items-center gap-2 text-red-400 bg-red-500/10 rounded-xl px-4 py-3">
                <AlertCircle size={14} />
                <p className="text-xs">{errorMsg}</p>
              </div>
            )}

            <p className="mt-4 text-[11px] text-slate-600 leading-relaxed text-center">
              How to export: WhatsApp → Open chat → ⋮ → More → Export Chat → Without Media
            </p>
          </>
        ) : state === "uploading" ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 mx-auto mb-4 rounded-2xl bg-violet-500/20 flex items-center justify-center">
              <FileText size={20} className="text-violet-400 animate-pulse" />
            </div>
            <p className="text-sm font-medium text-white">{fileName}</p>
            <p className="text-xs text-slate-500 mt-2">Parsing & embedding messages…</p>
            <div className="mt-5 h-1 rounded-full bg-white/5 overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-violet-500 to-pink-500 animate-pulse w-3/4" />
            </div>
            <p className="text-[11px] text-slate-600 mt-3">This may take 2–4 minutes for large chats</p>
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="w-12 h-12 mx-auto mb-4 rounded-2xl bg-emerald-500/20 flex items-center justify-center">
              <CheckCircle size={20} className="text-emerald-400" />
            </div>
            <p className="text-sm font-bold text-white">Upload complete!</p>
            {result && (
              <p className="text-xs text-slate-400 mt-2">
                {result.message_count.toLocaleString()} messages → {result.chunk_count.toLocaleString()} memory chunks
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
