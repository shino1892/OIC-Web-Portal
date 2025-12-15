"use client";

import { useState, useRef, useEffect } from "react";

type Message = { id: string; role: "user" | "assistant"; text: string };

export default function AiSupportPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastRequestTime, setLastRequestTime] = useState(0);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendPrompt() {
    const prompt = input.trim();
    if (!prompt) return;

    const now = Date.now();
    const timeSinceLastRequest = now - lastRequestTime;
    if (timeSinceLastRequest < 5000) { // 5秒以内の連続リクエストを防ぐ
      alert("リクエストが多すぎます。5秒待ってから再度お試しください。");
      return;
    }

    const userMsg: Message = { id: String(now), role: "user", text: prompt };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);
    setLastRequestTime(now);

    try {
      const res = await fetch("http://localhost:5000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      const data = await res.json();
      if (!res.ok) {
        const err = data?.error || "Unknown error";
        const assistantMsg: Message = { id: String(now + 1), role: "assistant", text: `エラー: ${err}` };
        setMessages((m) => [...m, assistantMsg]);
      } else {
        const assistantText = data.result || data.error || "（返答なし）";
        const assistantMsg: Message = { id: String(now + 1), role: "assistant", text: assistantText };
        setMessages((m) => [...m, assistantMsg]);
      }
    } catch (e) {
      const assistantMsg: Message = { id: String(now), role: "assistant", text: `通信エラー: ${String(e)}` };
      setMessages((m) => [...m, assistantMsg]);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendPrompt();
    }
  }

  return (
    <div style={{ padding: 20, maxWidth: 800, margin: "0 auto" }}>
      <h1>AI Support（チャット）</h1>

      <div style={{ border: "1px solid #ddd", padding: 12, borderRadius: 6, minHeight: 200, maxHeight: 480, overflowY: "auto" }}>
        {messages.length === 0 && <div style={{ color: "#666" }}>ここに会話が表示されます。質問を入力してください。</div>}
        {messages.map((m) => (
          <div key={m.id} style={{ margin: "8px 0", display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
            <div style={{
              background: m.role === "user" ? "#0b93f6" : "#f1f1f1",
              color: m.role === "user" ? "#fff" : "#000",
              padding: "8px 12px",
              borderRadius: 8,
              maxWidth: "80%",
              whiteSpace: "pre-wrap",
            }}>
              {m.text}
            </div>
          </div>
        ))}
        {loading && <div style={{ color: "#666", marginTop: 8 }}>AIが応答中...</div>}
        <div ref={bottomRef} />
      </div>

      <div style={{ marginTop: 12 }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          rows={3}
          style={{ width: "100%", padding: 8, boxSizing: "border-box" }}
          placeholder="ここに質問を入力して、Enterで送信（Shift+Enterで改行）"
        />
        <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
          <button onClick={sendPrompt} disabled={loading || !input.trim()}>
            送信
          </button>
          <button onClick={() => { setMessages([]); setInput(""); }}>
            履歴クリア
          </button>
        </div>
      </div>
    </div>
  );
}