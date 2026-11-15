"use client";

import { useEffect } from "react";

import ChatHeader from "./Header";
import MessageList from "./MessageList";
import ChatInput from "./Input";

import { useChat } from "@/hooks/useChat";

const SUGGESTIONS = [
  "What do you do at Likvido?",
  "How technical are you?",
  "What's your fintech experience?",
  "When are you available?",
];

export default function Chat({ token }: { token: string }) {
  // Drop the token from the address bar / history once it's been read, so it
  // doesn't linger in browser history or get logged in server access logs.
  useEffect(() => {
    if (token && window.location.search.includes("token=")) {
      window.history.replaceState({}, "", window.location.pathname);
    }
  }, [token]);

  const {
    messages,
    input,
    loading,
    usage,
    setInput,
    sendMessage,
  } = useChat(token);

  return (
    <div className="chat-card flex h-dvh w-full max-w-3xl flex-col overflow-hidden sm:h-175 sm:rounded-3xl">
      <ChatHeader usage={usage} />

      <MessageList
        messages={messages}
        suggestions={messages.length === 1 ? SUGGESTIONS : []}
        onPick={(question) => sendMessage(question)}
      />

      <ChatInput
        value={input}
        loading={loading}
        onChange={setInput}
        onSend={sendMessage}
      />

      <p className="chat-note px-6 pb-4 text-center text-xs">
        answers come from my CV. for anything else, message me on LinkedIn.
      </p>
    </div>
  );
}