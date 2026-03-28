import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MemoryLane — Your Relationship Chatbot",
  description: "Chat about your relationship, get roasted, take quizzes, and relive memories.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <div className="bg-mesh" aria-hidden />
        <div className="relative z-10 h-screen">{children}</div>
      </body>
    </html>
  );
}
