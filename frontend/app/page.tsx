"use client";

import { useState, useEffect, useCallback } from "react";
import Sidebar, { type Mode } from "@/components/Sidebar";
import Header from "@/components/Header";
import UploadModal from "@/components/UploadModal";
import ChatMode from "@/components/modes/ChatMode";
import RoastMode from "@/components/modes/RoastMode";
import QuizMode from "@/components/modes/QuizMode";
import TimelineMode from "@/components/modes/TimelineMode";
import StoryMode from "@/components/modes/StoryMode";
import AnalyticsMode from "@/components/modes/AnalyticsMode";
import { fetchHealth, deleteAllData } from "@/lib/api";

export default function Home() {
  const [mode, setMode] = useState<Mode>("chat");
  const [user, setUser] = useState("Shivang");
  const [showUpload, setShowUpload] = useState(false);
  const [chatLoaded, setChatLoaded] = useState(false);

  // Check backend on mount
  const checkHealth = useCallback(async () => {
    try {
      const h = await fetchHealth();
      setChatLoaded(h.chat_loaded);
    } catch {
      // backend not reachable yet — silent fail
    }
  }, []);

  useEffect(() => { checkHealth(); }, [checkHealth]);

  const handleUploadSuccess = () => {
    setShowUpload(false);
    setChatLoaded(true);
  };

  const handleDelete = async () => {
    if (!confirm("Delete all stored chat data? This cannot be undone.")) return;
    try {
      await deleteAllData();
      setChatLoaded(false);
      setMode("chat");
    } catch {
      alert("Failed to delete data.");
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar active={mode} onChange={setMode} chatLoaded={chatLoaded} />

      {/* Main area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header
          mode={mode}
          user={user}
          onUserChange={setUser}
          onUploadClick={() => setShowUpload(true)}
          onDeleteClick={handleDelete}
          chatLoaded={chatLoaded}
        />

        {/* Content */}
        <main className="flex-1 overflow-hidden relative">
          {/* Empty state — no chat loaded */}
          {!chatLoaded && mode !== "chat" ? (
            <div className="flex flex-col items-center justify-center h-full gap-5 px-6 animate-fade">
              <div className="text-5xl">🔒</div>
              <div className="text-center">
                <p className="text-base font-semibold text-white">Chat data required</p>
                <p className="text-sm text-slate-500 mt-1">Upload your WhatsApp chat export to unlock this mode</p>
              </div>
              <button
                onClick={() => setShowUpload(true)}
                className="btn-gradient px-6 py-2.5 rounded-xl text-white text-sm font-semibold"
              >
                Upload Chat Export
              </button>
            </div>
          ) : (
            <>
              {mode === "chat"      && <ChatMode user={user} />}
              {mode === "roast"     && <RoastMode />}
              {mode === "quiz"      && <QuizMode />}
              {mode === "timeline"  && <TimelineMode />}
              {mode === "story"     && <StoryMode />}
              {mode === "analytics" && <AnalyticsMode />}
            </>
          )}
        </main>
      </div>

      {/* Upload modal */}
      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onSuccess={handleUploadSuccess}
        />
      )}
    </div>
  );
}
